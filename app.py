import os
import requests
from flask import Flask, request

app = Flask(__name__)

# === CONFIG ===
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "EAAJ3CeIrHP4BPhymft5rdKlggOKxJB8CYVHqY4fPPD2wrZBJ5XM6PqWiZBIa7sZCaZChGVIpCZBlGurZCpXJgDdoZCGJGl6UMSdSRZBUCIgwjxZAZCECpm0Ryit9ZByvOkk99Pv2dZB1FR7joOjus0oEwJxCIYwY2aOUBx5wQVnNcZAWGeIDpvl4wdkNGYtbqH7PxGl2VfOUZD")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "123456")


# === ENVOI MESSAGE ===
def send_message(recipient_id, message_data):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    response = requests.post(url, json={
        "recipient": {"id": recipient_id},
        "message": message_data
    })
    if response.status_code != 200:
        print(f"Erreur envoi message: {response.status_code} - {response.text}")
    else:
        print(f"Message envoyé à {recipient_id}: {message_data}")


# === MESSAGE TEXTE SIMPLE ===
def send_text(recipient_id, text):
    send_message(recipient_id, {"text": text})


# === MENU PRINCIPAL ===
def send_main_menu(recipient_id):
    buttons = [
        {"type": "postback", "title": "🛒 شراء حساب جديد", "payload": "BUY_ACCOUNT"},
        {"type": "postback", "title": "📞 تواصل معنا", "payload": "CONTACT"},
        {"type": "postback", "title": "ℹ️ معلومات", "payload": "INFO"}
    ]
    message = {
        "attachment": {
            "type": "template",
            "payload": {"template_type": "button", "text": "مرحبًا 👋 اختر من القائمة:", "buttons": buttons}
        }
    }
    send_message(recipient_id, message)


# === ROUTE DE VÉRIFICATION DU WEBHOOK ===
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    verify_token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if verify_token == VERIFY_TOKEN:
        print("✅ Webhook vérifié avec succès !")
        return challenge
    else:
        print("❌ Échec de la vérification du webhook.")
        return "Token invalide", 403


# === TRAITEMENT DES ÉVÉNEMENTS ===
@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.get_json()
    print("📩 Reçu :", data)

    if "entry" in data:
        for entry in data["entry"]:
            if "messaging" in entry:
                for event in entry["messaging"]:
                    sender_id = event["sender"]["id"]

                    # ⚠️ Ignorer les échos (messages envoyés par le bot lui-même)
                    if event.get("message") and event["message"].get("is_echo"):
                        print("↩️ Message écho ignoré.")
                        continue

                    # --- Message texte reçu ---
                    if "message" in event and "text" in event["message"]:
                        message_text = event["message"]["text"].strip()
                        print(f"👤 Message reçu de {sender_id}: {message_text}")

                        if message_text in ["start", "bonjour", "سلام", "menu", "hello"]:
                            send_main_menu(sender_id)
                        else:
                            send_text(sender_id, "🌟 مرحبًا! اكتب 'menu' لعرض الخيارات.")

                    # --- Postback (bouton cliqué) ---
                    elif "postback" in event:
                        payload = event["postback"]["payload"]
                        print(f"🖱️ Postback reçu: {payload}")

                        if payload == "BUY_ACCOUNT":
                            send_text(sender_id, "ختر الحساب الذي تريد من القائمة التالية...")
                        elif payload == "CONTACT":
                            send_text(sender_id, "📞 تواصل معنا عبر صفحتنا على الفيسبوك.")
                        elif payload == "INFO":
                            send_text(sender_id, "ℹ️ نحن نوفر حسابات بأسعار جد مغرية!")
                        else:
                            send_text(sender_id, "❓ خيار غير معروف.")
    return "OK", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
