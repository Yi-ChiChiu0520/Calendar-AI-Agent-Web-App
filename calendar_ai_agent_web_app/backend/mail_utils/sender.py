from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os
import smtplib
from calendar_ai_agent_web_app.backend.utils.logger import logger

def send_email(to_emails: list[str], subject: str, message: str):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_emails, msg.as_string())
        logger.info(f"Email successfully sent to {msg['To']}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


