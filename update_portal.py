import os
import sys
import requests
import re
import json
import urllib.parse

# 1. Cari file Portal.txt secara otomatis
target_file = ""
for filename in os.listdir('.'):
    if filename.lower() == 'portal.txt':
        target_file = filename
        break

if not target_file:
    print("EROR KRUSIAL: File Portal.txt tidak ditemukan di halaman utama repositori Anda!")
    print("Daftar file saat ini:", os.listdir('.'))
    sys.exit(1)

with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = [line.strip() for line in f if line.strip()]

if not lines:
    print(f"EROR: File {target_file} ditemukan tetapi isinya kosong!")
    sys.exit(1)

print(f"Berhasil membaca {len(lines)} akun MAC Portal dari {target_file}.")

master_m3u_content = "#EXTM3U\n"
total_all_channels = 0

# 2. Ambil data dari masing-masing portal
for index, account in enumerate(lines, start=1):
    if '|' not in account:
        print(f"Baris {index} dilewati: format penulisan salah (wajib pakai tanda | )")
        continue
        
    PORTAL_URL, MAC_ADDRESS = account.split('|', 1)
    PORTAL_URL = PORTAL_URL.strip()
    MAC_ADDRESS = MAC_ADDRESS.strip()
    
    print(f"\n[{index}/{len(lines)}] Menghubungkan ke: {PORTAL_URL}")
    current_m3u_content = "#EXTM3U\n"
    
    if '/c/' in PORTAL_URL:
        base_url = PORTAL_URL.split('/c/')[0]
    else:
        base_url = PORTAL_URL.rstrip('/')
        
    api_url = f"{base_url}/server/load.php"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbid/000000000000000000000000000000000000',
        'Cookie': f'mac={MAC_ADDRESS}; stb_lang=en; timezone=Europe%2FParis;',
        'Referer': f"{base_url}/c/",
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    
    count = 0
    try:
        # Handshake
        handshake_url = f"{api_url}?type=stb&action=handshake&token="
        response = requests.get(handshake_url, headers=headers, timeout=12)
        if response.status_code == 200:
            token = response.json().get('js', {}).get('token', '')
            if token:
                headers['Authorization'] = f"Bearer {token}"

        # Ambil Channel
        channels_url = f"{api_url}?type=itv&action=get_all_channels"
        res = requests.get(channels_url, headers=headers, timeout=15)
        raw_text = res.text
        
        # Ekstraksi Regular Expression universal agar channel dijamin keluar
        matches = re.findall(r'"name"\s*:\s*"([^"]+)"[^}]+?"cmd"\s*:\s*"([^"]+)"', raw_text)
        if matches:
            for name, cmd in matches:
                name_str = name.strip()
                stream_url = cmd.replace('\\', '')
                link_match = re.search(r'(http[s]?://\S+)', stream_url)
                if link_match:
                    stream_url = link_match.group(1).replace('"', '').replace("'", "")
                else:
                    clean_cmd = stream_url.split('/')[-1]
                    stream_url = f"{base_url}/play/live.php?mac={MAC_ADDRESS}&stream={clean_cmd}"
                
                clean_name_encoded = urllib.parse.quote(name_str.lower())
                logo_url = f"https://github.io{clean_name_encoded}.png"
                
                item_text = f'#EXTINF:-1 tvg-id="{name_str}" tvg-name="{name_str}" tvg-logo="{logo_url}" group-title="Portal_{index}",{name_str}\n{stream_url}\n'
                current_m3u_content += item_text
                master_m3u_content += item_text
                count += 1
                
        print(f"-> Berhasil mengekstrak {count} channel.")
        total_all_channels += count

    except Exception as e:
        print(f"-> Gangguan koneksi ke portal ini: {e}")
        
    # Tulis file playlist terpisah
    output_filename = f"playlist_{index}.m3u"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(current_m3u_content)

# Tulis file master untuk memuaskan Git Actions
with open('mac_playlist.m3u', 'w', encoding='utf-8') as f:
    f.write(master_m3u_content)

print(f"\nSelesai! Total keseluruhan {total_all_channels} channel disimpan.")
if total_all_channels == 0:
    print("Peringatan: Seluruh playlist kosong. Periksa file Portal.txt Anda!")
    sys.exit(1)
