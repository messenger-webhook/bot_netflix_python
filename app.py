import os
import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN =EAAJ3CeIrHP4BPpEtPh7ZBsQDJWZAxuejcvZAgd1ZCqGt0LXAZCCJ4UjV0vslwUMxr4aRXpEFpaA2ZAPSb4Eg6e2HeTlGa0D2dqpDR2RFFZCLBMNtjjFVFXfBLvzheeB6YZAPuiaZCEOaeTZBi3HRZBNRA7GFGCeh20p18cH9u4hUfOu3rUBzPvGFVuEZAVdDZAbQcbFZCMMH664FMtTW7WRvgiuOm1hTAse8IiuRKtI5c7Djf2pwZDZD
VERIFY_TOKEN =b370b63a6cafa7a144131c8c079aca96  # ton verify_token

@app.route("/", methods=["GET"])
def home():
    return "Bot Messenger actif ✅"

# ✅ Vérification webhook
@app.route("/webhook", methods=["GET"])
def verify():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Erreur de vérification"

# ✅ Réception des messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Event reçu:", data)  # log Render
    
    if "entry" in data:
        for entry in data["entry"]:
            if "messaging" in entry:
                for event in entry["messaging"]:
                    if "message" in event and "text" in event["message"]:
                        sender_id = event["sender"]["id"]
                        message_text = event["message"]["text"]
                        print(f"Message de {sender_id}: {message_text}")
                        send_buttons(sender_id)  # Réponse avec boutons
    return "ok", 200

# ✅ Fonction pour envoyer des boutons
def send_buttons(recipient_id):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Bienvenue 👋 Choisis une option :",
                    "buttons": [
                        {"type": "postback", "title": "Voir produits 🛍", "payload": "PRODUITS"},
                        {"type": "postback", "title": "Contact 📞", "payload": "CONTACT"}
                    ]
                }
            }
        }
    }
    
    response = requests.post(url, json=payload)
    print("➡️ Réponse API:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
