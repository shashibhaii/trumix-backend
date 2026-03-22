import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from typing import Dict, Any
import datetime

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "mail.example.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER).strip()
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "TruMix Team").strip()
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://trumix.co.in").rstrip("/")

# Email enabled flag
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"

template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "emails")
env = Environment(loader=FileSystemLoader(template_dir))

def is_event_enabled(event_key: str) -> bool:
    """Helper to check if a specific email event is enabled in settings."""
    try:
        from ..database import SessionLocal
        from ..models import GlobalSetting
        
        db = SessionLocal()
        try:
            setting = db.query(GlobalSetting).filter(GlobalSetting.key == event_key).first()
            if setting:
                return setting.value.lower() == "true"
            return True # Default to enabled if setting not found
        finally:
            db.close()
    except Exception as e:
        print(f"[EMAIL SETTINGS ERROR] Could not check setting {event_key}: {e}")
        return True # Fail safe: enable it

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
        # Diagnostic setup
        print(f"[EMAIL DIAGNOSTIC] Attempting connection. Host: '{SMTP_HOST}', Port: {SMTP_PORT}")
        print(f"[EMAIL DIAGNOSTIC] User: '{SMTP_USER}' (len={len(SMTP_USER) if SMTP_USER else 0})")
        print(f"[EMAIL DIAGNOSTIC] Password Length: {len(SMTP_PASSWORD) if SMTP_PASSWORD else 0}")
        
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.set_debuglevel(1)  # High Verbosity for Vercel Logs
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.set_debuglevel(1)  # High Verbosity for Vercel Logs
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        print(f"[EMAIL SUCCESS] '{subject}' sent to {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {e}")

# High-level dispatcher functions for specific events

def dispatch_welcome_email(to_email: str, name: str, login_url: str = None):
    if not is_event_enabled("email_welcome"):
        return
    subject = "Welcome to TruMix! 🎉"
    login_url = login_url or f"{FRONTEND_URL}/login"
    context = {"name": name, "login_url": login_url}
    send_email_sync(to_email, subject, "welcome.html", context)

def dispatch_login_alert(to_email: str, name: str, ip_address: str):
    subject = "New Login Alert - TruMix 🔐"
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context = {"name": name, "time": time_str, "ip_address": ip_address}
    send_email_sync(to_email, subject, "login.html", context)

def dispatch_order_placed(to_email: str, name: str, order_data: dict):
    if not is_event_enabled("email_order_placed"):
        return
    subject = f"Order Confirmation #{order_data['id']} - TruMix 🛍️"
            
    context = {
        "name": name,
        "order_id": order_data['id'],
        "total_amount": order_data['total_amount'],
        "date": order_data['created_at'].strftime("%Y-%m-%d") if hasattr(order_data['created_at'], 'strftime') else order_data['created_at'],
        "payment_method": order_data['payment_method'].upper() if order_data['payment_method'] else "N/A",
        "items": order_data['items'],
        "orders_url": f"{FRONTEND_URL}/account/orders"
    }
    send_email_sync(to_email, subject, "order_placed.html", context)

def dispatch_order_status(to_email: str, name: str, order_id: int, new_status: str):
    if not is_event_enabled("email_order_status"):
        return
    subject = f"Order Update #{order_id} - TruMix 🚚"
    context = {
        "name": name,
        "order_id": order_id,
        "new_status": new_status,
        "trackingUrl": f"{FRONTEND_URL}/account/orders" # Placeholder
    }
    send_email_sync(to_email, subject, "order_status.html", context)

def dispatch_marketing_email(to_email: str, subject: str, content: str, user_name: str = None, cta_url: str = None, cta_text: str = None):
    """Send a custom marketing email to a user with variable support."""
    # Create a sub-context for the content itself
    content_context = {
        "name": user_name or "Valued Customer",
        "email": to_email
    }
    
    # Render the content string as a Jinja2 template
    try:
        from jinja2 import Template
        rendered_content = Template(content).render(**content_context)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to render marketing content variables: {e}")
        rendered_content = content # Fallback to original content
        
    context = {
        "content": rendered_content,
        "cta_url": cta_url,
        "cta_text": cta_text
    }
    send_email_sync(to_email, subject, "marketing.html", context)
