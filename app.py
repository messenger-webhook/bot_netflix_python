from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "123456")

# ================================
# 🌐 Google Sheets setup
# ================================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("netnet").worksheet("netnet1")

# ================================
# 🧠 Suivi des utilisateurs
# ================================
user_state = {}  # {sender_id: {"action": "renew", "email": "", "duration": 30}}

# ================================
# 📨 Fonction d’envoi de message
# ================================
def send_message(recipient_id, message, buttons=None):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "messaging_type": "RESPONSE", "message": {"text": message}}

    if buttons:
        payload["message"] = {
            "attachment": {"type": "template", "payload": {"template_type": "button", "text": message, "buttons": buttons}}
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
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            print("✅ Vérification Webhook réussie !")
            return request.args.get("hub.challenge")
        return "Invalid verification token"

    data = request.get_json()
    print("📩 Webhook POST reçu :")
    print(data)

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
    # Si en renouvellement
    if sender_id in user_state and user_state[sender_id]["action"] == "renew" and "email" not in user_state[sender_id]:
        user_state[sender_id]["email"] = text.strip()
        check_email(sender_id, text.strip())
        return

    # Menu principal
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
    if payload == "ACHAT":
        buttons = [
            {"type": "postback", "title": "✅ Netflix", "payload": "NETFLIX"},
            {"type": "postback", "title": "✅ Shahid VIP", "payload": "SHAHID"},
            {"type": "postback", "title": "✅ Spotify", "payload": "SPOTIFY"},
        ]
        send_message(sender_id, "اختر الحساب الذي تريد من القائمة التالية 👇", buttons)

    elif payload in ["NETFLIX", "SHAHID", "SPOTIFY"]:
        send_prices(sender_id, payload)

    elif payload == "RENEW":
        user_state[sender_id] = {"action": "renew"}
        send_message(sender_id, "يرجى ارسال الايميل الذي تريد تجديده")

    elif payload.startswith("DURATION_"):
        days = int(payload.split("_")[1])
        update_renewal(sender_id, days)

    elif payload == "PROBLEM":
        send_message(sender_id, "⚠️ أرسل مشكلتك بالتفصيل وسنقوم بمساعدتك في أقرب وقت 🙏")

# ================================
# 💰 Prix & Paiement
# ================================
def send_prices(sender_id, service):
    prices = {
        "NETFLIX": "💫 أسعار Netflix :\nشهر 01 : 750 دج\nشهرين 02 : 1400 دج\nثلاث 03 أشهر : 2000 دج\nاختر طريقة الدفع 💳",
        "SHAHID": "💫 أسعار Shahid VIP :\nشهر 01 : 600 دج\nشهرين 02 : 1100 دج\nثلاث 03 أشهر : 1500 دج\nاختر طريقة الدفع 💳",
        "SPOTIFY": "💫 أسعار Spotify :\nشهر 01 : 600 دج\nشهرين 02 : 1100 دج\nثلاث 03 أشهر : 1500 دج\nاختر طريقة الدفع 💳",
    }
    buttons = [
        {"type": "postback", "title": "💸 بريدي موب / CCP", "payload": "PAY_BARIDI"},
        {"type": "postback", "title": "📱 فليكسي +20%", "payload": "PAY_FLEXY"},
    ]
    send_message(sender_id, prices[service], buttons)

# ================================
# 🔁 Renouvellement
# ================================
def check_email(sender_id, email):
    records = sheet.get_all_records()
    for row in records:
        if row["email"].strip() == email:
            user_state[sender_id]["row"] = row
            send_message(sender_id, f"الايميل موجود ✅\nاختر المدة التي تريد تجديدها")
            buttons = [
                {"type": "postback", "title": "شهر 01", "payload": "DURATION_30"},
                {"type": "postback", "title": "شهرين 02", "payload": "DURATION_60"},
                {"type": "postback", "title": "ثلاث 03 أشهر", "payload": "DURATION_90"},
            ]
            send_message(sender_id, "اختر المدة 👇", buttons)
            return
    send_message(sender_id, "❌ الايميل غير موجود، يرجى التأكد وإعادة الإرسال")

def update_renewal(sender_id, days):
    row = user_state[sender_id].get("row")
    if not row:
        send_message(sender_id, "❌ خطأ في العثور على الايميل")
        return

    # Calcul nouvelle date
    current_date = datetime.strptime(row["date fin dinscription"], "%d/%m/%Y")
    new_date = current_date + timedelta(days=days)
    row_index = sheet.find(row["email"]).row
    sheet.update_cell(row_index, 8, new_date.strftime("%d/%m/%Y"))

    send_message(sender_id, f"✅ تم تحديث الحساب لمدة {days} يوم\nيرجى ارسال وصل الدفع")
