import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

user_state = {}  # pour mémoriser l’état de chaque utilisateur

@app.route("/", methods=["GET"])
def home():
    return "Bot Messenger actif ✅"

# === Vérification du webhook ===
@app.route("/webhook", methods=["GET"])
def verify():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Erreur de vérification"

# === Réception des messages ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Event:", data)

    if "entry" in data:
        for entry in data["entry"]:
            if "messaging" in entry:
                for event in entry["messaging"]:
                    sender_id = event["sender"]["id"]

                    # Message texte reçu
                    if "message" in event and "text" in event["message"]:
                        message_text = event["message"]["text"]
                        handle_message(sender_id, message_text)

                    # Bouton (postback) cliqué
                    elif "postback" in event:
                        payload = event["postback"]["payload"]
                        handle_postback(sender_id, payload)
    return "ok", 200


# === Gestion des messages texte ===
def handle_message(sender_id, message_text):
    message_text = message_text.strip().lower()

    # Si c’est un nouveau client
    if sender_id not in user_state:
        send_main_menu(sender_id)
        user_state[sender_id] = "MAIN_MENU"

    # Si l’utilisateur écrit autre chose après
    else:
        send_text(sender_id, "الرجاء اختيار زر من الأزرار 👇")


# === Gestion des clics sur les boutons ===
def handle_postback(sender_id, payload):
    print(f"📦 Postback: {payload}")

    if payload == "ACHAT":
        send_achat_options(sender_id)
        user_state[sender_id] = "ACHAT"

    elif payload == "RENOUVELLEMENT":
        send_text(sender_id, "أرسل لنا اسم حسابك وسنقوم بتجديده ✅")

    elif payload == "PROBLEME":
        send_text(sender_id, "صف لنا مشكلتك وسنقوم بمساعدتك 🔧")

    elif payload in ["NETFLIX", "SHAHID", "SPOTIFY", "PRIME"]:
        send_price_list(sender_id, payload)

    elif payload in ["BARIDI", "CCP", "FLEXY"]:
        send_payment_details(sender_id, payload)

    else:
        send_main_menu(sender_id)


# === Fonctions d’envoi ===
def send_text(recipient_id, text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, json=payload)


def send_main_menu(recipient_id):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "مرحبا بكم في صفحتنا 👋\nهل تريد شراء حساب جديد؟\nهل تريد تجديد حسابك؟\nهل لديك مشكل في حسابك؟",
                    "buttons": [
                        {"type": "postback", "title": "شراء حساب جديد 🛒", "payload": "ACHAT"},
                        {"type": "postback", "title": "تجديد حساب ♻️", "payload": "RENOUVELLEMENT"},
                        {"type": "postback", "title": "مشكل في الحساب ⚠️", "payload": "PROBLEME"},
                    ],
                },
            }
        },
    }
    requests.post(url, json=payload)


def send_achat_options(recipient_id):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "اختر الحساب الذي تريد من قائمة الحسابات التالية 👇",
                    "buttons": [
                        {"type": "postback", "title": "Netflix ✅", "payload": "NETFLIX"},
                        {"type": "postback", "title": "Shahid VIP ✅", "payload": "SHAHID"},
                        {"type": "postback", "title": "Spotify ✅", "payload": "SPOTIFY"},
                        {"type": "postback", "title": "Prime Video ✅", "payload": "PRIME"},
                    ],
                },
            }
        },
    }
    requests.post(url, json=payload)


def send_price_list(recipient_id, service):
    prices = {
        "NETFLIX": """✅ Netflix
شهر: 750 دج (بريدي موب / CCP)
شهرين: 1400 دج
3 أشهر: 2000 دج
بالفليكسي: +20%""",
        "SHAHID": """✅ Shahid VIP
شهر: 600 دج (بريدي موب / CCP)
شهرين: 1100 دج
3 أشهر: 1500 دج
بالفليكسي: +20%""",
        "SPOTIFY": """✅ Spotify
شهر: 600 دج (بريدي موب / CCP)
شهرين: 1100 دج
3 أشهر: 1500 دج
بالفليكسي: +20%""",
        "PRIME": """✅ Prime Video
شهر: 600 دج (بريدي موب / CCP)
شهرين: 1100 دج
3 أشهر: 1500 دج
بالفليكسي: +20%""",
    }

    send_text(recipient_id, prices.get(service, "❌ الخدمة غير معروفة"))
    send_payment_methods(recipient_id)


def send_payment_methods(recipient_id):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "اختر طريقة الدفع 💳",
                    "buttons": [
                        {"type": "postback", "title": "بريدي موب", "payload": "BARIDI"},
                        {"type": "postback", "title": "CCP", "payload": "CCP"},
                        {"type": "postback", "title": "Flexy", "payload": "FLEXY"},
                    ],
                },
            }
        },
    }
    requests.post(url, json=payload)


def send_payment_details(recipient_id, method):
    methods = {
        "BARIDI": "💳 بريدي موب:\n00799999004386752747",
        "CCP": "📮 CCP:\n43867527 Clé 11",
        "FLEXY": "📱 Flexy:\n0654103330",
    }
    send_text(recipient_id, methods.get(method, "طريقة غير معروفة"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
