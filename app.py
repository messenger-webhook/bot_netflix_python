from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()
app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

# ================================
# 📨 Fonction d’envoi de message
# ================================
def send_message(recipient_id, message, buttons=None):
    """Envoi d’un message texte ou message avec boutons."""
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}

    if buttons:
        payload = {
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": message,
                        "buttons": buttons
                    }
                }
            }
        }
    else:
        payload = {
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "message": {"text": message}
        }

    print(f"📤 Envoi à {recipient_id} → {message[:40]}...")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("⚠️ Erreur envoi :", response.text)

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

    # POST (messages et événements)
    data = request.get_json()
    print("📩 Webhook POST reçu :")
    print(data)

    if not data or "entry" not in data:
        return "ok"

    for entry in data["entry"]:
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]

            # Gestion postback (boutons)
            if "postback" in event:
                payload = event["postback"]["payload"]
                print(f"🔥 Postback reçu : {payload}")
                handle_postback(sender_id, payload)

            # Gestion message texte
            elif "message" in event and "text" in event["message"]:
                handle_message(sender_id, event["message"]["text"])

    return "ok"

# ================================
# 🧠 Gestion des messages texte
# ================================
def handle_message(sender_id, text):
    """Affiche le menu principal."""
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
    """Réagit aux clics sur les boutons."""
    if payload == "ACHAT":
        buttons = [
            {"type": "postback", "title": "📺 Netflix", "payload": "NETFLIX"},
            {"type": "postback", "title": "🎥 Shahid VIP", "payload": "SHAHID"},
            {"type": "postback", "title": "🎧 Spotify", "payload": "SPOTIFY"},
            {"type": "postback", "title": "🎬 Prime Video", "payload": "PRIME"},
        ]
        send_message(sender_id, "📦 اختر الحساب الذي تريد من القائمة التالية 👇", buttons)

    elif payload in ["NETFLIX", "SHAHID", "SPOTIFY", "PRIME"]:
        show_prices(sender_id, payload)

    elif payload == "PAY_BARIDI":
        send_message(sender_id, "🏦 الدفع عبر بريدي موب / CCP :\n\nبريدي موب : 00799999004386752747\nCCP : 43867527 clé 11")

    elif payload == "PAY_FLEXY":
        send_message(sender_id, "📱 الدفع عبر فليكسي :\n\nالرقم : 0654103330")

    elif payload == "RENEW":
        send_message(sender_id, "🔁 أرسل رقم الحساب الذي تريد تجديده 🆔")

    elif payload == "PROBLEM":
        send_message(sender_id, "⚠️ أرسل مشكلتك بالتفصيل وسنقوم بمساعدتك في أقرب وقت 🙏")

# ================================
# 💰 Tarifs par service
# ================================
def show_prices(sender_id, service):
    """Affiche les prix selon le service choisi."""
    if service == "NETFLIX":
        title = "💫 أسعار Netflix :"
    elif service == "SHAHID":
        title = "💫 أسعار Shahid VIP :"
    elif service == "SPOTIFY":
        title = "💫 أسعار Spotify :"
    else:
        title = "💫 أسعار Prime Video :"

    text = f"""{title}

شهر 01 بالبريدي موب أو CCP : 750 دج
شهر 01 بالفليكسي : 890 دج

شهرين 02 بالبريدي موب أو CCP : 1400 دج
شهرين 02 بالفليكسي : 1790 دج

ثلاث 03 أشهر بالبريدي موب أو CCP : 2000 دج
ثلاث 03 أشهر بالفليكسي : 2590 دج

اختر طريقة الدفع 💳"""
    payment_buttons(sender_id, text)

# ================================
# 💳 Boutons de paiement
# ================================
def payment_buttons(sender_id, text):
    buttons = [
        {"type": "postback", "title": "💸 بريدي موب / CCP", "payload": "PAY_BARIDI"},
        {"type": "postback", "title": "📱 فليكسي +20%", "payload": "PAY_FLEXY"},
    ]
    send_message(sender_id, text, buttons)

# ================================
# 🚀 Lancement serveur
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
