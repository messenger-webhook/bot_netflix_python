import os
import requests
from flask import Flask, request

app = Flask(__name__)

# ✅ Charger les variables depuis .env / Render
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


@app.route("/", methods=["GET"])
def home():
    return "Bot Messenger actif ✅"


# ✅ Vérification Webhook (GET)
@app.route("/webhook", methods=["GET"])
def verify():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Erreur de vérification", 403


# ✅ Réception des messages (POST)
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Event brut:", data, flush=True)  # log complet Render

    if "entry" in data:
        for entry in data["entry"]:
            # Cas normal: un utilisateur envoie un message
            if "messaging" in entry:
                for event in entry["messaging"]:
                    if "message" in event and "text" in event["message"]:
                        sender_id = event["sender"]["id"]
                        message_text = event["message"]["text"]
                        print(f"💬 Message reçu de {sender_id}: {message_text}", flush=True)
                        send_buttons(sender_id)

            # Cas d'autres events (ex: page, posts, etc.)
            if "changes" in entry:
                print("🔄 Event changes:", entry["changes"], flush=True)

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
    print("➡️ Réponse API:", response.status_code, response.text, flush=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
