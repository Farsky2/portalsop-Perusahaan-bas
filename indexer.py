import os
import re
import fitz  # PyMuPDF
import meilisearch

# Koneksi ke database Meilisearch lokal
client = meilisearch.Client('http://127.0.0.1:7700')
index = client.index('sop_docs')

pdf_folder = "dokumen_sop"
dokumen_siap_indeks = []

print("Memulai pembacaan PDF...")
for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        filepath = os.path.join(pdf_folder, filename)
        doc = fitz.open(filepath)
        print(f"-> Membaca: {filename} (Total {len(doc)} halaman)")
        
        for page_num in range(len(doc)):
            teks_halaman = doc.load_page(page_num).get_text("text")
            
            if teks_halaman.strip():
                base_name = filename.replace('.pdf', '')
                clean_id = re.sub(r'[^a-zA-Z0-9_-]', '_', base_name)
                
                dokumen_siap_indeks.append({
                    "id": f"{clean_id}_hal_{page_num+1}",
                    "judul_dokumen": filename,
                    "nomor_halaman": page_num + 1,
                    "isi_teks": teks_halaman,
                    "file_path": f"dokumen_sop/{filename}"
                })

print(f"\nTotal halaman berteks yang terkumpul: {len(dokumen_siap_indeks)}")

if len(dokumen_siap_indeks) > 0:
    print("Mengirim data ke Meilisearch...")
    try:
        index.delete_all_documents()
    except:
        pass
    
    task_docs = index.add_documents(dokumen_siap_indeks)
    print("Menunggu database memproses data...")
    client.wait_for_task(task_docs.task_uid)
    print("Selesai! Data berhasil masuk ke database.")
else:
    print("GAGAL: Tidak ada teks yang berhasil dibaca!")