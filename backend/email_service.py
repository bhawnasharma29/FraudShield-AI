
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import EMAIL_ADDRESS, EMAIL_PASSWORD


# ============================================================
# SEND OTP EMAIL
# ============================================================

def send_otp_email(
    receiver_email: str,
    otp: str
):

    subject = "FraudShield-AI OTP Verification"

    body = f"""
Hello,

Your FraudShield-AI verification OTP is:

{otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.

Thanks,
FraudShield-AI Team
"""

    # ========================================================
    # CREATE EMAIL
    # ========================================================

    message = MIMEMultipart()

    message["From"] = EMAIL_ADDRESS
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(
        MIMEText(
            body,
            "plain"
        )
    )

    # ========================================================
    # SEND EMAIL
    # ========================================================

    server = None

    try:

        print("=" * 60)
        print("EMAIL SENDING STARTED")
        print("From:", EMAIL_ADDRESS)
        print("To:", receiver_email)
        print("=" * 60)

        # Connect to Gmail SMTP
        server = smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=15
        )

        print("SMTP CONNECTION SUCCESS")

        # Enable debugging
        server.set_debuglevel(1)

        # Start TLS encryption
        server.starttls()

        print("TLS CONNECTION SUCCESS")

        # Login with Gmail + App Password
        server.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD
        )

        print("GMAIL LOGIN SUCCESS")

        # Send email
        server.sendmail(
            EMAIL_ADDRESS,
            receiver_email,
            message.as_string()
        )

        print("OTP EMAIL SENT SUCCESSFULLY")
        print("=" * 60)

        return True

    except smtplib.SMTPAuthenticationError as e:

        print("=" * 60)
        print("GMAIL AUTHENTICATION ERROR")
        print(e)
        print("=" * 60)

        return False

    except smtplib.SMTPConnectError as e:

        print("=" * 60)
        print("GMAIL CONNECTION ERROR")
        print(e)
        print("=" * 60)

        return False

    except TimeoutError as e:

        print("=" * 60)
        print("GMAIL CONNECTION TIMEOUT")
        print(e)
        print("=" * 60)

        return False

    except Exception as e:

        print("=" * 60)
        print("EMAIL ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 60)

        return False

    finally:

        if server is not None:

            try:
                server.quit()
            except Exception:
                pass

