from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from step_renew import start_renew, process_email, confirm_payment, finalize_renew

load_dotenv()
app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
ADMIN_ID = "24512169588466775"  # Ton ID admin Messenger

# ================================
# 📨 Fonction d’envoi de message
# ================================
def send_message(recipient_id, message, buttons=None):
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

    data = request.get_json()
    print("📩 Webhook POST reçu :", data)

    if not data or "entry" not in data:
        return "ok"

    for entry in data["entry"]:
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]

            if "postback" in event:
                payload = event["postback"]["payload"]
                handle_postback(sender_id, payload)

            elif "message" in event and "text" in event["message"]:
                handle_message(sender_id, event["message"]["text"])

    return "ok"

# ================================
# 🧠 Gestion des messages
# ================================
def handle_message(sender_id, text):
    """Menu principal + réponses selon l'étape"""
    # Si l'utilisateur est en mode renouvellement
    if text.endswith("@renew"):
        # text = email@renew
        email = text.replace("@renew", "").strip()
        sheet_row = process_email(sender_id, email)
        if sheet_row:
            send_message(sender_id, "Combien de jours voulez-vous ajouter ? (ex: 30)")
            # On stocke temporairement l'email et l'étape
            temp_user_state[sender_id] = {"step": "choose_days", "email": email, "sheet_row": sheet_row}
        return

    # Si l'utilisateur choisit les jours à ajouter
    if sender_id in temp_user_state and temp_user_state[sender_id]["step"] == "choose_days":
        try:
            days = int(text)
            temp_user_state[sender_id]["days"] = days
            sheet_row = temp_user_state[sender_id]["sheet_row"]
            confirm_payment(ADMIN_ID, sheet_row["nom client"], days, sheet_row)
            temp_user_state[sender_id]["step"] = "waiting_admin"
        except:
            send_message(sender_id, "❌ Veuillez entrer un nombre valide de jours.")
        return

    # Menu principal classique
    welcome_buttons = [
        {"type": "postback", "title": "🛒 شراء حساب جديد", "payload": "ACHAT"},
        {"type": "postback", "title": "🔄 تجديد حسابك", "payload": "RENEW"},
        {"type": "postback", "title": "⚠️ مشكل في حسابك", "payload": "PROBLEM"},
    ]
    send_message(sender_id, "مرحبا بكم في صفحتنا ❤️", welcome_buttons)

# ================================
# 🔄 Gestion des boutons
# ================================
def handle_postback(sender_id, payload):
    # ---------- Achat ----------
    if payload == "ACHAT":
        buttons = [
            {"type": "postback", "title": "✅ Netflix", "payload": "NETFLIX"},
            {"type": "postback", "title": "✅ Shahid VIP", "payload": "SHAHID"},
            {"type": "postback", "title": "✅ Spotify", "payload": "SPOTIFY"},
        ]
        send_message(sender_id, "اختر الحساب الذي تريد من القائمة التالية 👇", buttons)

    # ---------- Renouvellement ----------
    elif payload == "RENEW":
        start_renew(sender_id)

    # ---------- Problème ----------
    elif payload == "PROBLEM":
        send_message(sender_id, "⚠️ أرسل مشكلتك بالتفصيل وسنقوم بمساعدتك في أقرب وقت 🙏")

    # ---------- Paiement ----------
    elif payload.startswith("PAY_"):
        if payload == "PAY_BARIDI":
            send_message(sender_id, "🏦 معلومات الدفع :\nبريدي موب : 00799999004386752747\nCCP : 43867527 clé 11")
        elif payload == "PAY_FLEXY":
            send_message(sender_id, "📱 فليكسي : الرقم : 0654103330")

    # ---------- Confirmation admin ----------
    elif payload.startswith("CONFIRM_RENEW_"):
        email = payload.replace("CONFIRM_RENEW_", "")
        # On récupère les infos temporaires
        for user_id, state in temp_user_state.items():
            if state.get("email") == email:
                finalize_renew(state["sheet_row"], state["days"])
                send_message(user_id, f"✅ التجديد تم بنجاح! تم إضافة {state['days']} يوم.")
                send_message(ADMIN_ID, f"✅ التجديد للعميل {state['sheet_row']['nom client']} تم.")
                del temp_user_state[user_id]

    elif payload == "CANCEL_RENEW":
        send_message(ADMIN_ID, "❌ التجديد تم إلغاؤه.")

# ================================
# 🌟 Stockage temporaire des utilisateurs
# ================================
temp_user_state = {}

# ================================
# 🚀 Lancement du serveur
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
