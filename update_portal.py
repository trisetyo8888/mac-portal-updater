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
    token = ""
    if response.status_code == 200:
        try:
            json_data = response.json()
            token = json_data.get('js', {}).get('token', '')
            if token:
                headers['Authorization'] = f"Bearer {token}"
                print(f"Autentikasi Berhasil! Token diperoleh.")
        except Exception:
            pass

    # Langkah B: Ambil data channel
    channels_url = f"{api_url}?type=itv&action=get_all_channels"
    res = requests.get(channels_url, headers=headers, timeout=20)
    
    if res.status_code != 200:
        print(f"Gagal mengambil data dari server. Status Code: {res.status_code}")
        sys.exit(1)
        
    try:
        data = res.json()
        channels_list = data.get('js', [])
    except Exception:
        # Jika server merespons dalam format string teks JSON murni
        try:
            data = json.loads(res.text)
            channels_list = data.get('js', [])
        except Exception:
            print("Gagal membaca struktur data dari server.")
            sys.exit(1)
            
    print(f"Berhasil menarik data! Memproses data channel...")

    # 3. Menyusun ulang data menjadi file Playlist M3U (Proteksi Eror Tipe Data)
    m3u_content = "#EXTM3U\n"
    
    # Jika data berupa List Kamus (Format Standard)
    if isinstance(channels_list, list):
        for ch in channels_list:
            if isinstance(ch, dict):
                ch_name = ch.get('name', 'Unknown Channel')
                ch_cmd = ch.get('cmd', '')
                ch_id = ch.get('id', '')
                ch_group = ch.get('tv_genre_name', 'Lainnya')
            else:
                # Jika item di dalam list berupa string text
                ch_name = "Channel"
                ch_cmd = str(ch)
                ch_id = "tv"
                ch_group = "IPTV"
            
            # Cari link streaming tersembunyi di dalam cmd
            stream_url = ""
            if ch_cmd and isinstance(ch_cmd, str):
                match = re.search(r'(http[s]?://\S+)', ch_cmd)
                if match:
                    stream_url = match.group(1)
                else:
                    stream_url = f"{base_url}/playlist/live/{ch_id}.ts"
            
            if stream_url:
                m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}" group-title="{ch_group}",{ch_name}\n{stream_url}\n'
                
    print("Menyusun data ke dalam file M3U...")

    # 4. Menulis data ke file mac_playlist.m3u
    with open('mac_playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
        
    print("File mac_playlist.m3u berhasil diperbarui!")

except Exception as e:
    print(f"Terjadi kesalahan teknis: {e}")
    sys.exit(1)
