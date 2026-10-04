import os
import sys
import re

def convert_links_to_m3u():
    input_file = "portal.txt"
    output_file = "mac_playlist.m3u"

    # 1. Cek apakah file portal.txt ada
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' tidak ditemukan di repositori!")
        sys.exit(1)

    print(f"1. Membaca daftar link dari {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    m3u_content = "#EXTM3U\n"
    channel_count = 0

    print("2. Menyusun ulang link menjadi format M3U...")
    for line in lines:
        url = line.strip()
        
        # Validasi: Pastikan baris tersebut adalah link (mengandung http atau https)
        if url.startswith("http://") or url.startswith("https://"):
            channel_count += 1
            
            # Mencoba mengekstrak nama channel atau ID dari parameter 'cmd' di dalam URL jika ada
            # Contoh: jika ada &cmd=ffmpeg+http://.../Movie_Name, kita ambil nama belakangnya
            ch_name = f"Channel {channel_count}"
            cmd_match = re.search(r'cmd=([^&]+)', url)
            if cmd_match:
                cmd_value = cmd_match.group(1)
                # Ambil bagian teks terakhir setelah garis miring jika berupa path file video
                name_extract = cmd_value.split("/")[-1].replace("+", " ").replace("%20", " ")
                if name_extract and not name_extract.startswith("http"):
                    ch_name = name_extract

            # Tulis ke format standar M3U
            m3u_content += f'#EXTINF:-1 tvg-id="ch_{channel_count}",{ch_name}\n'
            m3u_content += f'{url}\n'

    # 3. Simpan hasil akhir ke file M3U
    if channel_count > 0:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print(f"✅ Selesai! Berhasil membungkus {channel_count} saluran ke dalam {output_file}.")
    else:
        print("❌ Gagal: Tidak ada baris link URL yang valid ditemukan di portal.txt.")
        sys.exit(1)

if __name__ == "__main__":
    convert_links_to_m3u()
