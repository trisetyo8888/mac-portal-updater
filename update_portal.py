import requests
import json

def fetch_and_update():
    # URL asli dan MAC address Anda yang sudah disesuaikan untuk tipe portal Stalker
    portal_url = "http://nk.team-tx.st/c/"
    mac_address = "1A:79:b6:eb:68"
    
    # Header wajib untuk mengelabui portal agar dikira perangkat STB asli
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp pb2 EmbeddedLinux plugin Components Qt/4.7.3",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "X-User-Agent": "model=MAG250; link=ethernet; mac={mac}; pkg=2.6.0".format(mac=mac_address),
        "Cookie": f"mac={mac_address}"
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        # Langkah 1: Handshake untuk mendapatkan Token Akses
        handshake_url = f"{portal_url}?type=stb&action=handshake&js=true"
        response = session.get(handshake_url, timeout=10)
        
        if response.status_code != 200:
            print(f"Gagal koneksi portal. Status: {response.status_code}")
            return

        res_data = response.json()
        token = res_data.get("js", {}).get("token")
        
        if not token:
            print("Portal menolak MAC Address atau token tidak ditemukan.")
            return

        # Perbarui header menggunakan token baru
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
