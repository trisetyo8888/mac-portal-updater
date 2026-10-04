import requests
import json
import sys
import hashlib

def fetch_stalker_m3u():
    # ==================== PENGATURAN PORTAL ANDA ====================
    portal_host = "http://babo01.com" 
    mac_address = "00:1A:79:1f:0e:30" 
    output_file = "mac_playlist.m3u"
    # ================================================================

    portal_url = f"{portal_host}/portal.php"
    
    mac_clean = mac_address.replace(":", "").upper()
    serial_mock = hashlib.md5(mac_clean.encode()).hexdigest()[:15].upper()
    device_id_mock = hashlib.sha256(mac_clean.encode()).hexdigest()[:40].upper()

    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3",
        "Cookie": f"mac={mac_address}; stb_lang=en; timezone=GMT",
        "Accept": "*/*",
        "X-User-Agent": "model=MAG250; gpsi=unknown; ver=0.2.18-r14-pub-250; flash=3.3.4",
        "Connection": "keep-alive"
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        print("1. Mencoba Handshake...")
        handshake_url = f"{portal_url}?type=stb&action=handshake&mac={mac_address}&sn={serial_mock}&device_id={device_id_mock}&device_id2={device_id_mock}"
        req_handshake = session.get(handshake_url, timeout=20)
        
        if req_handshake.status_code != 200:
            print(f"❌ Gagal Handshake. Status: {req_handshake.status_code}")
            return

        try:
            res_json = req_handshake.json()
            token = res_json.get("js", {}).get("token", "")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        except:
            pass

        print("2. Mengambil daftar kategori...")
        cat_url = f"{portal_url}?type=itv&action=get_categories&mac={mac_address}&sn={serial_mock}&device_id={device_id_mock}"
        req_cat = session.get(cat_url, timeout=20)
        categories = req_cat.json().get("js", [])
        
        m3u_content = "#EXTM3U\n"
        channel_count = 0

        print("3. Mengunduh data saluran...")
        for cat in categories:
            cat_id = cat.get("id")
            cat_name = cat.get("title")
            
            data_url = f"{portal_url}?type=itv&action=get_ordered_list&category={cat_id}&mac={mac_address}&sn={serial_mock}&device_id={device_id_mock}"
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
                        m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}" group-title="{cat_name}",{ch_name}\n'
                        m3u_content += f'{stream_url}\n'
                        channel_count += 1
                except:
                    continue
                    
        if channel_count > 0:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(m3u_content)
            print(f"✅ Berhasil mengekspor {channel_count} saluran.")
        else:
            print("❌ Saluran kosong.")

    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")

if __name__ == "__main__":
    fetch_stalker_m3u()
