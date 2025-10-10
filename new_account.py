# ======================
#   new_account.py
# ======================
from utils import send_message, append_to_sheet

# === Liste des services et leurs prix ===
SERVICES = {
    "NETFLIX": {
        "title": "Netflix",
        "prices": """💫 أسعار Netflix :
شهر 01 بالبريدي موب أو CCP : 750 دج
شهر 01 بالفليكسي : 890 دج

شهرين 02 بالبريدي موب أو CCP : 1400 دج
شهرين 02 بالفليكسي : 1790 دج

ثلاث 03 أشهر بالبريدي موب أو CCP : 2000 دج
ثلاث 03 أشهر بالفليكسي : 2590 دج

اختر طريقة الدفع 💳"""
    },
    "SHAHID": {
        "title": "Shahid VIP",
        "prices": """💫 أسعار Shahid VIP :
شهر 01 بالبريدي موب أو CCP : 600 دج
شهر 01 بالفليكسي : 750 دج

شهرين 02 بالبريدي موب أو CCP : 1100 دج
شهرين 02 بالفليكسي : 1300 دج

ثلاث 03 أشهر بالبريدي موب أو CCP : 1500 دج
ثلاث 03 أشهر بالفليكسي : 1800 دج

اختر طريقة الدفع 💳"""
    },
    "SPOTIFY": {
        "title": "Spotify",
        "prices": """💫 أسعار Spotify :
شهر 01 بالبريدي موب أو CCP : 600 دج
شهر 01 بالفليكسي : 750 دج

شهرين 02 بالبريدي موب أو CCP : 1100 دج
شهرين 02 بالفليكسي : 1300 دج

ثلاث 03 أشهر بالبريدي موب أو CCP : 1500 دج
ثلاث 03 أشهر بالفليكسي : 1800 دج

اختر طريقة الدفع 💳"""
    },
    "PRIME": {
        "title": "Prime Video",
        "prices": """💫 أسعار Prime Video :
شهر 01 بالبريدي موب أو CCP : 600 دج
شهر 01 بالفليكسي : 750 دج

شهرين 02 بالبريدي موب أو CCP : 1100 دج
شهرين 02 بالفليكسي : 1300 دج

ثلاث 03 أشهر بالبريدي موب أو CCP : 1500 دج
ثلاث 03 أشهر بالفليكسي : 1800 دج

اختر طريقة الدفع 💳"""
    },
}


# ================================
# 🧠 Démarrage de la commande
# ================================
def start_new_account(user_id):
    """Affiche la liste des services à acheter"""
    buttons1 = [
        {"type": "postback", "title": "✅ Netflix", "payload": "NEW_NETFLIX"},
        {"type": "postback", "title": "✅ Shahid VIP", "payload": "NEW_SHAHID"},
        {"type": "postback", "title": "✅ Spotify", "payload": "NEW_SPOTIFY"},
    ]
    send_message(user_id, "اختر الحساب الذي تريد من القائمة التالية 👇", buttons1)

    buttons2 = [
        {"type": "postback", "title": "✅ Prime Video", "payload": "NEW_PRIME"},
    ]
    send_message(user_id, "📺 المزيد من الحسابات :", buttons2)


# ================================
# 🎯 Affiche les prix d’un service
# ================================
def process_service_choice(user_id, service_name):
    """Montre les tarifs du service choisi"""
    service_key = service_name.upper()
    if service_key not in SERVICES:
        send_message(user_id, "⚠️ الخدمة غير معروفة.")
        return

    text = SERVICES[service_key]["prices"]
    buttons = [
        {"type": "postback", "title": "💳 بريدي موب / CCP", "payload": f"PAY_BARIDI_{service_key}"},
        {"type": "postback", "title": "📱 فليكسي", "payload": f"PAY_FLEXY_{service_key}"},
    ]
    send_message(user_id, text, buttons)


# ================================
# 💰 Informations de paiement
# ================================
def confirm_new_account(user_id, service_name, payment_type):
    """Affiche les infos de paiement et enregistre la commande"""
    if payment_type == "BARIDI":
        pay_text = """🏦 معلومات الدفع :
بريدي موب : 00799999004386752747
CCP : 43867527 clé 11"""
    else:
        pay_text = """📱 فليكسي :
الرقم : 0654103330"""

    send_message(user_id, pay_text)
    send_message(user_id, "📩 أرسل بريدك الإلكتروني الآن وسنتواصل معك لتأكيد الحساب.")

    # Enregistre la commande dans Google Sheets
    append_to_sheet({
        "user_id": user_id,
        "service": service_name,
        "payment_type": payment_type,
        "status": "En attente email",
    })
