import os
import smtplib
from email.message import EmailMessage

def send_2fa_code(to_email, code):
    """Sends a 2FA code to the specified email address."""
    
    email_host = os.environ.get('EMAIL_HOST')
    email_port = int(os.environ.get('EMAIL_PORT', 465))
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')

    if not all([email_host, email_port, email_user, email_pass]):
        print("\n" + "="*50)
        print("WARNING: Email service is not configured in .env file.")
        print(f"FALLBACK 2FA Code for {to_email}: {code}")
        print("Login will proceed using this fallback code.")
        print("="*50 + "\n")
        return True

    subject = "Your SmartBank Verification Code"
    body = f"""
    Hello,

    Your two-factor authentication code is: {code}

    This code will expire in 10 minutes.

    If you did not request this code, please secure your account immediately.

    Thank you,
    The SmartBank Team
    """

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = email_user
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL(email_host, email_port) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
            print(f"2FA code successfully sent to {to_email}")
            return True
    except smtplib.SMTPAuthenticationError:
        print("ERROR: SMTP Authentication failed. Check your EMAIL_USER and EMAIL_PASS credentials in the .env file. If using Gmail, ensure you have an 'App Password'.")
        return False
    except Exception as e:
        print(f"ERROR: Failed to send 2FA email. Details: {e}")
        return False
