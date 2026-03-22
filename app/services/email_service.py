import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from typing import Dict, Any
import datetime

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "mail.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "TruMix Team")

# Email enabled flag
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"

# Setup Jinja2 environment
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "emails")
env = Environment(loader=FileSystemLoader(template_dir))

def send_email_sync(to_email: str, subject: str, template_name: str, context: Dict[str, Any]):
    """Synchronous function to send email. Designed to be run in a BackgroundTask."""
    if not EMAIL_ENABLED:
        print(f"[EMAIL DISABLED] Would send {template_name} to {to_email}: {subject}")
        return

    if not SMTP_USER or not SMTP_PASSWORD:
        print("[EMAIL ERROR] SMTP credentials not configured. Skipping email dispatch.")
        return

    # Add global variables to context
    context["year"] = datetime.datetime.now().year

    # Render template
    try:
        template = env.get_template(template_name)
        html_content = template.render(**context)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to render template {template_name}: {e}")
        return

    # Construct email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg["To"] = to_email

    # Attach HTML content
    part = MIMEText(html_content, "html")
    msg.attach(part)

    # Send email
    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        print(f"[EMAIL SUCCESS] '{subject}' sent to {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {e}")

# High-level dispatcher functions for specific events

def dispatch_welcome_email(to_email: str, name: str, login_url: str = "https://trumix.co.in/login"):
    subject = "Welcome to TruMix! 🎉"
    context = {"name": name, "login_url": login_url}
    send_email_sync(to_email, subject, "welcome.html", context)

def dispatch_login_alert(to_email: str, name: str, ip_address: str):
    subject = "New Login Alert - TruMix 🔐"
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context = {"name": name, "time": time_str, "ip_address": ip_address}
    send_email_sync(to_email, subject, "login.html", context)

def dispatch_order_placed(to_email: str, name: str, order_data: dict):
    subject = f"Order Confirmation #{order_data['id']} - TruMix 🛍️"
            
    context = {
        "name": name,
        "order_id": order_data['id'],
        "total_amount": order_data['total_amount'],
        "date": order_data['created_at'].strftime("%Y-%m-%d") if hasattr(order_data['created_at'], 'strftime') else order_data['created_at'],
        "payment_method": order_data['payment_method'].upper() if order_data['payment_method'] else "N/A",
        "items": order_data['items'],
        "orders_url": "https://trumix.co.in/account/orders"
    }
    send_email_sync(to_email, subject, "order_placed.html", context)

def dispatch_order_status(to_email: str, name: str, order_id: int, new_status: str):
    subject = f"Order Update #{order_id} - TruMix 🚚"
    context = {
        "name": name,
        "order_id": order_id,
        "new_status": new_status,
        "trackingUrl": "https://trumix.co.in/account/orders" # Placeholder
    }
    send_email_sync(to_email, subject, "order_status.html", context)
