from utils import get_sheet_data, update_sheet_row
from app import send_message

def start_renew(sender_id):
    """Démarre le processus de renouvellement en demandant l'email"""
    send_message(sender_id, "🔁 يرجى إرسال الايميل الذي تريد تجديده 🆔")

def process_email(sender_id, email):
    """Vérifie l'email dans Google Sheets"""
    rows = get_sheet_data()
    for i, row in enumerate(rows):
        if row.get("email") == email:
            send_message(sender_id, f"✅ Email trouvé : {row['nom client']}.\nCombien de jours voulez-vous ajouter ?")
            return row
    send_message(sender_id, "❌ Email introuvable, veuillez réessayer.")
    return None

def confirm_payment(admin_id, client_name, days, sheet_row):
    """Envoie un message à l'admin pour confirmer le paiement"""
    text = f"📩 Nouveau renouvellement : {client_name}\nDurée : {days} jours\nConfirmez-vous le paiement ?"
    buttons = [
        {"type": "postback", "title": "✅ Oui", "payload": f"CONFIRM_RENEW_{sheet_row['email']}"},
        {"type": "postback", "title": "❌ Non", "payload": "CANCEL_RENEW"},
    ]
    send_message(admin_id, text, buttons)

def finalize_renew(sheet_row, days):
    """Ajoute les jours au compte dans Google Sheets"""
    from datetime import datetime, timedelta
    old_date_str = sheet_row.get("date fin dinscription")
    old_date = datetime.strptime(old_date_str, "%d/%m/%Y")
    new_date = old_date + timedelta(days=days)
    update_sheet_row(sheet_row_index=sheet_row["index"], column_name="date fin dinscription", value=new_date.strftime("%d/%m/%Y"))

