import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def send_verification_email(email: str, token: str):
    sender_email = os.getenv("EMAIL_USER")
    receiver_email = email
    password = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify your email"
    message["From"] = sender_email
    message["To"] = receiver_email

    verify_link = f"http://localhost:8000/verify?token={token}"
    text = f"Please click the link to verify your email: {verify_link}"

    part = MIMEText(text, "plain")
    message.attach(part)

    try:
        with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            print("Attempting to log in...")
            server.login(sender_email, password)
            print("Login completed.")
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent.")
    except Exception as e:
        print(f"An error occurred: {e}")