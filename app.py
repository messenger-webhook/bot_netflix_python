from flask import Flask, request
import requests
import os

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAJ3CeIrHP4BPmTuzRmbnw1zDwTixMQK6JZBU2LOSKvW5dAPjoR7UkHGphnZBGTYF8ZBmWTQDavN23WGAfMNoSz0FJXmPDBUNxbC0haS4x3AkzhFOtb4zSDo0EoZADRTKLUM0CFQmRpqzXBHctBkby4sIy2AX46JSaIk6xheM3RGZCdZCZCLt9VM50GmZBAe7UFVnLVqZCYKd3oqQsfWCiD4Nszhs7ZBeYUADAxb6IVnoZD"

VERIFY_TOKEN = "b370b63a6cafa7a144131c8c079aca96"

@app.route('/webhook', methods=['GET'])
def verify():
    # Vérification du token
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Token invalide"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                sender_id = messaging_event["sender"]["id"]
                if messaging_event.get("message"):
                    message_text = messaging_event["message"].get("text")
                    send_message(sender_id, "Bonjour ! 🤖\n1️⃣ Est-ce que vous voulez renouveller ?\n2️⃣ Est-ce que vous voulez un code d'identification du compte ?")
    return "EVENT_RECEIVED", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v23.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(debug=True)
