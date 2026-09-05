import os
import json
import requests
import sqlite3
from datetime import datetime

BOT_TOKEN = "7961613868:AAExZB1W9L5EinCeDvwGASisthoLGgYayBM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ========== DATABASE (SQLite) ==========
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, chat_id TEXT, username TEXT, first_name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, chat_id TEXT, command TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('bot_active', 'true')")
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

# ========== SEND MESSAGE ==========
def send_message(chat_id, text, parse_mode="Markdown"):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def send_video(chat_id, video_url, caption=""):
    payload = {
        "chat_id": chat_id,
        "video": video_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    requests.post(f"{TELEGRAM_API}/sendVideo", json=payload)

def send_audio(chat_id, audio_url, caption=""):
    payload = {
        "chat_id": chat_id,
        "audio": audio_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    requests.post(f"{TELEGRAM_API}/sendAudio", json=payload)

# ========== COMMAND HANDLERS ==========
def handle_command(chat_id, text, user_data):
    save_log(chat_id, text.split()[0])

    if text.startswith("/start"):
        send_message(chat_id, "🤖 *Bot Web Aktif!*\n\nGunakan /menu untuk lihat fitur.\nGunakan /tiktok <link> buat download video.", parse_mode="Markdown")
        return

    if text.startswith("/menu"):
        send_message(chat_id, "📋 *Menu Bot*\n\n1. /start - Mulai\n2. /tiktok <link> - Download video TikTok\n3. /mp3 <link> - Download audio TikTok\n4. /status - Cek status bot", parse_mode="Markdown")
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
                video_url = data['data']['play']
                title = data['data']['title']
                send_video(chat_id, video_url, f"🎬 {title}")
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
                audio_url = data['data']['music']
                title = data['data']['music_info']['title']
                send_audio(chat_id, audio_url, f"🎵 {title}")
            else:
                send_message(chat_id, "❌ Gagal ambil audio.")
        except Exception as e:
            send_message(chat_id, f"❌ Error: {str(e)}")
        return

    if text.startswith("/status"):
        bot_active = get_setting('bot_active')
        send_message(chat_id, f"🔍 *Status Bot*\n\n🤖 Bot: {'✅ Aktif' if bot_active == 'true' else '❌ Nonaktif'}", parse_mode="Markdown")
        return

    send_message(chat_id, "❓ Perintah tidak dikenali. Gunakan /menu.")

# ========== PROCESS UPDATE ==========
def process_update(update_data):
    if get_setting('bot_active') == 'false':
        return {"status": "bot inactive"}

    if 'message' in update_data:
        msg = update_data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '')
        user = msg.get('from', {})
        save_user(chat_id, user.get('username', ''), user.get('first_name', ''))
        handle_command(chat_id, text, {})

    return {"status": "ok"}
