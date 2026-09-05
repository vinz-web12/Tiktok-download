import os
import json
import requests
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = "7961613868:AAExZB1W9L5EinCeDvwGASisthoLGgYayBM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ========== DATABASE ==========
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, chat_id TEXT, username TEXT, first_name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, chat_id TEXT, command TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('active', 'true')")
    conn.commit()
    conn.close()

init_db()

def get_setting(key):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 'true'

def set_setting(key, value):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def save_user(chat_id, username, first_name):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (chat_id, username, first_name) VALUES (?, ?, ?)", (str(chat_id), username or '', first_name or ''))
    conn.commit()
    conn.close()

def save_log(chat_id, command):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO logs (chat_id, command, timestamp) VALUES (?, ?, ?)", (str(chat_id), command, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def get_logs(limit=20):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT chat_id, command, timestamp FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    result = c.fetchall()
    conn.close()
    return result

# ========== SEND MESSAGE ==========
def send_message(chat_id, text, parse_mode="Markdown"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def send_video(chat_id, video_url, caption=""):
    payload = {"chat_id": chat_id, "video": video_url, "caption": caption}
    requests.post(f"{TELEGRAM_API}/sendVideo", json=payload)

def send_audio(chat_id, audio_url, caption=""):
    payload = {"chat_id": chat_id, "audio": audio_url, "caption": caption}
    requests.post(f"{TELEGRAM_API}/sendAudio", json=payload)

# ========== COMMAND HANDLERS ==========
def handle_command(chat_id, text):
    save_log(chat_id, text.split()[0] if text else 'unknown')

    if text.startswith("/start"):
        send_message(chat_id, "🤖 *Bot Aktif!*\n\nGunakan /tiktok <link> buat download video.\nGunakan /mp3 <link> buat download audio.\nGunakan /status buat cek status bot.")
        return

    if text.startswith("/tiktok"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_message(chat_id, "⚠️ Gunakan: /tiktok <link>\nContoh: /tiktok https://tiktok.com/@user/video/123")
            return
        url = parts[1].strip()
        send_message(chat_id, "⏳ Lagi ambil videonya...")
        try:
            api_url = f"https://www.tikwm.com/api/?url={url}&hd=1"
            response = requests.get(api_url)
            data = response.json()
            if data.get('code') == 0:
                send_video(chat_id, data['data']['play'], f"🎬 {data['data']['title']}")
            else:
                send_message(chat_id, "❌ Gagal ambil video. Coba link lain, Bos.")
        except Exception as e:
            send_message(chat_id, f"❌ Error: {str(e)}")
        return

    if text.startswith("/mp3"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_message(chat_id, "⚠️ Gunakan: /mp3 <link>")
            return
        url = parts[1].strip()
        send_message(chat_id, "⏳ Lagi ambil audionya...")
        try:
            api_url = f"https://www.tikwm.com/api/?url={url}"
            response = requests.get(api_url)
            data = response.json()
            if data.get('code') == 0:
                send_audio(chat_id, data['data']['music'], f"🎵 {data['data']['music_info']['title']}")
            else:
                send_message(chat_id, "❌ Gagal ambil audio.")
        except Exception as e:
            send_message(chat_id, f"❌ Error: {str(e)}")
        return

    if text.startswith("/status"):
        active = get_setting('active') == 'true'
        send_message(chat_id, f"🔍 *Status Bot*\n\n🤖 Bot: {'✅ Aktif' if active else '❌ Nonaktif'}\n👥 User: {get_users()}", parse_mode="Markdown")
        return

    send_message(chat_id, "❓ Perintah tidak dikenali. Gunakan /tiktok atau /mp3.")

# ========== WEBHOOK ==========
@app.route("/webhook", methods=["POST"])
def webhook():
    if get_setting('active') == 'false':
        return jsonify({"status": "bot inactive"}), 200

    try:
        update = request.get_json()
        if not update or 'message' not in update:
            return jsonify({"status": "error"}), 400

        msg = update['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '')
        user = msg.get('from', {})
        save_user(chat_id, user.get('username', ''), user.get('first_name', ''))

        handle_command(chat_id, text)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

# ========== API DASHBOARD ==========
@app.route("/api/status", methods=["GET"])
def api_status():
    active = get_setting('active') == 'true'
    logs = get_logs(15)
    return jsonify({
        "active": active,
        "total_users": get_users(),
        "total_commands": len(logs),
        "logs": [{"chat_id": l[0], "command": l[1], "time": l[2]} for l in logs]
    })

@app.route("/api/toggle", methods=["POST"])
def api_toggle():
    data = request.get_json()
    if data and 'active' in data:
        set_setting('active', 'true' if data['active'] else 'false')
        return jsonify({"status": "ok", "active": data['active']})
    return jsonify({"status": "error"}), 400

@app.route("/api/set_webhook", methods=["POST"])
def api_set_webhook():
    data = request.get_json()
    url = data.get('url') if data else None
    if url:
        try:
            response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={url}")
            if response.ok:
                return jsonify({"status": "ok", "webhook": url})
            return jsonify({"status": "error", "msg": response.text}), 500
        except Exception as e:
            return jsonify({"status": "error", "msg": str(e)}), 500
    return jsonify({"status": "error"}), 400

# ========== ROOT ==========
@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot Telegram aktif. Dashboard di /dashboard"

# Vercel entry point
app = app
