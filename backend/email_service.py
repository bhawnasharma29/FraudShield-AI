import os
import resend


# ============================================================
# RESEND CONFIGURATION
# ============================================================

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


# ============================================================
# SEND OTP EMAIL
# ============================================================

def send_otp_email(receiver_email: str, otp: str) -> bool:

    subject = "FraudShield-AI OTP Verification"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">

        <h2>FraudShield-AI OTP Verification</h2>

        <p>Hello,</p>

        <p>Your FraudShield-AI verification OTP is:</p>

        <h1 style="letter-spacing: 5px;">
            {otp}
        </h1>

        <p>
            This OTP is valid for <strong>5 minutes</strong>.
        </p>

        <p>
            Do not share this OTP with anyone.
        </p>

        <p>
            Thanks,<br>
            <strong>FraudShield-AI Team</strong>
        </p>

    </body>
    </html>
    """

    # ========================================================
    # DEMO LOG
    # ========================================================

    print("=" * 60)
    print("FRAUDSHIELD-AI OTP")
    print("TO:", receiver_email)
    print("OTP:", otp)
    print("=" * 60)

    # ========================================================
    # CHECK API KEY
    # ========================================================

    if not RESEND_API_KEY:
        print("=" * 60)
        print("RESEND ERROR")
        print("RESEND_API_KEY is missing")
        print("=" * 60)
        return False

    try:
        print("=" * 60)
        print("RESEND EMAIL STARTED")
        print("TO:", receiver_email)
        print("=" * 60)

        # ====================================================
        # SEND EMAIL USING RESEND
        # ====================================================

        params = {
            "from": "onboarding@resend.dev",
            "to": [receiver_email],
            "subject": subject,
            "html": html_body,
        }

        email = resend.Emails.send(params)

        print("=" * 60)
        print("OTP EMAIL SENT SUCCESSFULLY")
        print("RESEND RESPONSE:", email)
        print("=" * 60)

        return True

    except Exception as e:
        print("=" * 60)
        print("RESEND EMAIL ERROR")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", e)
        print("=" * 60)

        return False