import imaplib
import email
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("/root/daily-journal/.env")

IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")
IMAP_FOLDER = os.getenv("IMAP_FOLDER")
KEYWORD = os.getenv("MAIL_SUBJECT_KEYWORD")
REPO_DIR = os.getenv("REPO_DIR")

mail = imaplib.IMAP4_SSL(IMAP_HOST)
mail.login(IMAP_USER, IMAP_PASS)
mail.select(IMAP_FOLDER)

status, data = mail.search(None, f'(UNSEEN SUBJECT "{KEYWORD}")')
mail_ids = data[0].split()

if not mail_ids:
    print("No matching emails found")
    mail.logout()
    raise SystemExit

for mail_id in mail_ids:
    status, msg_data = mail.fetch(mail_id, "(RFC822)")
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(errors="ignore")
                break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(errors="ignore")

    today = datetime.now().strftime("%Y-%m-%d")
    journal_dir = os.path.join(REPO_DIR, "journals")
    os.makedirs(journal_dir, exist_ok=True)

    filename = os.path.join(journal_dir, f"{today}.md")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n\n---\n\n{body}\n")

    print(f"Saved: {filename}")

mail.logout()
