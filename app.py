from flask import Flask, request
import requests
import os
import logging
import time
import re
from datetime import datetime
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CHARGEMENT DU .ENV ===
load_dotenv()
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

# === CONFIG GOOGLE SHEETS ===
GOOGLE_SVC_ACCOUNT_FILE = r"C:\Users\LENOVO\Desktop\bot telegram\credentials.json"
SHEET_ID = "1PYPI9EHX01zkL8gaNqKDk1p_KhXAoi_XtEYMStxCp4c"
SHEET_NAME = "netnet1"

# === CONFIG KUKU ===
KUKU_URL = "https://m.kuku.lu/recv.php"
FIREFOX_PROFILE_PATH = r"C:\Users\LENOVO\AppData\Roaming\Mozilla\Firefox\Profiles\ev6x8hpa.default-release"
FIREFOX_BINARY_PATH = r"C:\Program Files\Mozilla Firefox\firefox.exe"
GECKODRIVER_PATH = "geckodriver.exe"
MAIL_LINK_TITRE = "Netflix : Nouvelle demande d'identification"
MAIL_CODE_TITRE = "Netflix : Votre code d'identification"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === ETAT UTILISATEUR ===
user_state = {}  # user_id -> état actuel
user_data = {}   # user_id -> données temporaires

# === GOOGLE SHEETS ===
def get_worksheet():
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SVC_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

def find_row_index_and_record_by_email_and_name(ws, email, name):
    records = ws.get_all_records()
    target_email = (email or "").strip().lower()
    target_name = (name or "").strip().lower()
    last_email = None
    for i, rec in enumerate(records, start=2):
        a = str(rec.get("email","")).strip().lower()
        d = str(rec.get("nom client","")).strip().lower()
        if not a and last_email:
            a = last_email
        else:
            last_email = a
        if (a == target_email) and (target_name in d or d in target_name):
            return i, rec
    # essai par email seul
    last_email = None
    for i, rec in enumerate(records, start=2):
        a = str(rec.get("email","")).strip().lower()
        if not a and last_email:
            a = last_email
        else:
            last_email = a
        if a == target_email:
            return i, rec
    return None, None

# === FONCTIONS KUKU ===
def approuver_mail_netflix():
    options = Options()
    options.binary_location = FIREFOX_BINARY_PATH
    options.add_argument("-profile")
    options.add_argument(FIREFOX_PROFILE_PATH)
    driver = webdriver.Firefox(service=Service(GECKODRIVER_PATH), options=options)
    try:
        driver.get(KUKU_URL)
        time.sleep(8)
        mails = driver.find_elements(By.CSS_SELECTOR, "div[id^='area_mail_'] a[id^='link_maildata_']")
        for mail in mails:
            if MAIL_LINK_TITRE.lower() in mail.text.lower():
                mail_id = mail.get_attribute("id").replace("link_maildata_", "")
                try:
                    btn_cancel = driver.find_element(By.ID, f"link_cancelDeleteMail_{mail_id}")
                    if btn_cancel.is_displayed():
                        driver.execute_script("arguments[0].click();", btn_cancel)
                        time.sleep(2)
                except: pass
                try:
                    driver.find_element(By.ID, f"link_maildata_{mail_id}").click()
                    time.sleep(5)
                    iframe = driver.find_element(By.CSS_SELECTOR, f"iframe[id^='area_maildata_iframe_{mail_id}']")
                    driver.switch_to.frame(iframe)
                    bouton = WebDriverWait(driver,10).until(
                        EC.presence_of_element_located((By.XPATH,"//a[contains(text(),\"Approuver l'identification\")]"))
                    )
                    href = bouton.get_attribute("href")
                    driver.execute_script(f"window.open('{href}','_blank');")
                    time.sleep(5)
                    driver.switch_to.window(driver.window_handles[-1])
                    confirmation = driver.find_element(By.TAG_NAME,"body").text
                    driver.switch_to.default_content()
                    if "Et voilà !" in confirmation:
                        return True
                except: return False
        return False
    finally:
        driver.quit()

def recuperer_code_4chiffres():
    options = Options()
    options.binary_location = FIREFOX_BINARY_PATH
    options.add_argument("-profile")
    options.add_argument(FIREFOX_PROFILE_PATH)
    driver = webdriver.Firefox(service=Service(GECKODRIVER_PATH), options=options)
    try:
        driver.get(KUKU_URL)
        time.sleep(8)
        mails = driver.find_elements(By.CSS_SELECTOR, "div[id^='area_mail_'] a[id^='link_maildata_']")
        for mail in mails:
            if MAIL_CODE_TITRE.lower() in mail.text.lower():
                mail_id = mail.get_attribute("id").replace("link_maildata_", "")
                driver.find_element(By.ID, f"link_maildata_{mail_id}").click()
                time.sleep(5)
                iframe = driver.find_element(By.CSS_SELECTOR, f"iframe[id^='area_maildata_iframe_{mail_id}']")
                driver.switch_to.frame(iframe)
                body_text = driver.find_element(By.TAG_NAME,"body").text
                driver.switch_to.default_content()
                m = re.search(r"Saisissez ce code pour vous identifier\s+(\d{4})", body_text)
                if m:
                    return m.group(1)
        return None
    finally:
        driver.quit()

# === FLASK / MESSENGER ===
app = Flask(__name__)

def send_message(recipient_id, message, buttons=None):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "messaging_type": "RESPONSE",
        "message": {"text": message}
    }
    if buttons:
        payload["message"] = {
            "attachment": {
                "type": "template",
                "payload": {"template_type": "button", "text": message, "buttons": buttons}
            }
        }
    requests.post(url, json=payload)

@app.route("/webhook", methods=["GET","POST"])
def webhook():
    if request.method=="GET":
        verify_token = "123456"
        if request.args.get("hub.verify_token")==verify_token:
            return request.args.get("hub.challenge")
        return "Invalid token"

    data = request.get_json()
    if not data or "entry" not in data: return "ok"
    for entry in data["entry"]:
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]
            if "postback" in event: handle_postback(sender_id, event["postback"]["payload"])
            elif "message" in event and "text" in event["message"]: handle_message(sender_id, event["message"]["text"])
    return "ok"

# === GESTION DU FLUX TELEGRAM DANS MESSENGER ===
def handle_postback(sender_id, payload):
    state = user_state.get(sender_id)

    if payload == "PROBLEM":
        send_message(sender_id, "⚠️ Envoyez votre email Netflix ou nom Facebook.")
        user_state[sender_id] = "ASK_EMAIL"
        user_data[sender_id] = {}
        return

    if state == "ASK_DEVICE":
        email = user_data[sender_id]["email"]
        if payload == "DEVICE_TV":
            send_message(sender_id, f"🔹 Sur TV : Email {email}, mot de passe 999000.\nEnvoyez 'j’ai envoyé le lien' après action.")
            user_state[sender_id] = "WAIT_LINK"
        elif payload in ["DEVICE_PHONE","DEVICE_PC"]:
            send_message(sender_id, f"📱 Sur appareil : Email {email}. Envoyez 'Recevoir le code' quand prêt.")
            user_state[sender_id] = "WAIT_CODE"

def handle_message(sender_id, text):
    state = user_state.get(sender_id)

    if state=="ASK_EMAIL":
        user_data[sender_id]["email"] = text.strip()
        send_message(sender_id, "Email reçu ✅. Envoyez nom Facebook.")
        user_state[sender_id] = "ASK_NAME"
    elif state=="ASK_NAME":
        user_data[sender_id]["name"] = text.strip()
        send_message(sender_id, "Confirmez-vous (répondez 'ok') ?")
        user_state[sender_id] = "CONFIRM"
    elif state=="CONFIRM":
        if text.strip().lower() != "ok":
            send_message(sender_id, "Répondez 'ok' pour continuer.")
            return
        email = user_data[sender_id]["email"]
        name = user_data[sender_id]["name"]
        ws = get_worksheet()
        row_index, record = find_row_index_and_record_by_email_and_name(ws,email,name)
        if not record:
            send_message(sender_id,"❌ Compte introuvable.")
            user_state.pop(sender_id)
            user_data.pop(sender_id)
            return
        date_str = record.get("date fin dinscription") or record.get("date fin d’inscription")
        expiry_date = datetime.strptime(date_str.strip(),"%d/%m/%Y")
        if expiry_date.date() <= datetime.today().date():
            send_message(sender_id,"⚠️ Compte expiré.")
            user_state.pop(sender_id)
            user_data.pop(sender_id)
            return
        # choix appareil
        buttons = [
            {"type":"postback","title":"📺 TV","payload":"DEVICE_TV"},
            {"type":"postback","title":"📱 Téléphone / Tablette","payload":"DEVICE_PHONE"},
            {"type":"postback","title":"💻 PC","payload":"DEVICE_PC"}
        ]
        send_message(sender_id,"✅ Compte valide ! Choisissez appareil:", buttons)
        user_state[sender_id] = "ASK_DEVICE"

    elif state=="WAIT_LINK" and "envoy" in text.lower():
        send_message(sender_id,"✅ Lien envoyé, approbation automatique...")
        if approuver_mail_netflix():
            send_message(sender_id,"✅ Identité approuvée !")
        else:
            send_message(sender_id,"⚠️ Impossible d’approuver le lien.")
        user_state.pop(sender_id)
        user_data.pop(sender_id)

    elif state=="WAIT_CODE" and "recevoir" in text.lower():
        send_message(sender_id,"🔹 Récupération du code…")
        code = recuperer_code_4chiffres()
        if code:
            send_message(sender_id,f"✅ Code : {code} (15 min)")
        else:
            send_message(sender_id,"❌ Impossible de récupérer le code.")
        user_state.pop(sender_id)
        user_data.pop(sender_id)

# === LANCEMENT ===
if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
