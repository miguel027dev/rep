import os
import smtplib
from email.message import EmailMessage

from .logging_utils import log_event


def email_configured():
    return bool(os.getenv("SMTP_HOST") and os.getenv("EMAIL_FROM"))


def send_email(to_email, subject, text_body):
    if not email_configured():
        log_event("warning", "email_not_configured", subject=subject)
        return False
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("EMAIL_FROM")
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(text_body)
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=10) as smtp:
                if username:
                    smtp.login(username, password or "")
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=10) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                if username:
                    smtp.login(username, password or "")
                smtp.send_message(msg)
        return True
    except Exception as exc:
        log_event("error", "email_send_failed", error=type(exc).__name__)
        return False
