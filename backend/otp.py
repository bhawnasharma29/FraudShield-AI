from datetime import datetime, timedelta
import random


# ==========================================
# GENERATE OTP
# ==========================================

def generate_otp():

    return str(
        random.randint(
            100000,
            999999
        )
    )


# ==========================================
# OTP EXPIRY TIME
# ==========================================

def get_otp_expiry():

    return datetime.utcnow() + timedelta(
        minutes=5
    )


# ==========================================
# VERIFY OTP
# ==========================================

def verify_otp(
    entered_otp: str,
    saved_otp: str,
    expiry_time
):

    # OTP expired check

    if datetime.utcnow() > expiry_time:
        return False


    # OTP match check

    if entered_otp == saved_otp:
        return True


    return False