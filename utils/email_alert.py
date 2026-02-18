import smtplib
import os
from email.message import EmailMessage

# ===============================
# EMAIL CONFIGURATION (UNCHANGED)
# ===============================
SENDER_EMAIL = "chamanchangappa140@gmail.com"
RECEIVER_EMAIL = "chmnchangappa@gmail.com"
APP_PASSWORD = "igqk eivb jbab tyoh"


def send_email(image_path, csv_path, date, time, location, severity):
    msg = EmailMessage()
    msg["Subject"] = "🚧 Pothole Detected Alert"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    msg.set_content(
        f"""
Pothole Detected!

📅 Date: {date}
🕒 Time: {time}
📍 Location: {location}
⚠️ Severity: {severity}

Attached:
- Detected pothole image
- CSV log file
"""
    )

    # -------- Attach Image --------
    with open(image_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="image",
            subtype="jpeg",
            filename=os.path.basename(image_path)
        )

    # -------- Attach CSV --------
    if os.path.exists(csv_path):
        with open(csv_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="text",
                subtype="csv",
                filename=os.path.basename(csv_path)
            )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

    print("📧 Email sent (image + CSV attached)")
