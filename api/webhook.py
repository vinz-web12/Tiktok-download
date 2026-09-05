import os
import json
import sys
import importlib.util

# Add parent directory to path so we can import bot.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from bot import process_update

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update_data = request.get_json()
        if not update_data:
            return jsonify({"status": "error"}), 400

        # Proses update pake bot.py
        result = process_update(update_data)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot aktif di Vercel!"

# Vercel expects 'app' as the WSGI application
app = app  # Vercel needs this
