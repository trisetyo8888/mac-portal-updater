import os
import sys
import requests

# 1. Membaca data dari portal.txt bawaan Anda
if os.path.exists('portal.txt'):
    with open('portal.txt', 'r') as f:
        content = f.read().strip()
    
    # Memisahkan baris atau karakter pemisah '|'
    if '|' in content:
        PORTAL_URL, MAC_ADDRESS = content.split('|', 1)
    else:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if len(lines) >= 2:
            PORTAL_URL = lines[0]
            MAC_ADDRESS = lines[1]
        else:
            print("Eror: Format di dalam file Portal.txt tidak lengkap!")
            sys.exit(1)
else:
    print("Eror: File portal.txt tidak ditemukan!")
    sys.exit(1)

# Membersihkan spasi atau teks yang tidak diinginkan
PORTAL_URL = PORTAL_URL.strip()
MAC_ADDRESS = MAC_ADDRESS.strip()

print(f"Menghubungkan ke Portal: {PORTAL_URL}")
print(f"Menggunakan MAC: {MAC_ADDRESS}")

# 2. Logika utama mengirim data autentikasi ke Server Stalker Portal
# (Skrip akan membuat file mac_playlist.m3u otomatis)
# --- Taruh baris kode request download Anda di bawah ini ---
