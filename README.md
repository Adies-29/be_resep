# AI Resep - Backend API 🍳🤖

Backend API untuk aplikasi Rekomendasi Resep Masakan. Aplikasi ini memanfaatkan **Generative AI (Google Gemini)** untuk mengidentifikasi bahan makanan dari gambar, serta menggunakan pemodelan **TF-IDF & Cosine Similarity** untuk mencari resep masakan yang paling relevan berdasarkan bahan-bahan tersebut.

## Fitur Utama
1. **Identifikasi Gambar (Image-to-Text)**: Mendeteksi bahan mentah dari unggahan foto kulkas/bahan makanan (menggunakan `gemini-3.5-flash`).
2. **Sistem Rekomendasi Resep**: Mencari resep paling relevan berdasarkan input teks bahan makanan atau hasil deteksi gambar (menggunakan Machine Learning - TF-IDF).
3. **Optimasi Filter**: Menerapkan penyaringan (*filtering*) berlapis agar resep yang muncul benar-benar relevan dengan syarat minimal bahan yang harus ada.

## Teknologi yang Digunakan
- **Python 3.10**
- **Flask**: Framework backend untuk membuat REST API.
- **Google Generative AI (Gemini)**: Model AI untuk *Computer Vision*.
- **Scikit-Learn & Pandas**: Pemrosesan Machine Learning (TF-IDF & Cosine Similarity).
- **Gunicorn**: WSGI HTTP Server untuk *production* (Deployment).

## Struktur Dataset & Model
Aplikasi membutuhkan file model berikut di direktori root agar dapat berjalan:
- `df_resep.pkl`: Dataset Pandas yang berisi data resep (Judul, Bahan, Cara Masak).
- `tfidf_model.pkl`: Model TF-IDF yang sudah di-*training*.
- `tfidf_matrix.pkl`: Matriks hasil vektorisasi resep untuk pencarian kemiripan.

---

## 🛠️ Cara Menjalankan di Komputer Lokal (Development)

### 1. Prasyarat
Pastikan Python versi 3 (direkomendasikan 3.10+) sudah terinstal di komputermu.

### 2. Instalasi Dependensi
Buka terminal dan instal semua *package* yang dibutuhkan (sangat disarankan di dalam virtual environment):
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment Variables
Buat file bernama `.env` di folder utama (sejajar dengan `app.py`) dan tambahkan API Key Gemini milikmu:
```env
GEMINI_API_KEY="masukkan_api_key_gemini_kamu_di_sini"
```
*(Catatan: Dapatkan API Key secara gratis melalui [Google AI Studio](https://aistudio.google.com/app/apikey)).*

### 4. Menjalankan Server
Jalankan Flask server:
```bash
python app.py
```
Server akan berjalan di `http://localhost:5000`.

---

## 🚀 Dokumentasi API

### 1. Cari Resep
Mencari resep berdasarkan foto bahan makanan atau teks tulisan tangan.

- **URL:** `/cari_resep`
- **Method:** `POST`
- **Tipe Konten:** `multipart/form-data`

#### Parameter Request
Kirimkan *salah satu* dari parameter form data berikut:
| Nama Parameter | Tipe | Deskripsi |
| :--- | :--- | :--- |
| `gambar` | File (Image) | File foto bahan makanan yang akan dideteksi oleh AI (Prioritas). |
| `bahan` | Text (String) | Teks nama-nama bahan makanan, dipisah dengan spasi (Contoh: "telur ayam tomat"). |

#### Contoh Response Berhasil (200 OK)
```json
{
    "bahan_input": "telur ayam tomat",
    "total_ditemukan": 3,
    "rekomendasi": [
        {
            "judul": "Telur Dadar Tomat",
            "skor_cocok": 85.50,
            "bahan": ["2 butir telur", "1 buah tomat, potong dadu", "Garam dan merica secukupnya"],
            "langkah": ["Kocok telur", "Campurkan tomat", "Goreng hingga matang"]
        }
    ]
}
```

#### Contoh Response Gagal (400 Bad Request / 500 Error)
```json
{
    "pesan": "Bahan kosong!",
    "data": []
}
```

---

## 🌐 Panduan Deployment ke Render

Aplikasi ini sudah dikonfigurasi untuk siap di-*deploy* ke [Render](https://render.com/).
1. Hubungkan *repository* GitHub ini ke **Web Service** baru di Render.
2. Render akan membaca file `render.yaml` untuk mengonfigurasi perintah Build dan Start (`gunicorn`) secara otomatis.
3. **PENTING (Environment Variables):** Buka menu **Environment** pada dashboard layanan Rendermu, dan tambahkan secara manual variabel berikut:
   - Key: `GEMINI_API_KEY`
   - Value: *(API Key kamu)*

*(File `.env` sudah masuk ke `.gitignore` sehingga API Key milikmu tidak ikut ter-upload secara publik ke GitHub demi keamanan).*
