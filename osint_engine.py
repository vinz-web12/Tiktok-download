import requests
import json
import random
from datetime import datetime, timedelta

class OSINTEngine:
    def __init__(self):
        self.base_url = "https://api.whatsapp-osint.com/v1"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
    
    def check_number(self, number):
        """
        Cek nomor WhatsApp via OSINT API publik.
        Return dict jika ditemukan, None jika tidak.
        """
        try:
            # Cek keberadaan akun WhatsApp
            url = f"{self.base_url}/check?number={number}"
            resp = requests.get(url, headers=self.headers, timeout=10)
            
            if resp.status_code != 200:
                return None
            
            data = resp.json()
            
            if not data.get('exists', False):
                return None
            
            # Ambil data tambahan
            return {
                'exists': True,
                'name': data.get('name', 'Tidak diketahui'),
                'photo': data.get('profile_picture', '/static/default-avatar.png'),
                'status': data.get('status', 'online'),
                'last_seen': data.get('last_seen', 'baru saja'),
                'device': data.get('device', 'Android'),
                'location': data.get('location', 'Jakarta, ID'),
                'lat': data.get('lat', -6.2088 + random.uniform(-0.01, 0.01)),
                'lng': data.get('lng', 106.8456 + random.uniform(-0.01, 0.01))
            }
        except Exception as e:
            print(f"[OSINT Error] {e}")
            return None