import os
import sys
import requests
import re
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
    lines = [line.strip() for line in f if line.strip()]

print(f"Membaca {len(lines)} akun MAC Portal dari file...")

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
        base_url = PORTAL_URL.split('/c/')
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
        # Menarik data channel secara langsung tanpa handshake token dinamis Amerika
        channels_url = f"{api_url}?type=itv&action=get_all_channels"
        res = requests.get(channels_url, headers=headers, timeout=15)
        raw_text = res.text
        
        count = 0
        matches = re.findall(r'"name"\s*:\s*"([^"]+)"[^}]+?"cmd"\s*:\s*"([^"]+)"', raw_text)
        
        if matches:
            for name, cmd in matches:
                name_str = name.strip()
                stream_url = cmd.replace('\\', '')
                
                # Pemotongan link murni bebas proteksi Geo-Block Token
                link_match = re.search(r'(http[s]?://\S+)', stream_url)
                if link_match:
                    stream_base = link_match.group(1).replace('"', '').replace("'", "")
                    stream_url = stream_base
                else:
                    clean_cmd = stream_url.split('/')[-1] if '/' in stream_url else stream_url
                    clean_cmd = clean_cmd.replace('ffmpeg', '').replace('ffrt', '').strip()
                    # Merakit link langsung ke stream PHP server
                    stream_url = f"{base_url}/play/live.php?mac={MAC_ADDRESS}&stream={clean_cmd}&extension=ts"
                
                # Pasang Logo Champions League sesuai gambar permintaan
                if any(k in name_str.lower() for k in ["dazn", "ucl", "champions"]):
                    logo_url = "http://tivi-ott.net"
                    ch_group = "LIVE | UCL"
                else:
                    logo_url = f"https://github.io{urllib.parse.quote(name_str.lower())}.png"
                    ch_group = f"Portal_{index}"
                
                item_text = f'#EXTINF:-1 tvg-id="{name_str}" tvg-name="{name_str}" tvg-logo="{logo_url}" group-title="{ch_group}", {name_str}\n{stream_url}\n'
                current_m3u_content += item_text
                master_m3u_content += item_text
                count += 1
                
        print(f"-> Sukses mengekstrak {count} channel.")

    except Exception as e:
        print(f"-> Gagal memproses portal: {e}")
        continue
        
    output_filename = f"playlist_{index}.m3u"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(current_m3u_content)

with open('mac_playlist.m3u', 'w', encoding='utf-8') as f:
    f.write(master_m3u_content)
