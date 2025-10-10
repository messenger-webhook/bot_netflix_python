import os
import json
import requests
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# === Charger les variables d'environnement (.env ou Render) ===
load_dotenv()

# ============================================
# 🔐 Connexion à Google Sheets via Service Account
# ============================================
def get_sheet():
    """
    Connexion sécurisée à Google Sheets via JSON dans la variable d'environnement GOOGLE_CREDENTIALS.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials_json = os.getenv("GOOGLE_CREDENTIALS")

        if not credentials_json:
            raise Exception("❌ GOOGLE_CREDENTIALS non trouvé dans les variables d'environnement.")

        credentials_dict = json.loads(credentials_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("netnet").sheet1
        return sheet
    except Exception as e:
        print("Erreur lors de la connexion à Google Sheets:", e)
        raise

# ============================================
# 🔍 Recherche d’un compte par email
# ============================================
def find_account_by_email(sheet, email):
    """
    Recherche un compte dans la feuille Google Sheets à partir de l'email.
    Retourne (index_ligne, données) si trouvé, sinon (None, None).
    """
    try:
        records = sheet.get_all_records()
        for i, record in enumerate(records, start=2):  # ligne 1 = en-têtes
            if str(record.get("email", "")).strip().lower() == email.strip().lower():
                return i, record
        return None, None
    except Exception as e:
        print("Erreur dans find_account_by_email:", e)
        return None, None

# ============================================
# 📨 Envoi de message à Messenger
# ============================================
def send_message(user_id, text, buttons=None):
    """
    Envoie un message texte ou avec boutons au user Messenger.
    """
    PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

    if not PAGE_ACCESS_TOKEN:
        print("❌ PAGE_ACCESS_TOKEN manquant.")
        return

    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    if buttons:
        payload = {
            "recipient": {"id": user_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {"template_type": "button", "text": text, "buttons": buttons},
                }
            },
        }
    else:
        payload = {"recipient": {"id": user_id}, "message": {"text": text}}

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"⚠️ Erreur d’envoi à Messenger: {response.text}")

# ============================================
# 💰 Mise à jour du statut de paiement
# ============================================
def update_payment_status(sheet, row_index, status):
    """
    Met à jour le statut du paiement dans la feuille (colonne 'payer').
    """
    try:
        sheet.update_cell(row_index, 5, status)
    except Exception as e:
        print("Erreur dans update_payment_status:", e)

# ============================================
# 💬 Aide : boutons de paiement
# ============================================
def payment_buttons(sender_id, text):
    """
    Envoie les boutons de choix du mode de paiement.
    """
    buttons = [
        {"type": "postback", "title": "🏦 بريدي موب / CCP", "payload": "PAY_BARIDI"},
        {"type": "postback", "title": "📱 فليكسي", "payload": "PAY_FLEXY"},
    ]
    send_message(sender_id, text, buttons)
