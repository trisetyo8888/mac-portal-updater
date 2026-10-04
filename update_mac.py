import requests
import json

def fetch_stalker_m3u():
    # ==================== PENGATURAN PORTAL ANDA ====================
    # 1. Ganti dengan URL Host Portal Anda (tanpa /portal.php di ujungnya)
    portal_host = "http://z1.babo01.com:8080/c/" 
    
    # 2. Ganti dengan MAC Address aktif Anda
    mac_address = "00:1A:79:1f:0e:30" 
    
    # Nama file hasil ekspor otomatis
    output_file = "mac_playlist.m3u"
    # ================================================================

    portal_url = f"{portal_host}/portal.php"
    
    # Setup Headers menyerupai STB MAG
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3",
        "Cookie": f"mac={mac_address}; stb_lang=en; timezone=GMT"
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        print("1. Melakukan jabat tangan (handshake) dengan server...")
        handshake_url = f"{portal_url}?type=stb&action=handshake&mac={mac_address}"
        req_handshake = session.get(handshake_url, timeout=15)
        
        if req_handshake.status_code == 200:
            try:
                res_json = req_handshake.json()
                token = res_json.get("js", {}).get("token", "")
                if token:
                    session.headers.update({"Authorization": f"Bearer {token}"})
            except:
                pass 
        
        print("2. Mengambil daftar kategori saluran...")
        cat_url = f"{portal_url}?type=itv&action=get_categories&mac={mac_address}"
        req_cat = session.get(cat_url, timeout=15)
        
        if req_cat.status_code != 200:
            print(f"Gagal koneksi ke portal. Status: {req_cat.status_code}")
            return
            
        categories = req_cat.json().get("js", [])
        
        m3u_content = "#EXTM3U\n"
        channel_count = 0

        print("3. Mengunduh data saluran & konversi ke M3U...")
        for cat in categories:
            cat_id = cat.get("id")
            cat_name = cat.get("title")
            
            data_url = f"{portal_url}?type=itv&action=get_ordered_list&category={cat_id}&mac={mac_address}"
            req_data = session.get(data_url, timeout=15)
            
            if req_data.status_code == 200:
                channels = req_data.json().get("js", {}).get("data", [])
                for ch in channels:
                    ch_name = ch.get("name")
                    ch_id = ch.get("id")
                    cmd = ch.get("cmd", "")
                    
                    if cmd.startswith("ffmpeg "):
                        cmd = cmd.replace("ffmpeg ", "", 1)
                        
                    stream_url = f"{portal_host}/portal.php?type=itv&action=create_link&cmd={cmd}&mac={mac_address}"
                    
                    m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}" group-title="{cat_name}",{ch_name}\n'
                    m3u_content += f'{stream_url}\n'
                    channel_count += 1
                    
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(m3u_content)
            
        print(f"Selesai! Berhasil mengekspor {channel_count} saluran ke {output_file}")

    except Exception as e:
        print(f"Terjadi kesalahan saat memproses portal: {e}")

if __name__ == "__main__":
    fetch_stalker_m3u()
