import requests
import json
import re

def fetch_and_update():
    # URL dasar portal stalker Anda
    base_url = "http://nk.team-tx.st/c/" 
    mac_address = "1A:79:b6:eb:68" # MAC dari log Anda
    
    # Header wajib untuk mengelabui server seolah-olah kita adalah STB MAG
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 aurora/2.1.2 Safari/533.3",
        "X-User-Agent": "model=MAG250; gpsi=6/22/2013-1; mac=1A:79:b6:eb:68",
        "Referer": "http://team-tx.st",
        "Accept": "*/*",
        "Host": "nk.team-tx.st",
        "Connection": "Keep-Alive"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    # URL API internal stalker untuk otentikasi
    api_url = "http://team-tx.st"
    
    try:
        # Langkah 1: Handshake untuk meminta Token / Cookies
        print("Mencoba melakukan Handshake ke Stalker Portal...")
        params_handshake = {
            "type": "stb",
            "action": "handshake",
            "js": "true"
        }
        
        # Stalker Portal membutuhkan Cookies untuk menjaga sesi login
        response = session.get(api_url, params=params_handshake, timeout=15)
        print("Handshake Status:", response.status_code)
        
        res_json = response.json()
        token = res_json.get("js", {}).get("token")
        
        if not token:
            print("Gagal mendapatkan token Stalker. Respons:", response.text)
            return
            
        print("Token Stalker didapatkan:", token)
        
        # Daftarkan token ke header Authorization untuk request selanjutnya
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Langkah 2: Proses Login/Otentikasi menggunakan MAC Address
        print("Mencoba login dengan MAC Address...")
        params_login = {
            "type": "stb",
            "action": "do_auth",
            "mac": mac_address
        }
        login_res = session.get(api_url, params=params_login, timeout=15)
        print("Login Status:", login_res.status_code)
        
        # Langkah 3: Mengambil semua daftar siaran (All Channels)
        print("Mengambil daftar channel...")
        params_channels = {
            "type": "itv",
            "action": "get_all_channels"
        }
        channels_res = session.get(api_url, params=params_channels, timeout=15)
        
        if channels_res.status_code == 200:
            portal_data = channels_res.json()
            
            # Simpan data asli berbentuk JSON ke repositori
            with open("exported_portal.json", "w", encoding="utf-8") as f:
                json.dump(portal_data, f, indent=4, ensure_ascii=False)
            print("Pembaruan data portal berhasil disimpan ke exported_portal.json.")
        else:
            print(f"Gagal mengambil channel. Status: {channels_res.status_code}")
            
    except Exception as e:
        print(f"Terjadi kesalahan teknis Stalker: {e}")

if __name__ == "__main__":
    fetch_and_update()
