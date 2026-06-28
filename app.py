import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from PIL import Image
import io

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY tidak ditemukan. Pastikan file .env sudah dikonfigurasi.")
genai.configure(api_key=api_key)
model_vision = genai.GenerativeModel('gemini-3.5-flash') 

# --- TF-IDF ---
print("Sedang memuat model AI...")
tfidf = joblib.load('tfidf_model.pkl')
tfidf_matrix = joblib.load('tfidf_matrix.pkl')
df_data = pd.read_pickle('df_resep.pkl')
print("Model AI siap digunakan!")

@app.route('/cari_resep', methods=['POST'])
def api_cari_resep():
    bahan_kulkas = ""

    print("Files yang masuk:", request.files)
    print("Data Form yang masuk:", request.form)
    
    if 'gambar' in request.files:
        try:
            file_gambar = request.files['gambar']
            img = Image.open(file_gambar.stream)
            
            print("Mendeteksi gambar...")
            prompt = "Identifikasi bahan makanan mentah di gambar ini. Balas HANYA dengan nama bahan-bahannya dalam bahasa Indonesia, pisahkan dengan spasi. Jangan ada koma. Contoh: telur sawi ayam bawang"
            response = model_vision.generate_content([prompt, img])
            bahan_kulkas = response.text.strip()
            print(f"Bahan terdeteksi oleh Mata AI: {bahan_kulkas}")
        except Exception as e:
            return jsonify({"pesan": f"Gagal memproses gambar: {str(e)}", "data": []}), 500
        
    else:
        bahan_kulkas = request.form.get('bahan', '')

    if not bahan_kulkas:
        return jsonify({"pesan": "Bahan kosong!", "data": []}), 400

    vektor_input = tfidf.transform([bahan_kulkas.lower()])
    skor_kemiripan = cosine_similarity(vektor_input, tfidf_matrix)
    urutan_cocok = skor_kemiripan[0].argsort()[::-1]
    
    hasil_resep = []
    ditemukan = 0
    
    # Persiapkan list kata dari input user untuk dicocokkan
    bahan_kulkas_list = bahan_kulkas.lower().split()
    jumlah_input = len(bahan_kulkas_list)
    
    # Tentukan syarat minimal bahan yang harus ada di resep
    if jumlah_input <= 2:
        syarat_minimal = 1
    elif jumlah_input <= 4:
        syarat_minimal = 2
    else:
        syarat_minimal = 3 # Meskipun bahannya ada banyak sekali (misal 6+ dari foto), cukup 3 kata saja yang cocok agar tetap memunculkan hasil resep
    
    # Ambil top 200 hasil teratas saja untuk mempercepat proses (menghindari bottleneck)
    top_k_indices = urutan_cocok[:200]
    
    for i in top_k_indices:
        skor = skor_kemiripan[0][i]
        
        # Kita turunkan sedikit batas skor TF-IDF karena kita akan menggunakan filter yang lebih ketat
        if skor > 0.05: 
            judul = df_data['Title'].iloc[i]
            bahan_asli = df_data['Ingredients'].iloc[i]
            cara_masak = df_data['Steps'].iloc[i]
            
            # --- LOGIKA FILTER BARU ---
            bahan_asli_lower = str(bahan_asli).lower()
            bahan_cocok = [bahan for bahan in bahan_kulkas_list if bahan in bahan_asli_lower]
            
            # Hanya lanjutkan jika jumlah kata yang cocok memenuhi syarat minimal
            if len(bahan_cocok) >= syarat_minimal:
                daftar_bahan = [b.strip() for b in str(bahan_asli).split('--') if b.strip()]
                daftar_langkah = [l.strip() for l in str(cara_masak).split('--') if l.strip()]
                
                hasil_resep.append({
                    "judul": judul.title(),
                    "skor_cocok": round(float(skor) * 100, 2),
                    "bahan": daftar_bahan,
                    "langkah": daftar_langkah
                })
                ditemukan += 1
            
        if ditemukan == 10:
            break
            
    return jsonify({
        "bahan_input": bahan_kulkas,
        "total_ditemukan": ditemukan,
        "rekomendasi": hasil_resep
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)