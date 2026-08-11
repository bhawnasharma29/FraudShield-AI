# ==========================================
# SMS SERVICE
# FraudShield-AI
# Fast2SMS Integration
# ==========================================

import os
import requests
from dotenv import load_dotenv

load_dotenv()

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")


def send_otp_sms(phone_number: str, otp: str):

    message = (
        f"FraudShield-AI Verification OTP: {otp}. "
        f"This OTP is valid for 5 minutes. Do not share it with anyone."
    )

    try:

        url = "https://www.fast2sms.com/dev/bulkV2"

        headers = {
            "authorization": FAST2SMS_API_KEY
        }

        payload = {
            "route": "q",
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": phone_number
        }

        response = requests.post(
            url=url,
            headers=headers,
            data=payload
        )

        print("=" * 50)
        print("STATUS CODE :", response.status_code)
        print("RESPONSE TEXT:")
        print(response.text)
        print("=" * 50)

        try:
            result = response.json()

            print("FAST2SMS RESPONSE:")
            print(result)

            if result.get("return") is True:
                print("SMS SENT SUCCESSFULLY")
                return True
            else:
                print("SMS FAILED")
                return False

        except Exception as e:
            print("JSON Error:", e)
            print("Raw Response:", response.text)
            return False

    except Exception as e:

        print("SMS Error:", e)
        return False