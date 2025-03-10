import requests
import time
import random
import smtplib
import os  # Import os to access environment variables
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# 🚀 API URL
SHIFT_API_URL = "https://northeastern.libstaffer.com/admin/shift/open/list"

# 🚀 Headers (Looks Like a Real Browser)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://northeastern.libstaffer.com/admin/home",
    "Origin": "https://northeastern.libstaffer.com",
    "X-Requested-With": "XMLHttpRequest"
}

# 🚀 Get credentials from environment variables
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER")  # Your Gmail
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # App Password
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")  # Recipient Email
SESSION_COOKIE = os.getenv("SESSION_COOKIE")  # Session Cookie

if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT, SESSION_COOKIE]):
    print("❌ Missing environment variables. Please set EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT, SESSION_COOKIE.")
    exit(1)  # Exit if required variables are not set

def send_email(subject, message):
    """Sends an email notification via Gmail SMTP."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECIPIENT
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        # 🚀 Connect to SMTP Server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        server.quit()

        print("📩 Email notification sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def get_date_range():
    """Returns today's date and 14 days later as formatted strings."""
    today = datetime.today().strftime("%Y-%m-%d")
    future_date = (datetime.today() + timedelta(days=14)).strftime("%Y-%m-%d")
    return today, future_date

def check_shifts():
    """Fetch available shifts with random delays to avoid bot detection."""
    SESSION_COOKIES = {"ls_info": SESSION_COOKIE}  # Store cookie

    while True:
        from_date, to_date = get_date_range()
        grange = f"{from_date} - {to_date}"

        PAYLOAD = {
            "uid": "89121",
            "from": from_date,
            "to": to_date,
            "grange": grange
        }

        print(f"🔄 Checking shifts from {from_date} to {to_date}...")

        # 🚀 Send API Request
        response = requests.post(SHIFT_API_URL, headers=HEADERS, cookies=SESSION_COOKIES, data=PAYLOAD)

        if response.status_code == 200:
            try:
                shift_data = response.json()
                print("✅ Shift Data:", shift_data)
                current_shift_count = len(shift_data["data"]["rows"])
                
                # 🚀 Send email only when new shifts appear
                if current_shift_count > 0:
                    subject = "🚨 Open Shift Available!"
                    message = f"New open shifts found: {shift_data['data']['rows']}"
                    send_email(subject, message)

            except requests.exceptions.JSONDecodeError:
                print("❌ API did not return JSON. Response might be HTML or empty.")
        else:
            print(f"❌ Failed to fetch shifts! HTTP Status: {response.status_code}")

        # 🚀 Random Delay to Avoid Detection
        wait_time = random.randint(240, 360)  # Random delay between 4 to 6 minutes
        print(f"⏳ Waiting {wait_time // 60} minutes before next check...\n")
        time.sleep(wait_time)

if __name__ == "__main__":
    print("🚀 Shift Checker is starting...")
    check_shifts()
