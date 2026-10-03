import requests
import json

def fetch_and_update():
    # Contoh target API portal atau logika pemindaian/pembaruan Anda
    portal_url = "http://nk.team-tx.st/c/"
    mac_address = "1A:79:b6:eb:68"
    
    try:
        # Ganti dengan parameter yang sesuai dengan kebutuhan portal Anda
        response = requests.get(f"{portal_url}?mac={mac_address}")
        if response.status_code == 200:
            data = response.json()
            
            # Simpan hasil ekspor ke dalam file
            with open("exported_portal.json", "w") as f:
                json.dump(data, f, indent=4)
            print("Pembaruan berhasil disimpan.")
        else:
            print("Gagal mengambil data dari portal.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    fetch_and_update()
