import os
import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_secret_token_123")

@app.route("/", methods=["GET"])
def home():
    return "Bot is running successfully!", 200

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return str(challenge), 200
        else:
            return 'Verification failed', 403
    return 'Hello World', 200

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.get_json()
    if data and data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                
                # التحقق إذا كانت رسالة نصية مرسلة من المستخدم
                if sender_id and messaging_event.get("message") and messaging_event["message"].get("text"):
                    message_text = messaging_event["message"]["text"]
                    print(f"Received message from {sender_id}: {message_text}")
                    
                    # إرسال رد تلقائي من المارد السحري
                    send_message(sender_id, "أهلاً بك! أنا المارد السحري 🧞‍♂️، هل نبدأ اللعبة؟")
                    
    return "EVENT_RECEIVED", 200

def send_message(recipient_id, text_message):
    if not PAGE_ACCESS_TOKEN:
        print("Error: PAGE_ACCESS_TOKEN is missing!")
        return
        
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text_message}
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Send message response: {response.status_code}, {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
