import smtplib
from email.message import EmailMessage
from config import EMAIL_CONFIG

def send_email(to_email, body, subject):
    with smtplib.SMTP_SSL(EMAIL_CONFIG["SMTP_SERVER"], EMAIL_CONFIG["PORT"]) as smtp:
        smtp.login(EMAIL_CONFIG["MAIL_ADDRESS"], EMAIL_CONFIG["MAIL_APP_PW"])
        msg = EmailMessage()
        msg.set_content(body)
        msg['subject'] = subject
        msg['to'] = to_email
        msg['from'] = EMAIL_CONFIG["MAIL_ADDRESS"]
        smtp.send_message(msg)
