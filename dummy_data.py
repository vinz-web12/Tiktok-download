import json
import random
import os
from datetime import datetime, timedelta

class DummyData:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_db.json')
        self.load_db()
    
    def load_db(self):
        with open(self.db_path, 'r') as f:
            self.db = json.load(f)
    
    def get_user(self, number):
        for user in self.db:
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
    
    def get_history(self, number):
        user = self.get_user(number)
        if not user:
            return None
        base_lat = user['lat']
        base_lng = user['lng']
        history = []
        for i in range(10):
            history.append({
                'lat': base_lat + random.uniform(-0.02, 0.02),
                'lng': base_lng + random.uniform(-0.02, 0.02),
                'time': (datetime.now() - timedelta(minutes=i*5)).strftime('%H:%M')
            })
        return history[::-1]