from utils import send_message, get_sheet
import datetime

def start_new_account(user_id):
    text = "🛒 مرحبا! اختر الخدمة التي تريد شرائها :"
    buttons = [
        {"type": "postback", "title": "Netflix", "payload": "NEW_NETFLIX"},
        {"type": "postback", "title": "Shahid", "payload": "NEW_SHAHID"},
        {"type": "postback", "title": "Spotify", "payload": "NEW_SPOTIFY"}
    ]
    send_message(user_id, text, buttons)

def process_service_choice(user_id, service_name):
    text = f"⏳ اختر المدة التي تريدها pour {service_name} :"
    buttons = [
        {"type": "postback", "title": "1 mois", "payload": f"NEW_{service_name}_1M"},
        {"type": "postback", "title": "3 mois", "payload": f"NEW_{service_name}_3M"}
    ]
    send_message(user_id, text, buttons)

def confirm_new_account(user_id, service_name, duration):
    sheet = get_sheet()
    today = datetime.date.today().strftime("%d/%m/%Y")
    new_row = [f"{service_name}_{today}", "", "", "", "", "", "", today]
    sheet.append_row(new_row)
    text = f"✅ تم تسجيل طلبك لشراء {service_name} لمدة {duration}.\n📩 سنتواصل معك لتأكيد الدفع."
    send_message(user_id, text)
