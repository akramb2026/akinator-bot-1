import os
import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "YOUR_PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_verify_token")

CHARACTERS = [
    {"name": "ميسي", "gender": "male", "real": True, "football": True, "barcelona": True, "image": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Lionel_Messi_2018.jpg"},
    {"name": "رونالدو", "gender": "male", "real": True, "football": True, "barcelona": False, "image": "https://upload.wikimedia.org/wikipedia/commons/8/8c/Cristiano_Ronaldo_2018.jpg"},
    {"name": "سبونج بوب", "gender": "male", "real": False, "football": False, "barcelona": False, "image": "https://upload.wikimedia.org/wikipedia/en/3/3b/SpongeBob_SquarePants_character.svg"},
    {"name": "غوكو", "gender": "male", "real": False, "football": False, "barcelona": False, "image": "https://upload.wikimedia.org/wikipedia/en/a/af/Son_Goku_Goku.png"}
]

QUESTIONS = [
    {"id": "gender", "text": "هل الشخصية حقيقية أم خيالية؟", "options": [{"label": "حقيقية", "val": True}, {"label": "خيالية", "val": False}]},
    {"id": "football", "text": "هل الشخصية تلعب كرة القدم؟", "options": [{"label": "نعم", "val": True}, {"label": "لا", "val": False}]},
    {"id": "barcelona", "text": "هل لعبت الشخصية لنادي برشلونة؟", "options": [{"label": "نعم", "val": True}, {"label": "لا", "val": False}]}
]

user_sessions = {}

def send_message(sender_id, text, quick_replies=None):
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": text}
    }
    if quick_replies:
        payload["message"]["quick_replies"] = [
            {
                "content_type": "text",
                "title": opt["label"],
                "payload": str(opt["val"])
            } for opt in quick_replies
        ]
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json=payload)

def send_image(sender_id, image_url):
    payload = {
        "recipient": {"id": sender_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": image_url, "is_reusable": True}
            }
        }
    }
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json=payload)

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Bot is running on Render successfully!", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                
                if messaging_event.get("message"):
                    message = messaging_event["message"]
                    text = message.get("text", "").strip()
                    quick_reply = message.get("quick_reply")
                    
                    if text.lower() in ["ابدأ", "ابدا", "start"]:
                        user_sessions[sender_id] = {"step": 0, "filters": {}}
                        q = QUESTIONS[0]
                        send_message(sender_id, f"أهلاً بك في لعبة أكيناتور! 🧞‍♂️\n\nالسؤال الأول: {q['text']}", q["options"])
                        continue

                    if sender_id not in user_sessions:
                        send_message(sender_id, "أهلاً بك! أرسل كلمة 'ابدأ' لنبدأ اللعبة معاُ 🧞‍♂️")
                        continue

                    session = user_sessions[sender_id]
                    step = session["step"]

                    if quick_reply:
                        ans_val = quick_reply.get("payload") == "True"
                        current_q_id = QUESTIONS[step]["id"]
                        session["filters"][current_q_id] = ans_val
                        session["step"] += 1

                        if session["step"] < len(QUESTIONS):
                            next_q = QUESTIONS[session["step"]]
                            send_message(sender_id, f"السؤال {session['step']+1}: {next_q['text']}", next_q["options"])
                        else:
                            candidates = CHARACTERS
                            for k, v in session["filters"].items():
                                candidates = [c for c in candidates if c.get(k) == v]
                            
                            if candidates:
                                char = candidates[0]
                                send_message(sender_id, f"الشخصية التي تفكر بها هي: {char['name']}! 🎉")
                                send_image(sender_id, char["image"])
                            else:
                                send_message(sender_id, "لم أستطع تخمين الشخصية هذه المرة! 🤔")
                            
                            del user_sessions[sender_id]

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
