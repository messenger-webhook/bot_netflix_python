from flask import Flask, request
import requests
import json

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAJ3CeIrHP4BP…ton_token…"
VERIFY_TOKEN = "b370b63a6cafa7a144131c8c079aca96"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Vérification de Facebook
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token_sent == VERIFY_TOKEN:
            return challenge
        return "Token incorrect", 403

    if request.method == 'POST':
        # Gestion des messages reçus
        output = request.get_json()
        print("Webhook reçu:", json.dumps(output, indent=2))

        for entry in output.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event['sender']['id']

                if 'message' in messaging_event and 'text' in messaging_event['message']:
                    message_text = messaging_event['message']['text']
                    print(f"Message reçu de {sender_id}: {message_text}")
                    # Répond automatiquement
                    send_message(sender_id, f"Tu as envoyé : {message_text}")

        return "EVENT_RECEIVED", 200

def send_message(recipient_id, message_text):
    """Envoie un message à l'utilisateur via l'API Messenger"""
    url = f"https://graph.facebook.com/v23.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Réponse FB:", response.text)

if __name__ == '__main__':
    app.run(debug=True)
