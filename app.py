from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = "b370b63a6cafa7a144131c8c079aca96"
PAGE_ACCESS_TOKEN = "EAAJ3CeIrHP4BPkx3teShpZBiL1aKpfi9Jb..."  # remplace par ton token

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token_sent == VERIFY_TOKEN:
            return challenge, 200
        return "Invalid verification token", 403
    else:
        data = request.get_json()
        print("Message reçu :", data)

        if "entry" in data:
            for entry in data["entry"]:
                for messaging_event in entry.get("messaging", []):
                    sender_id = messaging_event["sender"]["id"]
                    if "message" in messaging_event:
                        message_text = messaging_event["message"].get("text")
                        if message_text:
                            send_message(sender_id, f"Vous avez écrit : {message_text}")

        return "EVENT_RECEIVED", 200

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v23.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    r = requests.post(url, json=payload)
    print("Réponse API Messenger :", r.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
