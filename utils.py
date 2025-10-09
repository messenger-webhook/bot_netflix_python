import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Charger les credentials depuis le fichier JSON
SCOPE = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"

def get_client():
    """Retourne le client gspread autorisé"""
    from google.oauth2.service_account import Credentials
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPE)
    return gspread.authorize(creds)

def get_sheet_data(sheet_name="netnet1", file_name="netnet"):
    """Récupère toutes les lignes de la feuille"""
    client = get_client()
    sheet = client.open(file_name).worksheet(sheet_name)
    rows = sheet.get_all_records()
    return rows

def update_sheet_row(sheet_row_index, column_name, value, sheet_name="netnet1", file_name="netnet"):
    """Met à jour une cellule spécifique par index de ligne (0-based)"""
    client = get_client()
    sheet = client.open(file_name).worksheet(sheet_name)
    col_index = sheet.row_values(1).index(column_name) + 1
    sheet.update_cell(sheet_row_index + 2, col_index, value)  # +2 car header + 0-based
