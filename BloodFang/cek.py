#!/usr/bin/env python3
import urllib.request
import json
import os
import getpass

# 1. Ambil Key (Otomatis dari file .gemini_key jika ada)
key_file = ".gemini_key"
api_key = None

if os.path.exists(key_file):
    try:
        with open(key_file, "r") as f:
            api_key = f.read().strip()
    except: pass

if not api_key:
    api_key = getpass.getpass("Masukkan API Key Anda: ").strip()

# 2. Tanya ke Google: List Models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

print(f"[*] Menghubungi Google dengan Key: {api_key[:5]}...*****")

try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        
        print("\n[✓] KONEKSI SUKSES! Berikut model yang tersedia untuk Anda:\n")
        print(f"{'NAMA MODEL (Pakai string ini)':<40} {'METODE YG DISUPPORT'}")
        print("-" * 70)
        
        valid_models = []
        for m in data.get('models', []):
            name = m['name'].replace("models/", "")
            methods = m.get('supportedGenerationMethods', [])
            
            # Kita cari model yang support 'generateContent'
            if "generateContent" in methods:
                print(f"{name:<40} {methods}")
                valid_models.append(name)
        
        print("-" * 70)
        print(f"\n[!] REKOMENDASI: Ubah baris GEMINI_MODEL di script utama menjadi salah satu nama di atas.")
        if "gemini-1.5-flash" in valid_models:
            print("    Saran: Gunakan 'gemini-1.5-flash'")
        elif "gemini-pro" in valid_models:
            print("    Saran: Gunakan 'gemini-pro'")

except urllib.error.HTTPError as e:
    print(f"\n[!] HTTP Error {e.code}: {e.read().decode()}")
    print("    -> Kemungkinan API Key salah atau belum diaktifkan di Google AI Studio.")
except Exception as e:
    print(f"\n[!] Error: {e}")
