from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Ton token d'accès Facebook Page
PAGE_ACCESS_TOKEN = "EAAJ3CeIrHP4BPkmTykfsp98jBQgxH58Vw2dMq1eGs8lhabQT08REtqN5TFiZAOzsFTi2qjgtda0Dxk14gNlwsUndIRhJBY80OzJ9b7zqF2hGDZAQn3f5qJn1LD6D5F841ax21i4l5c7kQxLuZBvaFDsTZCByv3HrOUYblId3dX3n0OUdIRTDkgsANiKeUPhfiC0uGp6ZBJQZAPeCnN4Fq3cUYLAWy37bFj0CynGJdaAZDZD"

# Fonction pour envoyer un message
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v23.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload)
    return response.json()

# Webhook de vérification
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    VERIFY_TOKEN = "b370b63a6cafa7a144131c8c079aca96"
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge
    return "Erreur de vérification", 403

# Webhook de réception des messages
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data['object'] == "page":
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event['sender']['id']
                # Ici tu peux personnaliser la réponse automatique
                reply = ("Bonjour ! \n"
                         "1️⃣ Voulez-vous renouveler votre abonnement ?\n"
                         "2️⃣ Voulez-vous un code d'identification du compte ?")
                send_message(sender_id, reply)
    return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    app.run(debug=True)
