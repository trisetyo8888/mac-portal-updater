import os
import sys
import re

def create_playlist_from_direct_links():
    input_file = "portal.txt"
    output_file = "mac_playlist.m3u"

    # 1. Pastikan file portal.txt ada di dalam repositori
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' tidak ditemukan di repositori!")
        sys.exit(1)

    print(f"1. Membaca tautan langsung dari {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Memulai kerangka file M3U standar universal
    m3u_content = "#EXTM3U\n"
    channel_count = 0

    print("2. Menyusun playlist M3U untuk aplikasi IPTV...")
    for line in lines:
        url = line.strip()
        
        # Validasi: Hanya memproses baris yang berisi link valid (http atau https)
        if url.startswith("http://") or url.startswith("https://"):
            channel_count += 1
            
            # --- STRATEGI PENAMAAN SALURAN ---
            # Nama default jika tidak ditemukan teks nama di dalam tautan
            ch_name = f"Channel {channel_count}"
            
            # Deteksi Otomatis: Mencoba memotong nama asli dari bagian akhir URL siaran
            # (Misal jika ujung link berupa /hbo.ts, /rcti.m3u8, atau sejenisnya)
            url_clean = url.split("?")[0] # Buang parameter token di belakang tanda tanya jika ada
            name_extract = url_clean.split("/")[-1]
            
            if name_extract and "." in name_extract:
                # Buang ekstensi format video seperti .ts, .m3u8, .mp4, dll.
                name_clean = os.path.splitext(name_extract)[0]
                # Bersihkan spasi dan karakter persen bawaan URL
                name_clean = name_clean.replace("+", " ").replace("%20", " ")
                if name_clean and not name_clean.isdigit():
                    ch_name = name_clean.upper()

            # Tulis ke struktur standar M3U agar bisa dibaca komponen Video Player apa pun
            m3u_content += f'#EXTINF:-1 tvg-id="ch_{channel_count}" group-title="MAC Portal Converter",{ch_name}\n'
            m3u_content += f'{url}\n'

    # 3. Menyimpan hasil akhir ke file ekspor mac_playlist.m3u
    if channel_count > 0:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print(f"✅ SUKSES! Berhasil membungkus {channel_count} saluran ke dalam '{output_file}'.")
    else:
        print(f"❌ Gagal: Tidak ditemukan tautan video yang valid di dalam {input_file}.")
        sys.exit(1)

if __name__ == "__main__":
    create_playlist_from_direct_links()
