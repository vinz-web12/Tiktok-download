import os
import sys
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# ========== INISIALISASI ==========
app = Flask(__name__)
CORS(app)

# ========== PATH UTILITIES ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DUMMY_DB_PATH = os.path.join(DATA_DIR, 'dummy_db.json')

# ========== OSINT ENGINE (DIREKT DI SINI BIAR GAK IMPORT GAGAL) ==========
def osint_check_number(number):
    """Cek nomor via OSINT API"""
    try:
        import requests
        url = f"https://api.whatsapp-osint.com/v1/check?number={number}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('exists'):
                return {
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

# ========== DUMMY DATA ==========
def load_dummy_db():
    try:
        with open(DUMMY_DB_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_dummy_user(number):
    db = load_dummy_db()
    for user in db:
        if user['number'] == number:
            return {
                'name': user['name'],
                'number': user['number'],
                'lat': user['base_lat'] + random.uniform(-0.005, 0.005),
                'lng': user['base_lng'] + random.uniform(-0.005, 0.005),
                'status': random.choice(['online', 'online', 'online', 'offline']),
                'last_seen': (datetime.now() - timedelta(minutes=random.randint(1, 30))).strftime('%H:%M'),
                'location': user['location'],
                'device': user['device'],
                'photo': user.get('photo', '/static/default-avatar.png'),
                'source': 'dummy'
            }
    return None

# ========== ROUTES ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/track', methods=['POST'])
def track():
    data = request.get_json()
    number = data.get('number', '').strip()
    if not number:
        return jsonify({'error': 'Nomor tidak boleh kosong'}), 400

    # Coba OSINT
    osint_result = osint_check_number(number)
    if osint_result:
        osint_result['source'] = 'osint'
        return jsonify(osint_result)

    # Fallback dummy
    dummy_result = get_dummy_user(number)
    if dummy_result:
        return jsonify(dummy_result)

    return jsonify({'error': 'Nomor tidak ditemukan'}), 404

@app.route('/api/history', methods=['POST'])
def history():
    data = request.get_json()
    number = data.get('number', '').strip()
    dummy = get_dummy_user(number)
    if not dummy:
        return jsonify({'error': 'Data tidak ditemukan'}), 404

    base_lat = dummy['lat']
    base_lng = dummy['lng']
    history_points = []
    for i in range(10):
        history_points.append({
            'lat': base_lat + random.uniform(-0.02, 0.02),
            'lng': base_lng + random.uniform(-0.02, 0.02),
            'time': (datetime.now() - timedelta(minutes=i*5)).strftime('%H:%M')
        })
    return jsonify(history_points[::-1])

# ========== UNTUK VERCEL ==========
# Ini yang bikin Vercel bisa jalan
if __name__ == '__main__':
    app.run(debug=True)
