import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import EMAIL_ADDRESS, EMAIL_PASSWORD


def send_otp_email(receiver_email: str, otp: str) -> bool:
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

    # ============================================================
    # OTP FOR DEMO
    # ============================================================
    # Render Free par Gmail SMTP blocked hone ki wajah se
    # OTP ko logs mein bhi print kar rahe hain.
    print("=" * 60)
    print("FRAUDSHIELD-AI OTP")
    print("TO:", receiver_email)
    print("OTP:", otp)
    print("=" * 60)

    # ============================================================
    # CREATE EMAIL
    # ============================================================

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

    server = None

    try:
        print("=" * 60)
        print("OTP EMAIL STARTED")
        print("FROM:", EMAIL_ADDRESS)
        print("TO:", receiver_email)
        print("=" * 60)

        # Gmail SMTP
        server = smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=30
        )

        server.ehlo()
        print("SMTP CONNECTION SUCCESS")

        # TLS
        server.starttls()
        server.ehlo()
        print("TLS SUCCESS")

        # Gmail login
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
        print("ERROR:", e)
        print("=" * 60)

        return False

    except smtplib.SMTPConnectError as e:
        print("=" * 60)
        print("GMAIL SMTP CONNECTION ERROR")
        print("ERROR:", e)
        print("=" * 60)

        return False

    except smtplib.SMTPException as e:
        print("=" * 60)
        print("GMAIL SMTP ERROR")
        print("ERROR:", e)
        print("=" * 60)

        return False

    except Exception as e:
        print("=" * 60)
        print("EMAIL ERROR")
        print(type(e).__name__)
        print("ERROR:", e)
        print("=" * 60)

        return False

    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass