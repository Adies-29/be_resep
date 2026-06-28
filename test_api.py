import requests

# Mengirim paket sisa bahan ke loket server lokalmu
url = 'http://127.0.0.1:5000/cari_resep'
paket_data = {"bahan": "kerupuk telur sosis"}

print("Mengirim data ke server...")
jawaban = requests.post(url, json=paket_data)

# Mencetak balasan dari server AI
import json
print(json.dumps(jawaban.json(), indent=2))