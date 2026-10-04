import requests
import json
import sys
import hashlib
import urllib3
import re

# Menonaktifkan peringatan SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_free_proxies():
    """Mengambil daftar proxy gratis secara real-time"""
    print("[Log] Mengambil daftar proxy publik gratis...")
    urls = [
        "https://proxyscrape.com",
        "https://githubusercontent.com"
    ]
    proxies = []
    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                found = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', res.text)
                proxies.extend(found)
        except:
            continue
    return list(set(proxies))[:15] # Ambil 15 proxy teratas untuk dites

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

    # Dapatkan daftar proxy
    proxy_list = get_free_proxies()
    
    session = requests.Session()
    session.headers.update(headers)
    
    success = False
    req_handshake = None
    
    print(f"[Log] Menemukan {len(proxy_list)} proxy kandidat. Mencoba menembus blokir server...")
    
    # Mencoba melakukan jabat tangan menggunakan proxy satu per satu hingga berhasil
    for p in proxy_list:
        proxy_config = {
            "http": f"http://{p}",
            "https://": f"http://{p}"
        }
        try:
            handshake_url = (
                f"{portal_url}?type=stb&action=handshake&mac={mac_address}"
                f"&sn={serial_mock}&device_id={device_id_mock}&device_id2={device_id_mock}"
            )
            print(f" -> Mencoba via Proxy: {p}")
            res = session.get(handshake_url, timeout=12, verify=False, proxies=proxy_config)
            if res.status_code == 200:
                req_handshake = res
                session.proxies.update(proxy_config) # Kunci proxy ini untuk request berikutnya
                print(f" ✅ Sukses bypass menggunakan proxy: {p}")
                success = True
                break
        except Exception as e:
            continue

    # Jika semua proxy publik gagal, gunakan koneksi langsung bawaan GitHub sebagai fallback terakhir
    if not success:
        print("⚠️ Semua proxy gagal merespon. Mencoba jalur langsung tanpa proxy...")
        try:
            handshake_url = (
                f"{portal_url}?type=stb&action=handshake&mac={mac_address}"
                f"&sn={serial_mock}&device_id={device_id_mock}&device_id2={device_id_mock}"
            )
            req_handshake = session.get(handshake_url, timeout=20, verify=False)
            if req_handshake.status_code == 200:
                success = True
        except Exception as direct_err:
            print(f"❌ Jalur langsung juga error: {direct_err}")

    if not success or req_handshake is None:
        print("❌ Server IPTV benar-benar tidak bisa dijangkau dari cloud GitHub.")
        sys.exit(1)

    try:
        token = ""
        try:
            res_json = req_handshake.json()
            token = res_json.get("js", {}).get("token", "")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
                print("   [Log] Token otentikasi diterapkan.")
        except:
            print("   [Log] Handshake berjalan murni dengan identitas MAC.")

        print("2. Mengambil daftar kategori saluran...")
        cat_url = (
            f"{portal_url}?type=itv&action=get_categories&mac={mac_address}"
            f"&sn={serial_mock}&device_id={device_id_mock}"
        )
        req_cat = session.get(cat_url, timeout=20, verify=False)
        categories = req_cat.json().get("js", [])
        
        m3u_content = "#EXTM3U\n"
        channel_count = 0

        print("3. Mengunduh data saluran per kategori...")
        for cat in categories:
            cat_id = cat.get("id")
            cat_name = cat.get("title")
            
            data_url = (
                f"{portal_url}?type=itv&action=get_ordered_list&category={cat_id}&mac={mac_address}"
                f"&sn={serial_mock}&device_id={device_id_mock}"
            )
            req_data = session.get(data_url, timeout=20, verify=False)
            
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
            print(f"✅ Selesai! Berhasil memproses total {channel_count} saluran ke {output_file}.")
        else:
            raise Exception("Kategori ditemukan tapi daftar saluran kosong.")

    except Exception as err:
        print(f"⚠️ Gagal ekstraksi penuh via cloud ({err}). Mengaktifkan link bypass darurat...")
        m3u_content = "#EXTM3U\n"
        stream_url = f"{portal_host}/portal.php?type=itv&action=create_link&mac={mac_address}"
        m3u_content += f'#EXTINF:-1 tvg-id="babo01_direct" group-title="Babo01 Stream Direct",Live MAC Portal\n'
        m3u_content += f'{stream_url}\n'
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print(f"✅ Jalur darurat sukses menulis ke {output_file}.")

if __name__ == "__main__":
    fetch_stalker_m3u()
