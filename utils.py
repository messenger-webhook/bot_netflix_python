# ======================
#   utils.py
# ======================
import os
import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
SHEET_NAME = os.getenv("SHEET_NAME", "NetflixBot")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME", "commandes")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "credentials.json")


# =====================
# 📤 Envoi de message Messenger
# =====================
def send_message(recipient_id, message_text, buttons=None):
    """Envoie un message simple ou avec boutons à Messenger"""
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    if buttons:
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": message_text,
                        "buttons": buttons,
                    },
                }
            },
        }
    else:
        payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("❌ Erreur envoi Messenger :", response.text)


# =====================
# 📊 Google Sheets : Ajouter ligne
# =====================
def append_to_sheet(data):
    """Ajoute une commande dans la feuille Google Sheets"""
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

        sheet.append_row([
            data.get("user_id"),
            data.get("service"),
            data.get("payment_type"),
            data.get("status"),
        ])

        print("✅ Ligne ajoutée dans Google Sheets")

    except Exception as e:
        print("❌ Erreur Google Sheets :", e)
