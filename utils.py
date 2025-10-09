# step_renew.py
from utils import send_message, payment_buttons
import gspread
from datetime import datetime, timedelta

# ⚙️ Connexion à Google Sheets
gc = gspread.service_account(filename="credentials.json")
sh = gc.open("netnet")  # nom du fichier
ws = sh.worksheet("netnet1")  # nom de la feuille

# dictionnaire pour stocker l'état temporaire des utilisateurs
user_state = {}  # {sender_id: {"email": "", "client": ""}}

def handle_renew(sender_id):
    """Demande l'email à renouveler."""
    send_message(sender_id, "🔁 يرجى إرسال الايميل الذي تريد تجديده 🆔")

def process_email(sender_id, email):
    """
    Vérifie l'email dans la feuille, sauvegarde le client, 
    puis demande la durée du renouvellement.
    """
    records = ws.get_all_records()
    for record in records:
        if record["email"] == email:
            # sauvegarde temporaire
            user_state[sender_id] = {"email": email, "client": record["nom client"]}
            
            # envoyer options de durée
            buttons = [
                {"type": "postback", "title": "1 شهر", "payload": "DURATION_30"},
                {"type": "postback", "title": "2 أشهر", "payload": "DURATION_60"},
                {"type": "postback", "title": "3 أشهر", "payload": "DURATION_90"},
            ]
            send_message(sender_id, f"💫 اختر عدد الأيام لتجديد الحساب للعميل {record['nom client']} 👇", buttons)
            return
    send_message(sender_id, "⚠️ الايميل غير موجود، يرجى التحقق والمحاولة مرة أخرى.")

def process_duration(sender_id, days):
    """
    Met à jour la date de fin inscription et demande le paiement.
    """
    if sender_id not in user_state:
        send_message(sender_id, "⚠️ يرجى إرسال الايميل أولاً.")
        return

    email = user_state[sender_id]["email"]
    client = user_state[sender_id]["client"]

    records = ws.get_all_records()
    for idx, record in enumerate(records, start=2):
        if record["email"] == email:
            # mise à jour date
            old_date = datetime.strptime(record["date fin dinscription"], "%d/%m/%Y")
            new_date = old_date + timedelta(days=days)
            ws.update(f"H{idx}", new_date.strftime("%d/%m/%Y"))

            # demander paiement
            text = f"يرجى ارسال وصل الدفع بريديموب او سيسيبي او صورة الشاشة إذا كان الدفع فليكسي للعميل: {client}"
            payment_buttons(sender_id, text)
            # nettoyage état
            del user_state[sender_id]
            return
    send_message(sender_id, "⚠️ حدث خطأ أثناء تحديث التاريخ.")
