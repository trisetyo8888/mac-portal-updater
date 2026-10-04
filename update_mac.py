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
        
        token = ""
        if req_handshake.status_code == 200:
            try:
                res_json = req_handshake.json()
                token = res_json.get("js", {}).get("token", "")
                if token:
                    # Beberapa server Stalker menggunakan variasi header otentikasi ini
                    session.headers.update({
                        "Authorization": f"Bearer {token}",
                        "X-User-Token": token
                    })
                    print(f"   [Log] Token aktif ditemukan.")
            except:
                print("   [Log] Handshake sukses tanpa pembacaan token JSON.")

        print("2. Mengambil daftar kategori...")
        # Menambahkan parameter token langsung di URL (Sering diwajibkan oleh server Stalker)
        cat_url = f"{portal_url}?type=itv&action=get_categories&mac={mac_address}"
        if token:
            cat_url += f"&token={token}"
            
        req_cat = session.get(cat_url, timeout=20)
        
        print(f"   [Log] Status Kategori: {req_cat.status_code}")
        # Membantu debugging jika respon bukan JSON
        if not req_cat.text.strip().startswith("{") and not req_cat.text.strip().startswith("["):
            print(f"   [Log] Respon Server Kategori (Bukan JSON): {req_cat.text[:200]}")
            
        try:
            categories = req_cat.json().get("js", [])
        except Exception as json_err:
            print(f"❌ Respon server tidak bisa dibaca sebagai JSON. Error: {json_err}")
            sys.exit(1)
            
        if not categories:
            print("❌ Tidak ada kategori yang ditemukan. Akun mungkin perlu detail header tambahan.")
            sys.exit(1)
        
        m3u_content = "#EXTM3U\n"
        channel_count = 0

        print("3. Mengunduh data saluran...")
        for cat in categories:
            cat_id = cat.get("id")
            cat_name = cat.get("title")
            
            data_url = f"{portal_url}?type=itv&action=get_ordered_list&category={cat_id}&mac={mac_address}"
            if token:
                data_url += f"&token={token}"
                
            req_data = session.get(data_url, timeout=20)
            
            if req_data.status_code == 200:
                try:
                    channels = req_data.json().get("js", {}).get("data", [])
                    for ch in channels:
                        ch_name = ch.get("name")
                        ch_id = ch.get("id")
                        cmd = ch.get("cmd", "")
                        
                        if cmd.startswith("ffmpeg "):
                            cmd = cmd.replace("ffmpeg ", "", 1)
                            
                        stream_url = f"{portal_host}/portal.php?type=itv&action=create_link&cmd={cmd}&mac={mac_address}"
                        if token:
                            stream_url += f"&token={token}"
                            
                        m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}" group-title="{cat_name}",{ch_name}\n'
                        m3u_content += f'{stream_url}\n'
                        channel_count += 1
                except:
                    continue
                    
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
