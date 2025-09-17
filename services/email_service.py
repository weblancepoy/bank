import os
import smtplib
from email.message import EmailMessage

def send_2fa_code(to_email, code):
    """Sends a 2FA code to the specified email address."""
    
    # Get email configuration from environment variables
    email_host = os.environ.get('EMAIL_HOST')
    email_port = int(os.environ.get('EMAIL_PORT', 465))
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')

    if not all([email_host, email_port, email_user, email_pass]):
        print("ERROR: Email service is not configured. Please set EMAIL variables in your .env file.")
        # Fallback for development: print the code to the console if email isn't set up.
        print(f"FALLBACK 2FA Code for {to_email}: {code}")
        return False

    # Create the email message content
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
        # Connect to the SMTP server using a secure SSL connection and send the email
        with smtplib.SMTP_SSL(email_host, email_port) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
            print(f"2FA code successfully sent to {to_email}")
            return True
    except smtplib.SMTPAuthenticationError:
        print("ERROR: SMTP Authentication failed. Check your EMAIL_USER and EMAIL_PASS credentials in the .env file.")
        return False
    except Exception as e:
        print(f"ERROR: Failed to send 2FA email. Details: {e}")
        return False
