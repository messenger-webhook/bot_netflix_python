from utils import send_message, find_account_by_email, update_payment_status
import datetime

def start_renew(user_id):
    send_message(user_id, "🔁 أرسل البريد الإلكتروني المستخدم في حسابك (ex: wassim.netflix01@gmail.com)")

def process_email(user_id, email):
    row_index, row = find_account_by_email(email)
    if not row:
        send_message(user_id, "❌ هذا البريد الإلكتروني غير موجود في قاعدة البيانات.")
        return

    name = row.get("nom client", "")
    price = row.get("prix", "")
    text = f"👤 {name}\n💰 Prix : {price} DA\nVoulez-vous confirmer le renouvellement ?"
    buttons = [
        {"type": "postback", "title": "Oui ✅", "payload": f"CONFIRM_RENEW_{row_index}"},
        {"type": "postback", "title": "Non ❌", "payload": "CANCEL_RENEW"}
    ]
    send_message(user_id, text, buttons)

def confirm_payment(user_id, row_index):
    update_payment_status(row_index, paid=True)
    text = "✅ Paiement confirmé, votre compte a été renouvelé avec succès !"
    send_message(user_id, text)
