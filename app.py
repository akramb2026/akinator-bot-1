import os
import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")

@app.route("/", methods=["GET"])
def home():
    return "Bot is running successfully!", 200

# 1. التحقق المباشر والربط السريع مع Webhook الفيسبوك
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    challenge = request.args.get('hub.challenge')
    if challenge:
        return str(challenge), 200
    return 'Webhook Active', 200

# 2. استقبال الأحداث والرسائل من فيسبوك
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.get_json()
    if data and data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                print(f"Received message from {sender_id}")
    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
