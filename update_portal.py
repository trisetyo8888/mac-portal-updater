import requests
import json

def fetch_and_update():
    # Menggunakan URL load.php absolut
    api_url = "http://team-tx.st"
    mac_address = "1A:79:b6:eb:68"
    
    # Menambahkan 'Host' header secara manual agar koneksi tidak dipotong oleh requests Python
    headers = {
        "Host": "nk.team-tx.st",
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 aurora/2.1.2 Safari/533.3",
        "X-User-Agent": f"model=MAG250; gpsi=6/22/2013-1; mac={mac_address}",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        print("--- MEMULAI PROSES EKSPOR MAC PORTAL ---")
        
        # Langkah 1: Handshake Awal
        params_handshake = {
            "type": "stb",
            "action": "handshake",
            "js": "true"
        }
        
        # menonaktifkan allow_redirects agar requests tidak melompat ke domain induk yang rusak
        response = session.get(api_url, params=params_handshake, timeout=15, allow_redirects=False)
        print("Status Koneksi Awal:", response.status_code)
        
        if response.status_code != 200:
            print(f"Akses ditolak server portal! Status: {response.status_code}")
            print("Isi balasan server:", response.text[:300])
            return

        try:
            res_json = response.json()
            print("Balasan Struktur Server Sukses Dibaca.")
        except Exception:
            print("Server tidak membalas dengan JSON yang valid! Isi teks asli server:")
            print(response.text[:500])
            return
            
        token = None
        if isinstance(res_json, dict):
            if "js" in res_json and isinstance(res_json["js"], dict):
                token = res_json["js"].get("token")
            if not token:
                token = res_json.get("token")
                
        if not token:
            print("Gagal menemukan token akses. Isi JSON dari server adalah:", res_json)
            return
            
        print("Akses Diterima! Token sukses didapatkan.")
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Langkah 2: Registrasi Sesi Profil
        params_profile = {
            "type": "stb",
            "action": "get_profile",
            "token": token
        }
        session.get(api_url, params=params_profile, timeout=15, allow_redirects=False)
        
        # Langkah 3: Ambil Seluruh Data Channel IPTV
        print("Mengunduh seluruh daftar siaran...")
        params_channels = {
            "type": "itv",
            "action": "get_all_channels",
            "token": token
        }
        channels_res = session.get(api_url, params=params_channels, timeout=15, allow_redirects=False)
        
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
        print(f"Terjadi kesalahan koneksi absolut: {e}")

if __name__ == "__main__":
    fetch_and_update()
