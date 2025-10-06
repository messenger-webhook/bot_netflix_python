from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

# ================================
# 📨 Fonction d’envoi de message
# ================================
def send_message(recipient_id, message, buttons=None):
    """Envoi d’un message texte ou message avec boutons."""
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "messaging_type": "RESPONSE",
        "message": {"text": message}
    }

    if buttons:
        payload["message"] = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": message,
                    "buttons": buttons
                }
            }
        }

    print(f"📤 Envoi à {recipient_id} → {message[:40]}...")
    requests.post(url, json=payload)


# ================================
# 🌐 Webhook Messenger
# ================================
@app.route("/", methods=["GET", "POST"])
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = "123456"
        if request.args.get("hub.verify_token") == verify_token:
            print("✅ Vérification Webhook réussie !")
            return request.args.get("hub.challenge")
        return "Invalid verification token"

    # Requête POST (message ou bouton)
    data = request.get_json()
    print("📩 Webhook POST reçu :")
    print(data)

    if not data or "entry" not in data:
        print("⚠️ Données webhook invalides")
        return "ok"

    for entry in data["entry"]:
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]

            if "postback" in event:
                payload = event["postback"]["payload"]
                print(f"🔥 Postback reçu : {payload}")
                handle_postback(sender_id, payload)

            elif "message" in event and "text" in event["message"]:
                print(f"💬 Message texte reçu : {event['message']['text']}")
                handle_message(sender_id, event["message"]["text"])

    return "ok"


# ================================
# 🧠 Gestion des messages
# ================================
def handle_message(sender_id, text):
    """Affiche le menu principal quand un utilisateur écrit."""
    welcome_buttons = [
        {"type": "postback", "title": "🛒 شراء حساب جديد", "payload": "ACHAT"},
        {"type": "postback", "title": "🔄 تجديد حسابك", "payload": "RENEW"},
        {"type": "postback", "title": "⚠️ مشكل في حسابك", "payload": "PROBLEM"},
    ]
    send_message(sender_id, "مرحبا بكم في صفحتنا ❤️", welcome_buttons)


# ================================
# 🎯 Gestion des boutons
# ================================
def handle_postback(sender_id, payload):
    """Gère les clics sur les boutons du bot Messenger."""

    if payload == "ACHAT":
        buttons = [
            {"type": "postback", "title": "✅ Netflix", "payload": "NETFLIX"},
            {"type": "postback", "title": "✅ Shahid VIP", "payload": "SHAHID"},
            {"type": "postback", "title": "✅ Spotify", "payload": "SPOTIFY"},
            {"type": "postback", "title": "✅ Prime Video", "payload": "PRIME"},
        ]
        send_message(sender_id, "اختر الحساب الذي تريد من القائمة التالية 👇", buttons)

    elif payload == "NETFLIX":
        text = """💫 أسعار Netflix :
شهر 01 بالبريدي موب أو CCP : 750 دج
شهر 01 بالفليكسي : 890 دج

شهرين 02 بالبريدي موب أو CCP : 1400 دج
شهرين 02 بالفليكسي : 1790 دج

ثلاث 03 أشهر بالبريدي موب أو CCP : 2000 دج
ثلاث 03 أشهر بالفليكسي : 2590 دج

اختر طريقة الدفع 💳"""
        payment_buttons(sender_id, text)

    elif payload == "SHAHID":
        text = """💫 أسعار Shahid VIP :
شهر 01 بالبريدي موب أو CCP : 600 دج
شهر 01 بالفليكسي : 750 دج

شهرين 02 بالبريدي موب أو CCP : 1100 دج
شهرين 02 بالفليكسي : 1300 دج

ثلاث 03 أشهر بالبريدي موب أو CCP : 1500 دج
ثلاث 03 أشهر بالفليكسي : 1800 دج

اختر طريقة الدفع 💳"""
        payment_buttons(sender_id, text)

    elif payload == "SPOTIFY":
        text = """💫 أسعار Spotify :
شهر 01 بالبريدي موب أو CCP : 600 دج
شهر 01 بالفليكسي : 750 دج

شهرين 02 بالبريدي موب أو CCP : 1100 دج
شهرين 02 بالفليكسي : 1300 دج

ثلاث 03 أشهر بالبريدي موب أو CCP : 1500 دج
ثلاث 03 أشهر بالفليكسي : 1800 دج

اختر طريقة الدفع 💳"""
        payment_buttons(sender_id, text)

    elif payload == "PRIME":
        text = """💫 أسعار Prime Video :
شهر 01 بالبريدي موب أو CCP : 600 دج
شهر 01 بالفليكسي : 750 دج

شهرين 02 بالبريدي موب أو CCP : 1100 دج
شهرين 02 بالفليكسي : 1300 دج

ثلاث 03 أشهر بالبريدي موب أو CCP : 1500 دج
ثلاث 03 أشهر بالفليكسي : 1800 دج

اختر طريقة الدفع 💳"""
        payment_buttons(sender_id, text)

    elif payload == "PAY_BARIDI":
        send_message(sender_id, """🏦 معلومات الدفع :
بريدي موب : 00799999004386752747
CCP : 43867527 clé 11""")

    elif payload == "PAY_FLEXY":
        send_message(sender_id, """📱 فليكسي :
الرقم : 0654103330""")

    elif payload == "RENEW":
        send_message(sender_id, "🔁 يرجى إرسال رقم الحساب الذي تريد تجديده 🆔")

    elif payload == "PROBLEM":
        send_message(sender_id, "⚠️ أرسل مشكلتك بالتفصيل وسنقوم بمساعدتك في أقرب وقت 🙏")


# ================================
# 💳 Boutons de paiement
# ================================
def payment_buttons(sender_id, text):
    """Envoie les boutons de paiement (Baridi / Flexy)."""
    buttons = [
        {"type": "postback", "title": "💸 بريدي موب / CCP", "payload": "PAY_BARIDI"},
        {"type": "postback", "title": "📱 فليكسي +20%", "payload": "PAY_FLEXY"},
    ]
    send_message(sender_id, text, buttons)


# ================================
# 🚀 Lancement du serveur
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
