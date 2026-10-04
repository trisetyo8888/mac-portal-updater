import os
import sys
import re

def convert_links_to_universal_m3u():
    input_file = "portal.txt"
    output_file = "mac_playlist.m3u"

    # 1. Validasi keberadaan file portal.txt
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' tidak ditemukan di repositori!")
        sys.exit(1)

    print(f"1. Membaca daftar tautan dari {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    m3u_content = "#EXTM3U\n"
    channel_count = 0

    print("2. Menyusun ulang tautan menjadi format M3U Universal...")
    for line in lines:
        url = line.strip()
        
        # Pastikan baris tersebut adalah link HTTP/HTTPS valid
        if url.startswith("http://") or url.startswith("https://"):
            channel_count += 1
            
            # Pengaturan Nama Saluran Default
            ch_name = f"Channel {channel_count}"
            
            # EKSTRAKSI OTOMATIS: Mencoba mencari nama siaran asli dari parameter 'cmd' di dalam link Anda
            cmd_match = re.search(r'cmd=([^&]+)', url)
            if cmd_match:
                cmd_value = cmd_match.group(1)
                # Ambil nama file/kata paling belakang setelah garis miring terakhir
                name_extract = cmd_value.split("/")[-1].replace("+", " ").replace("%20", " ")
                if name_extract and not name_extract.startswith("http"):
                    ch_name = name_extract

            # Bungkus ke format standar M3U agar dikenali semua Video Player
            m3u_content += f'#EXTINF:-1 tvg-id="ch_{channel_count}",{ch_name}\n'
            m3u_content += f'{url}\n'

    # 3. Ekspor hasil akhir ke mac_playlist.m3u
    if channel_count > 0:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print(f"✅ Selesai! Berhasil mengonversi {channel_count} saluran ke dalam {output_file}.")
    else:
        print("❌ Gagal: Tidak ditemukan link URL yang valid di dalam file portal.txt.")
        sys.exit(1)

if __name__ == "__main__":
    convert_links_to_universal_m3u()
