import os
import sys
import requests
import re
import json
import urllib.parse

m3u_content = "#EXTM3U\n"
total_all_channels = 0

target_file = ""
for filename in os.listdir('.'):
    if filename.lower() == 'portal.txt':
        target_file = filename
        break

if not target_file or not os.path.exists(target_file):
    print("Error: File Portal.txt tidak ditemukan!")
    sys.exit(1)

with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = [line.strip() for line in f if line if line.strip()]

master_m3u_content = "#EXTM3U\n"

for index, account in enumerate(lines, start=1):
    if '|' not in account:
        continue
        
    PORTAL_URL, MAC_ADDRESS = account.split('|', 1)
    PORTAL_URL = PORTAL_URL.strip()
    MAC_ADDRESS = MAC_ADDRESS.strip()
    
    print(f"\n[{index}/{len(lines)}] Memproses: {PORTAL_URL}")
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
    
    try:
        # Handshake Token
        handshake_url = f"{api_url}?type=stb&action=handshake&token="
        response = requests.get(handshake_url, headers=headers, timeout=12)
        play_token = ""
        if response.status_code == 200:
            try:
                play_token = response.json().get('js', {}).get('token', '')
                if play_token:
                    headers['Authorization'] = f"Bearer {play_token}"
            except:
                pass

        # Tarik siaran
        channels_url = f"{api_url}?type=itv&action=get_all_channels"
        res = requests.get(channels_url, headers=headers, timeout=15)
        raw_text = res.text
        
        matches = re.findall(r'"name"\s*:\s*"([^"]+)"[^}]+?"cmd"\s*:\s*"([^"]+)"', raw_text)
        
        if matches:
            for name, cmd in matches:
                name_str = name.strip()
                cmd_str = cmd.replace('\\', '')
                
                # PERBAIKAN LOGIKA LINK TERPOTONG (Bypass localhost)
                if "http" in cmd_str and "localhost" not in cmd_str:
                    stream_url = cmd_str
                else:
                    # Ambil nomor ID channel yang ada di ujung, misalnya dari 'ch/108525_' diambil '108525_'
                    clean_cmd = cmd_str.split('/')[-1] if '/' in cmd_str else cmd_str
                    clean_cmd = clean_cmd.replace('ffmpeg', '').replace('ffrt', '').strip()
                    
                    # Hubungkan paksa ke domain utama eksternal safetv/mag7070 menggantikan localhost
                    stream_url = f"{base_url}/play/live.php?mac={MAC_ADDRESS}&stream={clean_cmd}&extension=ts&play_token={play_token}"
                
                if any(k in name_str.lower() for k in ["dazn", "ucl", "champions"]):
                    logo_url = "http://tivi-ott.net"
                    ch_group = "LIVE | UCL"
                else:
                    clean_name_encoded = urllib.parse.quote(name_str.lower())
                    logo_url = f"https://github.io{clean_name_encoded}.png"
                    ch_group = f"Portal_{index}"
                
                item_text = f'#EXTINF:-1 tvg-id="{name_str}" tvg-name="{name_str}" tvg-logo="{logo_url}" group-title="{ch_group}", {name_str}\n{stream_url}\n'
                current_m3u_content += item_text
                master_m3u_content += item_text
                count += 1
                
        print(f"-> Sukses mengekstrak {count} channel.")
        total_all_channels += count

    except Exception as e:
        print(f"-> Gagal memproses portal: {e}")
        continue
        
    output_filename = f"playlist_{index}.m3u"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(current_m3u_content)

with open('mac_playlist.m3u', 'w', encoding='utf-8') as f:
    f.write(master_m3u_content)
