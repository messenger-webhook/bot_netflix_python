# -*- coding: utf-8 -*-
import requests
import json
import os

# === CONFIG ===
APP_ID = "693834286308606"
APP_SECRET = "b370b63a6cafa7a144131c8c079aca96"
USER_TOKEN_LONG = "EAAJ3CeIrHP4BPjwlrZBLOxyejnxSsmc3C6GUsEk2xVq2ZB1Ihl8vhcl5MaEb9XpNPZAV5d5TxwhqZA86Xn4PsMIJyp66swtqBnrovmZBQ9TZCVfm0hXEXAcMK4PZA5AZBNh06ogZB6VZCxZBDYkqD3YcvDlcUqflgxhtzxTU1nZAKXvdPzyvZCQYm9s8pbW66xBeZAZBlHq"
PAGE_ID = "100389475278672"
ENV_PATH = ".env"  # chemin vers ton fichier .env

def get_new_page_token():
    """Récupère un nouveau Page Access Token à partir du User Token."""
    url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={USER_TOKEN_LONG}"
    try:
        r = requests.get(url)
        data = r.json()

        if "data" in data:
            for page in data["data"]:
                if page.get("id") == PAGE_ID:
                    new_token = page.get("access_token")
                    print("✅ Nouveau PAGE_ACCESS_TOKEN récupéré avec succès.")
                    return new_token

        print("⚠️ Impossible de récupérer le token de la page.")
        print("Réponse API :", json.dumps(data, indent=2, ensure_ascii=False))
        return None

    except Exception as e:
        print("❌ Erreur lors de la requête :", e)
        return None


def update_env_file(token):
    """Met à jour la valeur du PAGE_ACCESS_TOKEN dans ton fichier .env."""
    if not os.path.exists(ENV_PATH):
        print(f"⚠️ Fichier {ENV_PATH} introuvable. Création d’un nouveau.")
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(f"PAGE_ACCESS_TOKEN={token}\n")
        return

    lines = []
    updated = False
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("PAGE_ACCESS_TOKEN="):
                lines.append(f"PAGE_ACCESS_TOKEN={token}\n")
                updated = True
            else:
                lines.append(line)

    if not updated:
        lines.append(f"PAGE_ACCESS_TOKEN={token}\n")

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print("📝 Fichier .env mis à jour avec le nouveau token.")


def main():
    print("🔁 Vérification et renouvellement du token de page...")
    new_token = get_new_page_token()
    if new_token:
        update_env_file(new_token)
        print("✅ Token mis à jour automatiquement.")
    else:
        print("❌ Aucun nouveau token généré.")


if __name__ == "__main__":
    main()
