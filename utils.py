import os
import requests
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

# === CONFIG ===
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")

# === Google Sheets ===
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
    return sheet


# === Messenger ===
def send_message(recipient_id, text, buttons=None):
    """Envoie un message Messenger simple ou avec boutons"""
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    if buttons:
        payload["message"] = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": buttons
                }
            }
        }

    response = requests.post(
        f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}",
        json=payload
    )
    return response.status_code


def find_account_by_email(email):
    """Recherche une ligne dans la feuille Google par email"""
    sheet = get_sheet()
    data = sheet.get_all_records()
    for i, row in enumerate(data, start=2):
        if str(row.get("email", "")).strip().lower() == email.strip().lower():
            return i, row
    return None, None


def update_payment_status(row_index, paid=True):
    """Met à jour la colonne 'payer'"""
    sheet = get_sheet()
    sheet.update_cell(row_index, 6, "oui" if paid else "non")
    return True
