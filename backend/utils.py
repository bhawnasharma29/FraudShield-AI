from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM

import random


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ==========================
# PASSWORD
# ==========================

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ==========================
# JWT TOKEN
# ==========================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=30
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            return None

        return user_id

    except JWTError:
        return None


# ==========================
# OTP FUNCTIONS
# ==========================

def generate_otp():

    return str(
        random.randint(
            100000,
            999999
        )
    )


def otp_expiry_time():

    return datetime.utcnow() + timedelta(
        minutes=5
    )