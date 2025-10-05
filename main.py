import requests
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# === CONFIGURATION ===
URL = "https://www.nigeremploi.com/recherche_offre-secteur-informatique-tic-t%C3%A9l%C3%A9com"
DATA_FILE = "job_count.json"

EMAIL_SENDER = "maboubacarsadik@gmail.com"
EMAIL_PASSWORD = "jjdo tpki niwv dldo"
EMAIL_RECEIVER = "maboubacarsadik@gmail.com"  # ou une autre adresse


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# === FONCTIONS ===

def get_total_count():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(URL, headers=headers, timeout=15)
    r.raise_for_status()
    text = r.text

    m = re.search(r"Nombre\s+d'annonce(?:\(s\))?\s*=\s*(\d+)", text, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)


def main():
    # Charger la dernière valeur sauvegardée
    try:
        data = json.load(open(DATA_FILE))
        old_count = data.get("count", 0)
    except FileNotFoundError:
        old_count = 0

    # Obtenir le nouveau nombre
    current_count = get_total_count()
    if current_count is None:
        print("⚠️ Impossible de trouver le nombre d'annonces.")
        return

    print(f"📊 Ancien : {old_count} | Actuel : {current_count}")

    # Si le nombre a changé → envoyer un e-mail
    if current_count != old_count:
        diff = current_count - old_count
        change_type = "augmentation 📈" if diff > 0 else "diminution 📉"

        subject = f"[Alerte Emploi Niger] Changement détecté ({change_type})"
        body = (
            f"Le nombre total d'annonces dans la catégorie Informatique/TIC a changé.\n\n"
            f"Ancien nombre : {old_count}\n"
            f"Nouveau nombre : {current_count}\n"
            f"Type de changement : {change_type}\n\n"
            f"👉 Voir la page : {URL}"
        )

        send_email(subject, body)
        json.dump({"count": current_count}, open(DATA_FILE, "w"))
        print("📬 E-mail envoyé.")
    else:
        print("✅ Aucun changement détecté.")


if __name__ == "__main__":
    while True:
        main()
        time.sleep(86400)  # vérifie toutes les heures
