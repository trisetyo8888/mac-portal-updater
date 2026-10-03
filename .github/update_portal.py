import requests
import json

def fetch_and_update():
    # Menggunakan URL load.php absolut sesuai domain mac portal Anda
    api_url = "http://team-tx.st"
    mac_address = "1A:79:b6:eb:68"
    
    # Header standard untuk MAC Portal agar dikenali sebagai pemutar IPTV resmi
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 aurora/2.1.2 Safari/533.3",
        "X-User-Agent": f"model=MAG250; gpsi=6/22/2013-1; mac={mac_address}",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # Langkah 1: Handshake
        print("Mencoba menghubungkan skrip ke MAC Portal...")
        params_handshake = {
            "type": "stb",
            "action": "handshake",
            "js": "true"
        }
        
        response = session.get(api_url, params=params_handshake, timeout=15)
        print("Status Koneksi Awal:", response.status_code)
        
        res_json = response.json()
        token = res_json.get("js", {}).get("token") or res_json.get("token")
        
        if not token:
            print("Portal menolak akses MAC Address atau Token tidak ditemukan.")
            return
            
        print("Akses Diterima! Token didapatkan.")
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Langkah 2: Otentikasi Profil
        params_profile = {
            "type": "stb",
            "action": "get_profile",
            "token": token
        }
        session.get(api_url, params=params_profile, timeout=15)
        
        # Langkah 3: Mengambil Data Siaran Channel
        print("Mengunduh seluruh daftar siaran...")
        params_channels = {
            "type": "itv",
            "action": "get_all_channels",
            "token": token
        }
        channels_res = session.get(api_url, params=params_channels, timeout=15)
        
        if channels_res.status_code == 200:
            portal_data = channels_res.json()
            
            # Simpan hasil ekspor ke file json
            with open("exported_portal.json", "w", encoding="utf-8") as f:
                json.dump(portal_data, f, indent=4, ensure_ascii=False)
            print("Pembaruan data sukses! File exported_portal.json berhasil dibuat.")
        else:
            print(f"Gagal mengambil siaran. Status server: {channels_res.status_code}")
            
    except Exception as e:
        print(f"Terjadi kesalahan koneksi: {e}")

if __name__ == "__main__":
    fetch_and_update()
