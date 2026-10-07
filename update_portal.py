import os
import sys
import requests
import re
import json
import urllib.parse

m3u_content = "#EXTM3U\n"
total_all_channels = 0

# 1. Pencarian otomatis file konfigurasi Portal.txt
target_file = ""
for filename in os.listdir('.'):
    if filename.lower() == 'portal.txt':
        target_file = filename
        break

if not target_file or not os.path.exists(target_file):
    print("Error: File Portal.txt tidak ditemukan di repositori!")
    sys.exit(1)

with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = [line.strip() for line in f if line.strip()]

if not lines:
    print("Error: File Portal.txt kosong!")
    sys.exit(1)

print(f"Membaca {len(lines)} akun MAC Portal dari file...")

master_m3u_content = "#EXTM3U\n"

# 2. Proses iterasi perulangan akun portal (Mendukung Multi-Portal)
for index, account in enumerate(lines, start=1):
    if '|' not in account:
        print(f"Baris {index} dilewati: Tidak ada pemisah '|'")
        continue
        
    PORTAL_URL, MAC_ADDRESS = account.split('|', 1)
    PORTAL_URL = PORTAL_URL.strip()
    MAC_ADDRESS = MAC_ADDRESS.strip()
    
    print(f"\n[{index}/{len(lines)}] Memproses Portal: {PORTAL_URL}")
    current_m3u_content = "#EXTM3U\n"
    
    # PERBAIKAN REVISI URL SANGAT AMAN (Menjamin output berupa teks String murni)
    clean_portal = PORTAL_URL
    if '/c/' in clean_portal:
        base_url = clean_portal.split('/c/')[0]
    else:
        base_url = clean_portal.rstrip('/')
        
    api_url = f"{base_url}/server/load.php"
    print(f"-> Alamat API yang berhasil dirakit: {api_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbid/000000000000000000000000000000000000',
        'Cookie': f'mac={MAC_ADDRESS}; stb_lang=en; timezone=Europe%2FParis;',
        'Referer': f"{base_url}/c/",
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    
    count = 0
    try:
        # Langkah A: Mengambil token login lokal (Handshake Session ID)
        handshake_url = f"{api_url}?type=stb&action=handshake&token="
        response = requests.get(handshake_url, headers=headers, timeout=12)
        play_token = ""
        if response.status_code == 200:
            try:
                play_token = response.json().get('js', {}).get('token', '')
                if play_token:
                    headers['Authorization'] = f"Bearer {play_token}"
                    print("-> Jabat tangan server berhasil! Token aktif didapatkan.")
            except:
                pass

        # Langkah B: Menarik data siaran TV asli dari server
        channels_url = f"{api_url}?type=itv&action=get_all_channels"
        res = requests.get(channels_url, headers=headers, timeout=15)
        raw_text = res.text
        
        # Langkah C: Mengekstrak channel menggunakan pola ekspresi reguler universal
        matches = re.findall(r'"name"\s*:\s*"([^"]+)"[^}]+?"cmd"\s*:\s*"([^"]+)"', raw_text)
        
        if matches:
            for name, cmd in matches:
                name_str = name.strip()
                stream_url = cmd.replace('\\', '')
                
                # PERBAIKAN BYPASS TAUTAN TERPOTONG (Mengalihkan localhost ke alamat IP server asli)
                if "http" in stream_url and "localhost" not in stream_url:
                    # Jika link dari server sudah berbentuk tautan penuh luar
                    if "play_token" not in stream_url:
                        stream_url = f"{stream_url}&play_token={play_token}"
                else:
                    # Menguraikan potongan string ujung dari localhost/ch/xxxxx_ menjadi data stream murni
                    clean_cmd = stream_url.split('/')[-1] if '/' in stream_url else stream_url
                    clean_cmd = clean_cmd.replace('ffmpeg', '').replace('ffrt', '').strip()
                    stream_url = f"{base_url}/play/live.php?mac={MAC_ADDRESS}&stream={clean_cmd}&extension=ts&play_token={play_token}"
                
                # PERBAIKAN LOGO: Menyematkan ikon resmi UEFA Champions League .png secara permanen
                if any(keyword in name_str.lower() for keyword in ["dazn", "ucl", "champions"]):
                    logo_url = "http://tivi-ott.net"
                    ch_group = "LIVE | UCL"
                else:
                    # Menggunakan repositori gambar global untuk channel umum non-olahraga
                    logo_url = f"https://github.io{urllib.parse.quote(name_str.lower())}.png"
                    ch_group = f"Portal_{index}"
                
                item_text = f'#EXTINF:-1 tvg-id="{name_str}" tvg-name="{name_str}" tvg-logo="{logo_url}" group-title="{ch_group}", {name_str}\n{stream_url}\n'
                current_m3u_content += item_text
                master_m3u_content += item_text
                count += 1
                
        print(f"-> Sukses mengekstrak {count} channel dari portal ini.")
        total_all_channels += count

    except Exception as e:
        print(f"-> Gangguan teknis saat membaca data portal: {e}")
        continue
        
    output_filename = f"playlist_{index}.m3u"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(current_m3u_content)
    print(f"-> Berkas [{output_filename}] sukses diperbarui.")

# 3. Menulis berkas master gabungan wajib
with open('mac_playlist.m3u', 'w', encoding='utf-8') as f:
    f.write(master_m3u_content)

print(f"\nSelesai! Total keseluruhan: {total_all_channels} channel berhasil dikumpulkan.")
