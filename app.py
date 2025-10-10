# ======================
#   app.py
# ======================
import os
from flask import Flask, request
from dotenv import load_dotenv
from utils import send_message
from new_account import start_new_account, process_service_choice, confirm_new_account
from renew_account import start_renew, process_email, confirm_payment
from problem_account import handle_problem

# Charger les variables d’environnement
load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

app = Flask(__name__)

# =====================
# ✅ Vérification Webhook (GET)
# =====================
@app.route("/", methods=["GET"])
def verify_webhook():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token_sent == VERIFY_TOKEN:
        return str(challenge)
    return "Invalid verification token", 403


# =====================
# 💬 Réception des messages (POST)
# =====================
@app.route("/", methods=["POST"])
def receive_message():
    data = request.get_json()

    if "entry" not in data:
        return "no_entry", 200

    for entry in data["entry"]:
        if "messaging" not in entry:
            continue

        for event in entry["messaging"]:
            sender_id = event["sender"]["id"]

            # === Message texte ===
            if "message" in event and "text" in event["message"]:
                message_text = event["message"]["text"].strip().lower()
                process_text_message(sender_id, message_text)

            # === Bouton (postback) ===
            elif "postback" in event:
                payload = event["postback"]["payload"]
                process_postback(sender_id, payload)

    return "ok", 200


# =====================
# 🧠 Gestion du texte
# =====================
def process_text_message(user_id, message):
    if message in ["start", "bonjour", "salut", "menu"]:
        send_main_menu(user_id)

    elif "@" in message and "." in message:
        process_email(user_id, message)

    else:
        send_message(user_id, "📋 اكتب 'menu' لعرض الخيارات.")


# =====================
# 🖱️ Gestion des boutons
# =====================
def process_postback(user_id, payload):
    if payload == "START_NEW":
        start_new_account(user_id)

    elif payload == "START_RENEW":
        start_renew(user_id)

    elif payload == "START_PROBLEM":
        handle_problem(user_id)

    # === Achat compte ===
    elif payload.startswith("NEW_"):
        service_name = payload.replace("NEW_", "")
        process_service_choice(user_id, service_name)

    elif payload.startswith("PAY_BARIDI_"):
        service_name = payload.replace("PAY_BARIDI_", "")
        confirm_new_account(user_id, service_name, "BARIDI")

    elif payload.startswith("PAY_FLEXY_"):
        service_name = payload.replace("PAY_FLEXY_", "")
        confirm_new_account(user_id, service_name, "FLEXY")

    # === Renouvellement ===
    elif payload.startswith("CONFIRM_RENEW_"):
        row_index = int(payload.split("_")[-1])
        confirm_payment(user_id, row_index)

    elif payload == "CANCEL_RENEW":
        send_message(user_id, "❌ تم إلغاء التجديد.")

    else:
        send_message(user_id, "⚠️ أمر غير معروف.")


# =====================
# 📋 Menu principal
# =====================
def send_main_menu(user_id):
    text = "🎬 مرحبا بك في بوت NETNET\nاختر ما تريد 👇"
    buttons = [
        {"type": "postback", "title": "🛒 شراء حساب جديد", "payload": "START_NEW"},
        {"type": "postback", "title": "🔄 تجديد حسابك", "payload": "START_RENEW"},
        {"type": "postback", "title": "⚠️ مشكل في حسابك", "payload": "START_PROBLEM"},
    ]
    send_message(user_id, text, buttons)


# =====================
# 🚀 Lancement Flask
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
