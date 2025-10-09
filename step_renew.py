# step_renew.py
from utils import send_message, payment_buttons
import gspread
from datetime import datetime, timedelta

# ⚙️ Connexion à Google Sheets
gc = gspread.service_account(filename="credentials.json")
sh = gc.open("netnet")  # nom du fichier
ws = sh.worksheet("netnet1")  # nom de la feuille

def handle_renew(sender_id):
    """Demande l'email à renouveler."""
    send_message(sender_id, "🔁 يرجى إرسال الايميل الذي تريد تجديده 🆔")

def process_email(sender_id, email, duration_days):
    """
    Vérifie l'email dans la feuille, met à jour la date de fin, 
    puis envoie les instructions de paiement.
    """
    try:
        records = ws.get_all_records()
        for idx, record in enumerate(records, start=2):  # lignes Excel commencent à 2 si header
            if record["email"] == email:
                # mise à jour de la date
                old_date = datetime.strptime(record["date fin dinscription"], "%d/%m/%Y")
                new_date = old_date + timedelta(days=duration_days)
                ws.update(f"H{idx}", new_date.strftime("%d/%m/%Y"))
                
                # envoyer instructions de paiement
                text = f"يرجى ارسال وصل الدفع بريديموب او سيسيبي او صورة الشاشة إذا كان الدفع فليكسي للعميل: {record['nom client']}"
                payment_buttons(sender_id, text)
                return
        # si email non trouvé
        send_message(sender_id, "⚠️ الايميل غير موجود، يرجى التحقق والمحاولة مرة أخرى.")
    except Exception as e:
        send_message(sender_id, f"⚠️ حدث خطأ: {str(e)}")
