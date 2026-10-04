import json
import os
import sys

def convert_txt_to_m3u():
    input_file = "portal.txt"
    output_file = "mac_playlist.m3u"
    portal_host = "http://babo01.com"
    mac_address = "00:1A:79:1f:0e:30"

    # 1. Cek apakah file portal.txt ada di repositori
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' tidak ditemukan di repositori!")
        sys.exit(1)

    print(f"1. Membaca data dari {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        raw_data = f.read().strip()

    if not raw_data:
        print("❌ Error: File portal.txt kosong!")
        sys.exit(1)

    m3u_content = "#EXTM3U\n"
    channel_count = 0

    print("2. Memproses dan mengonversi data ke format M3U...")
    try:
        # Mencoba membaca data sebagai JSON (format bawaan get_ordered_list Stalker)
        data_json = json.loads(raw_data)
        
        # Ekstrak daftar channel dari struktur JSON Stalker Portal
        # (Mengantisipasi jika JSON dibungkus di dalam key 'js' -> 'data')
        channels = data_json.get("js", {}).get("data", []) if isinstance(data_json.get("js"), dict) else data_json.get("data", [])
        if not channels and isinstance(data_json, list):
            channels = data_json
        elif not channels and isinstance(data_json, dict):
            channels = data_json.get("js", []) if isinstance(data_json.get("js"), list) else []

        if channels:
            for ch in channels:
                if isinstance(ch, dict):
                    ch_name = ch.get("name", "Unknown Channel")
                    ch_id = ch.get("id", "")
                    cmd = ch.get("cmd", "")
                    
                    if cmd.startswith("ffmpeg "):
                        cmd = cmd.replace("ffmpeg ", "", 1)
                        
                    stream_url = f"{portal_host}/portal.php?type=itv&action=create_link&cmd={cmd}&mac={mac_address}"
                    
                    m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}",{ch_name}\n'
                    m3u_content += f'{stream_url}\n'
                    channel_count += 1
        else:
            # JALUR FALLBACK: Jika portal.txt bukan JSON, melainkan teks berisi daftar cmd/nama baris per baris
            lines = raw_data.split("\n")
            for line in lines:
                if line.strip():
                    # Contoh jika format teks biasa, sesuaikan logika pemisahnya di sini jika perlu
                    m3u_content += f'#EXTINF:-1,Channel {channel_count + 1}\n'
                    m3u_content += f'{portal_host}/portal.php?type=itv&action=create_link&cmd={line.strip()}&mac={mac_address}\n'
                    channel_count += 1

    except json.JSONDecodeError:
        # Jika bukan JSON, langsung proses sebagai teks baris per baris
        print("   [Log] Format bukan JSON, memproses sebagai teks baris per baris...")
        lines = raw_data.split("\n")
        for line in lines:
            if line.strip():
                cmd = line.strip()
                if "portal.php" in cmd:
                    # Jika teks di portal.txt sudah berupa link utuh
                    m3u_content += f'#EXTINF:-1,Channel {channel_count + 1}\n'
                    m3u_content += f'{cmd}\n'
                else:
                    # Jika teks di portal.txt hanya baris command (cmd) siaran
                    stream_url = f"{portal_host}/portal.php?type=itv&action=create_link&cmd={cmd}&mac={mac_address}"
                    m3u_content += f'#EXTINF:-1,Channel {channel_count + 1}\n'
                    m3u_content += f'{stream_url}\n'
                channel_count += 1

    # 3. Simpan hasil akhir ke file M3U
    if channel_count > 0:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print(f"✅ Selesai! Berhasil mengonversi {channel_count} saluran ke {output_file}.")
    else:
        print("❌ Gagal: Tidak ada saluran yang berhasil diekstrak dari portal.txt.")
        sys.exit(1)

if __name__ == "__main__":
    convert_txt_to_m3u()
