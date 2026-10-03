import requests
import json

def fetch_and_update():
    # Menembak langsung ke target load.php
    api_url = "http://team-tx.st"
    mac_address = "1A:79:b6:eb:68"
    
    # Kunci kombinasi header MAG STB asli agar server portal mau merespon IP GitHub Actions
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 aurora/2.1.2 Safari/533.3",
        "X-User-Agent": f"model=MAG250; gpsi=6/22/2013-1; mac={mac_address}",
        "Referer": "http://team-tx.st",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        print("--- MEMULAI PROSES EKSPOR MAC PORTAL ABSOLUT ---")
        print(f"Menghubungi: {api_url}")
        
        # Langkah 1: Handshake Awal (Tanpa mengizinkan pengalihan otomatis agar tidak eror DNS)
        params_handshake = {
            "type": "stb",
            "action": "handshake",
            "js": "true"
        }
        
        response = session.get(api_url, params=params_handshake, timeout=20, allow_redirects=False)
        print("Status Koneksi Awal:", response.status_code)
        
        if response.status_code != 200:
            print(f"Akses ditolak server portal! Status: {response.status_code}")
            return

        try:
            res_json = response.json()
            print("Balasan Struktur Server Sukses Dibaca.")
        except Exception:
            print("Server tidak membalas dengan JSON yang valid! Isi teks asli:")
            print(response.text[:300])
            return
            
        token = res_json.get("js", {}).get("token") or res_json.get("token")
        if not token:
            print("Gagal menemukan token akses. Isi balasan:", res_json)
            return
            
        print("Akses Diterima! Token sukses didapatkan.")
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Langkah 2: Registrasi Profil
        params_profile = {
            "type": "stb",
            "action": "get_profile",
            "token": token
        }
        session.get(api_url, params=params_profile, timeout=20, allow_redirects=False)
        
        # Langkah 3: Ambil Daftar Channel IPTV
        print("Mengunduh seluruh daftar siaran...")
        params_channels = {
            "type": "itv",
            "action": "get_all_channels",
            "token": token
        }
        channels_res = session.get(api_url, params=params_channels, timeout=20, allow_redirects=False)
        
        if channels_res.status_code == 200:
            portal_data = channels_res.json()
            with open("exported_portal.json", "w", encoding="utf-8") as f:
                json.dump(portal_data, f, indent=4, ensure_ascii=False)
            print("Pembaruan data sukses! File exported_portal.json berhasil dibuat.")
        else:
            print(f"Gagal mengambil siaran. Status server: {channels_res.status_code}")
            
    except Exception as e:
        print(f"Terjadi kesalahan koneksi murni: {e}")

if __name__ == "__main__":
    fetch_and_update()
