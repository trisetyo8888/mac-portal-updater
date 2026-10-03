import requests
import json

def fetch_and_update():
    # === SILAKAN SESUAIKAN DUA BARIS DI BAWAH INI ===
    portal_url = "http://contoh-portal.com" 
    mac_address = "00:1A:79:XX:XX:XX"
    
    # Menambahkan User-Agent agar tidak terdeteksi sebagai robot/bot otomatis
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # Menghubungi portal untuk meminta token/akses
        login_url = f"{portal_url}?mac={mac_address}"
        print(f"Mencoba menghubungi: {login_url}")
        
        response = session.get(login_url, timeout=15)
        
        # Cetak isi respons mentah untuk proses analisa jika terjadi eror lagi
        print("Respons Status Code:", response.status_code)
        print("Isi Respons Mentah (100 karakter pertama):", response.text[:100])
        
        # Mencoba membaca data JSON
        res_data = response.json()
        token = res_data.get("js", {}).get("token")
        
        if not token:
            print("Portal menolak MAC Address atau token tidak ditemukan.")
            return
            
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Langkah 2: Mengambil daftar siaran/channel
        data_url = f"{portal_url}?type=itv&action=get_all_channels"
        data_response = session.get(data_url, timeout=15)
        
        if data_response.status_code == 200:
            portal_data = data_response.json()
            
            # Simpan hasil ke file JSON
            with open("exported_portal.json", "w", encoding="utf-8") as f:
                json.dump(portal_data, f, indent=4, ensure_ascii=False)
            print("Pembaruan data portal berhasil disimpan ke exported_portal.json.")
        else:
            print(f"Gagal mengambil channel. Status: {data_response.status_code}")
            
    except Exception as e:
        print(f"Terjadi kesalahan teknis: {e}")

if __name__ == "__main__":
    fetch_and_update()









