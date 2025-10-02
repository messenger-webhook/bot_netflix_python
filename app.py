from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Token de vérification pour Messenger
VERIFY_TOKEN = "b370b63a6cafa7a144131c8c079aca96"

# Token de la page Messenger
PAGE_ACCESS_TOKEN = "EAAJ3CeIrHP4BPkmTykfsp98jBQgxH58Vw2dMq1eGs8lhabQT08REtqN5TFiZAOzsFTi2qjgtda0Dxk14gNlwsUndIRhJBY80OzJ9b7zqF2hGDZAQn3f5qJn1LD6D5F841ax21i4l5c7kQxLuZBvaFDsTZCByv3HrOUYblId3dX3nS0OUdIRTDkgsANiKeUPhfiC0uGp6ZBJQZAPeCnN4Fq3cUYLAWy37bFj0CynGJdaAZDZD"

# Fonction pour envoyer un message via Messenger
def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v23.0/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    headers = {"Content-Type": "application/json"}
    params = {"access_token": PAGE_ACCESS_TOKEN}
    response = requests.post(url, json=payload, headers=headers, params=params)
    return response.json()

# Webhook GET/POST
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
        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    sender_id = messaging_event["sender"]["id"]
                    if "message" in messaging_event and "text" in messaging_event["message"]:
                        message_text = messaging_event["message"]["text"]
                        # Réponse automatique
                        send_message(sender_id, f"Tu as dit : {message_text}")
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
