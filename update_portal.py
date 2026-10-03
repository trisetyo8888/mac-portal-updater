import requests
import json

def fetch_and_update():
    # TETAP GUNAKAN load.php agar server merespon perintah API dengan format JSON
    api_url = "http://team-tx.st"
    mac_address = "1A:79:b6:eb:68"
    
    # Kumpulan Header MAG STB murni untuk lolos dari filter firewall portal
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 aurora/2.1.2 Safari/533.3",
        "X-User-Agent": "model=MAG250; gpsi=6/22/2013-1; mac=1A:79:b6:eb:68",
        # Alamat /c/ dimasukkan ke sini sebagai penanda asal perangkat (Referer)
        "Referer": "http://nk.team-tx.st/c/",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # Langkah 1: Handshake Bersih (Hanya mengirim parameter mutlak untuk menghindari error 400)
        print("Mencoba melakukan Handshake ke Stalker Portal...")
        params_handshake = {
            "type": "stb",
            "action": "handshake",
            "js": "true"
        }
        
        response = session.get(api_url, params=params_handshake, timeout=15)
        print("Handshake Status:", response.status_code)
        
        # Analisis jika balasan bukan JSON
        try:
            res_json = response.json()
        except Exception:
            print("Server tidak membalas dengan JSON. Isi balasan:", response.text[:200])
            return
            
        # Ekstraksi Token Otentikasi
        token = None
        if "js" in res_json and isinstance(res_json["js"], dict):
            token = res_json["js"].get("token")
        if not token:
            token = res_json.get("token")
            
        if not token:
            print("Gagal menemukan token dalam respon JSON:", res_json)
            return
            
        print("Token Stalker Berhasil Didapatkan:", token)
        
        # Rekatkan Token dan Cookie Sesi
        session.headers.update({"Authorization": f"Bearer {token}"})
        session.cookies.set("mac", mac_address, domain="nk.team-tx.st", path="/")
        
        # Langkah 2: Pendaftaran Profil & Validasi Akses MAC
        print("Mengirimkan konfirmasi login profil...")
        params_profile = {
            "type": "stb",
            "action": "get_profile",
            "token": token
        }
        session.get(api_url, params=params_profile, timeout=15)
        
        # Langkah 3: Mengunduh Seluruh Daftar Siaran / IPTV Channel
        print("Mengunduh daftar semua siaran channel...")
        params_channels = {
            "type": "itv",
            "action": "get_all_channels",
            "token": token
        }
        channels_res = session.get(api_url, params=params_channels, timeout=15)
        print("Status Unduh Channel:", channels_res.status_code)
        
        if channels_res.status_code == 200:
            portal_data = channels_res.json()
            
            # Simpan data portal ke dalam berkas repositori GitHub
            with open("exported_portal.json", "w", encoding="utf-8") as f:
                json.dump(portal_data, f, indent=4, ensure_ascii=False)
            print("Pembaruan data portal BERHASIL disimpan ke exported_portal.json!")
        else:
            print(f"Gagal mengambil channel. Status: {channels_res.status_code}")
            print("Pesan server:", channels_res.text[:200])
            
    except Exception as e:
        print(f"Terjadi kesalahan teknis Stalker: {e}")

if __name__ == "__main__":
    fetch_and_update()
