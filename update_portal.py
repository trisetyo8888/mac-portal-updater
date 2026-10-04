import os
import sys
import requests
import re
import json

# 1. Membaca data dari Portal.txt
if os.path.exists('Portal.txt'):
    with open('Portal.txt', 'r') as f:
        content = f.read().strip()
    
    if '|' in content:
        PORTAL_URL, MAC_ADDRESS = content.split('|', 1)
    else:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if len(lines) >= 2:
            PORTAL_URL = lines[0]
            MAC_ADDRESS = lines[1]
        else:
            print("Error: Format di dalam file Portal.txt tidak lengkap!")
            sys.exit(1)
else:
    print("Error: File Portal.txt tidak ditemukan!")
    sys.exit(1)

PORTAL_URL = PORTAL_URL.strip()
MAC_ADDRESS = MAC_ADDRESS.strip()

# Bersihkan URL dan arahkan ke API server
base_url = PORTAL_URL.split('/c/')[0]
api_url = f"{base_url}/server/load.php"

print(f"Menghubungkan ke API Portal: {api_url}")
print(f"Menggunakan MAC: {MAC_ADDRESS}")

headers = {
    'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbid/000000000000000000000000000000000000',
    'Cookie': f'mac={MAC_ADDRESS}; stb_lang=en; timezone=Europe%2FParis;',
    'Referer': f"{base_url}/c/",
    'Accept': '*/*',
    'Connection': 'keep-alive'
}

try:
    # Langkah A: Handshake Token
    handshake_url = f"{api_url}?type=stb&action=handshake&token="
    response = requests.get(handshake_url, headers=headers, timeout=15)
    if response.status_code == 200:
        try:
            json_data = response.json()
            token = json_data.get('js', {}).get('token', '')
            if token:
                headers['Authorization'] = f"Bearer {token}"
                print("Autentikasi Berhasil! Token diperoleh.")
        except:
            pass

    # Langkah B: Ambil data menggunakan metode paksa (Mendukung All Channels & Categories)
    print("Mencoba menarik seluruh data siaran...")
    channels_url = f"{api_url}?type=itv&action=get_all_channels"
    res = requests.get(channels_url, headers=headers, timeout=20)
    
    # Simpan response text mentah untuk di-analisis secara mendalam
    raw_text = res.text
    
    m3u_content = "#EXTM3U\n"
    count = 0

    # Pengecekan 1: Menggunakan Regular Expression langsung ke text mentah (Paling Ampuh)
    # Mencari pola nama dan perintah streaming dari server IPTV Stalker
    matches = re.findall(r'"name"\s*:\s*"([^"]+)"[^}]+?"cmd"\s*:\s*"([^"]+)"', raw_text)
    
    if matches:
        for name, cmd in matches:
            # Bersihkan tautan streaming dari karakter backslash escape
            stream_url = cmd.replace('\\', '')
            
            # Cari link http/https asli di dalam cmd
            link_match = re.search(r'(http[s]?://\S+)', stream_url)
            if link_match:
                stream_url = link_match.group(1).split('"')[0].split("'")[0]
            else:
                # Jika berbentuk perintah internal portal, ubah ke format direct streaming port
                if "localhost" in stream_url or "/" in stream_url:
                    clean_cmd = stream_url.split('/')[-1]
                    stream_url = f"{base_url}/play/live.php?mac={MAC_ADDRESS}&stream={clean_cmd}"
            
            m3u_content += f'#EXTINF:-1 group-title="IPTV TV",{name}\n{stream_url}\n'
            count += 1

    # Pengecekan 2: Jika regex gagal, bongkar menggunakan JSON standard secara fleksibel
    if count == 0:
        try:
            data = json.loads(raw_text)
            items = data.get('js', [])
            if isinstance(items, dict):
                items = list(items.values())
            
            for item in items:
                if isinstance(item, dict):
                    name = item.get('name', 'IPTV Channel')
                    cmd = item.get('cmd', '')
                    if cmd:
                        stream_url = cmd.replace('\\', '')
                        m3u_content += f'#EXTINF:-1 group-title="IPTV TV",{name}\n{stream_url}\n'
                        count += 1
        except:
            pass

    print(f"Berhasil mengekstrak {count} channel ke dalam M3U.")

    # 4. Menulis data ke file mac_playlist.m3u
    with open('mac_playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
        
    print("File mac_playlist.m3u berhasil diperbarui!")

except Exception as e:
    print(f"Terjadi kesalahan teknis: {e}")
    sys.exit(1)
