import requests
import json

def fetch_and_update():
    # Menggunakan Proxy Server untuk membongkar pemblokiran DNS/IP di GitHub Actions
    proxy_url = "https://herokuapp.com"
    target_url = "http://team-tx.st"
    api_url = proxy_url + target_url
    
    mac_address = "1A:79:b6:eb:68"
    
    # Header wajib agar lolos validasi keamanan portal
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 aurora/2.1.2 Safari/533.3",
        "X-User-Agent": f"model=MAG250; gpsi=6/22/2013-1; mac={mac_address}",
        "Origin": "http://team-tx.st",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        print("--- MEMULAI PROSES EKSPOR MAC PORTAL VIA PROXY ---")
        print(f"Menghubungi alamat bypass: {api_url}")
        
        # Langkah 1: Handshake Awal
        params_handshake = {
            "type": "stb",
            "action": "handshake",
            "js": "true"
        }
        
        response = session.get(api_url, params=params_handshake, timeout=25)
        print("Status Koneksi Awal:", response.status_code)
        
        if response.status_code != 200:
            print(f"Akses ditolak server proxy/portal! Status: {response.status_code}")
            print("Isi teks server:", response.text[:300])
            return

        try:
            res_json = response.json()
            print("Balasan Struktur Server Sukses Dibaca.")
        except Exception:
            print("Server tidak membalas dengan JSON yang valid! Isi teks asli:")
            print(response.text[:400])
            return
            
        token = None
        if isinstance(res_json, dict):
            if "js" in res_json and isinstance(res_json["js"], dict):
                token = res_json["js"].get("token")
            if not token:
                token = res_json.get("token")
                
        if not token:
            print("Gagal menemukan token akses. Isi JSON server:", res_json)
            return
            
        print("Akses Diterima! Token sukses didapatkan.")
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Langkah 2: Registrasi Sesi Profil
        params_profile = {
            "type": "stb",
            "action": "get_profile",
            "token": token
        }
        session.get(api_url, params=params_profile, timeout=25)
        
        # Langkah 3: Ambil Seluruh Data Channel IPTV
        print("Mengunduh seluruh daftar siaran...")
        params_channels = {
            "type": "itv",
            "action": "get_all_channels",
            "token": token
        }
        channels_res = session.get(api_url, params=params_channels, timeout=25)
        
        if channels_res.status_code == 200:
            try:
                portal_data = channels_res.json()
                with open("exported_portal.json", "w", encoding="utf-8") as f:
                    json.dump(portal_data, f, indent=4, ensure_ascii=False)
                print("Pembaruan data sukses! File exported_portal.json berhasil dibuat.")
            except Exception:
                print("Gagal mengubah daftar channel menjadi JSON. Server membalas:")
                print(channels_res.text[:300])
        else:
            print(f"Gagal mengambil siaran. Status server: {channels_res.status_code}")
            
    except Exception as e:
        print(f"Terjadi kesalahan koneksi absolut via Proxy: {e}")

if __name__ == "__main__":
    fetch_and_update()
