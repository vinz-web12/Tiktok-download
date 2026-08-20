from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# ===== DUMMY DATA =====
DUMMY_DB = [
    {"number": "+6281234567890", "name": "Alina Putri", "lat": -6.2088, "lng": 106.8456, "location": "Jakarta Selatan", "device": "iPhone 15 Pro"},
    {"number": "+6281234567891", "name": "Bima Sakti", "lat": -6.1754, "lng": 106.8271, "location": "Jakarta Pusat", "device": "Samsung S24"},
    {"number": "+6281234567892", "name": "Citra Dewi", "lat": -6.2634, "lng": 106.7945, "location": "Jakarta Barat", "device": "Xiaomi 14"}
]

def get_user(number):
    for user in DUMMY_DB:
        if user['number'] == number:
            return {
                'name': user['name'],
                'number': user['number'],
                'lat': user['lat'] + random.uniform(-0.005, 0.005),
                'lng': user['lng'] + random.uniform(-0.005, 0.005),
                'status': random.choice(['online', 'online', 'online', 'offline']),
                'last_seen': (datetime.now() - timedelta(minutes=random.randint(1, 30))).strftime('%H:%M'),
                'location': user['location'],
                'device': user['device'],
                'photo': '/static/default-avatar.png',
                'source': 'dummy'
            }
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/track', methods=['POST'])
def track():
    data = request.get_json()
    number = data.get('number', '').strip()
    if not number:
        return jsonify({'error': 'Nomor kosong'}), 400
    user = get_user(number)
    if user:
        return jsonify(user)
    return jsonify({'error': 'Nomor tidak ditemukan'}), 404

if __name__ == '__main__':
    app.run(debug=True)
