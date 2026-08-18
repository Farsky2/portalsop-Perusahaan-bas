import os
import fitz  # PyMuPDF
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Izinkan akses dari mana saja
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Struktur data untuk menyimpan isi SOP
data_sop = []

# Membaca PDF saat server pertama kali jalan
def load_pdfs():
    global data_sop
    folder = "dokumen_sop"
    if not os.path.exists(folder): return
    
    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            doc = fitz.open(os.path.join(folder, filename))
            for i in range(len(doc)):
                text = doc.load_page(i).get_text("text")
                data_sop.append({
                    "judul_dokumen": filename,
                    "nomor_halaman": i + 1,
                    "isi_teks": text
                })
    print(f"Berhasil memuat {len(data_sop)} halaman SOP.")

load_pdfs()

@app.get("/search")
def search(q: str):
    q = q.lower()
    # Pencarian sederhana: cari kata kunci di dalam teks
    results = [d for d in data_sop if q in d["isi_teks"].lower()]
    
    # Ambil 10 hasil teratas
    return {"hits": results[:10]}