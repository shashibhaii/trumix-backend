# Email Setup Guide for TruMix

Quick guide to enable email notifications for order confirmations and welcome emails.

## 📧 What You'll Get

- **Order Confirmation Emails**: Sent automatically when customers place orders
- **Welcome Emails**: Sent when new users register (includes WELCOME10 coupon!)

## 🚀 Quick Setup (Gmail)

### 1. Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** → **2-Step Verification** (enable if not already)
3. Scroll to **App passwords**
4. Generate new app password for "Mail"
5. Copy the 16-character password

### 2. Update .env File

Copy `.env.example` to `.env` (if you haven't already):
```bash
cp .env.example .env
```

Edit `.env` and update these lines:
```bash
EMAIL_ENABLED=true

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=youremail@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=noreply@trumix.co.in
SMTP_FROM_NAME=TruMix
```

### 3. Restart Server

```bash
# Server will auto-reload if you're using --reload flag
# Otherwise, restart manually
```

## ✅ Testing

### Test Welcome Email
Register a new user:
```bash
POST /api/v1/auth/register
{
  "name": "Test User",
  "email": "yourtest@email.com",
  "password": "password123",
  "phone": "9876543210"
}
```

Check your email! You should receive a welcome email with WELCOME10 coupon.

### Test Order Confirmation
1. Login and create an order
2. Check the customer email address
3. You'll receive an order confirmation with all details!

## 🎨 Email Templates Include

### Order Confirmation:
- Order number and date
- Product list with prices
- Financial breakdown (subtotal, tax, shipping, discount, total)
- Delivery address
- Track order button

### Welcome Email:
- Personalized greeting
- WELCOME10 coupon code
- Feature highlights
- Shop now button

## 🔧 Alternative SMTP Providers

### SendGrid
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

### Mailgun
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
```

### AWS SES
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
```

## 🐛 Troubleshooting

### Emails not sending?
1. Check console logs for error messages
2. Verify `EMAIL_ENABLED=true` in `.env`
3. Confirm SMTP credentials are correct
4. For Gmail: Make sure app password (not regular password) is used

### Development Mode
Keep `EMAIL_ENABLED=false` during development to:
- See email content in console logs
- Avoid sending test emails to real addresses
- Test without SMTP configuration

## 📝 Template Customization

Email templates are in `app/services/email_templates.py`:
- `get_order_confirmation_template()` - Order emails
- `get_welcome_email_template()` - Welcome emails

Feel free to customize colors, text, and layout!

---

Need help? Contact your development team or check [walkthrough.md](file:///C:/Users/shash/.gemini/antigravity/brain/47bad0c2-c156-4568-8c36-44984be10601/walkthrough.md) for full documentation.
