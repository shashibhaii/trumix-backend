"""
Email service for sending transactional emails
Supports order confirmations, welcome emails, and more
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import os
from pathlib import Path

# Email configuration from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@trumix.co.in")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "TruMix")

# Email enabled flag
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: Optional[str] = None
) -> bool:
    """
    Send an HTML email
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content
        plain_body: Plain text fallback (optional)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not EMAIL_ENABLED:
        print(f"[EMAIL DISABLED] Would send to {to_email}: {subject}")
        return True
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("[EMAIL ERROR] SMTP credentials not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        
        # Add plain text version if provided
        if plain_body:
            msg.attach(MIMEText(plain_body, 'plain'))
        
        # Add HTML version
        msg.attach(MIMEText(html_body, 'html'))
        
        # Connect to SMTP server and send
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"[EMAIL] Sent to {to_email}: {subject}")
        return True
        
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {str(e)}")
        return False


def send_order_confirmation(order_data: dict) -> bool:
    """
    Send order confirmation email
    
    Args:
        order_data: Dictionary with order details
            - customer_email
            - customer_name
            - order_id
            - items (list of dicts with name, quantity, price)
            - subtotal, discount_amount, tax_amount, shipping_amount, cod_charges, total_amount
            - shipping_address
    """
    from .email_templates import get_order_confirmation_template
    
    html_body = get_order_confirmation_template(order_data)
    subject = f"Order Confirmation #{order_data['order_id']} - TruMix"
    
    return send_email(
        to_email=order_data['customer_email'],
        subject=subject,
        html_body=html_body
    )


def send_welcome_email(user_data: dict) -> bool:
    """
    Send welcome email to new user
    
    Args:
        user_data: Dictionary with user details
            - email
            - name
    """
    from .email_templates import get_welcome_email_template
    
    html_body = get_welcome_email_template(user_data)
    subject = "Welcome to TruMix - Premium Indian Snacks & Beverages!"
    
    return send_email(
        to_email=user_data['email'],
        subject=subject,
        html_body=html_body
    )
