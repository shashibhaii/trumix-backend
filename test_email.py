import os
from dotenv import load_dotenv
from app.services.email_service import dispatch_welcome_email

load_dotenv()

# We will send the test email to the SMTP_FROM_EMAIL itself (your inbox)
test_email = os.getenv("SMTP_FROM_EMAIL", "notification@trumix.co.in")

if not test_email:
    print("Error: SMTP_USER not found in .env")
else:
    print(f"Testing SMTP Configuration...")
    print(f"Sending test welcome email to: {test_email}")
    try:
        dispatch_welcome_email(test_email, "System Admin")
        print("Dispatch function called.")
    except Exception as e:
        print(f"Test failed with error: {e}")
