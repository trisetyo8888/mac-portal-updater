import requests
import json
import sys

def fetch_stalker_m3u():
    # ==================== PENGATURAN PORTAL ANDA ====================
    # Pastikan URL ini sudah benar menggunakan milik Anda
    portal_host = "http://z1.babo01.com:8080/c/" 
    mac_address = "00:1A:79:1f:0e:30" 
    output_file = "mac_playlist.m3u"
    # ================================================================

    portal_url = f"{portal_host}/portal.php"
    
    # Menggunakan User-Agent yang lebih umum digunakan oleh pemutar IPTV modern
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": f"mac={mac_address}; stb_lang=en; timezone=GMT",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        print("1. Mencoba Handshake dengan server...")
        handshake_url = f"{portal_url}?type=stb&action=handshake&mac={mac_address}"
        req_handshake = session.get(handshake_url, timeout=20)
        
        print(f"   [Log] Status Handshake: {req_handshake.status_code}")
        print(f"   [Log] Respon Server: {req_handshake.text[:200]}") # Intip isi respon server

        if req_handshake.status_code != 200:
            print("❌ Gagal Handshake. Server memblokir koneksi dari GitHub Actions (Kemungkinan IP Terblokir/Geo-block).")
            sys.exit(1)

        try:
            res_json = req_handshake.json()
            token = res_json.get("js", {}).get("token", "")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
                print("   [Log] Token berhasil didapatkan.")
        except:
            print("   [Log] Berjalan tanpa token bearer (menggunakan cookie).")
        
        print("2. Mengambil daftar kategori...")
        cat_url = f"{portal_url}?type=itv&action=get_categories&mac={mac_address}"
        req_cat = session.get(cat_url, timeout=20)
        
        if req_cat.status_code != 200:
            print(f"❌ Gagal mengambil kategori. Status: {req_cat.status_code}")
            sys.exit(1)
            
        categories = req_cat.json().get("js", [])
        if not categories:
            print("❌ Tidak ada kategori yang ditemukan. Akun MAC mungkin mati atau diblokir oleh server.")
            sys.exit(1)
        
        m3u_content = "#EXTM3U\n"
        channel_count = 0

        print("3. Mengunduh data saluran...")
        for cat in categories:
            cat_id = cat.get("id")
            cat_name = cat.get("title")
            
            data_url = f"{portal_url}?type=itv&action=get_ordered_list&category={cat_id}&mac={mac_address}"
            req_data = session.get(data_url, timeout=20)
            
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
                    
        if channel_count > 0:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(m3u_content)
            print(f"✅ Selesai! Berhasil mengekspor {channel_count} saluran.")
        else:
            print("❌ Gagal: Saluran kosong.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Terjadi kesalahan sistem: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_stalker_m3u()
