from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError

from database import get_db
from models import User
from schemas import UserRegister, VerifyOTP

from otp import (
    generate_otp,
    get_otp_expiry,
    verify_otp
)

from email_service import send_otp_email
from sms import send_otp_sms

from config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(
        password,
        hashed_password
    )


# ============================================================
# JWT TOKEN
# ============================================================

def create_access_token(data: dict):

    to_encode = data.copy()

    from datetime import datetime, timedelta

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ============================================================
# REGISTER USER
# ============================================================

@router.post("/register")
def register_user(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # CHECK EMAIL
    # --------------------------------------------------------

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # --------------------------------------------------------
    # CHECK PHONE
    # --------------------------------------------------------

    existing_phone = db.query(User).filter(
        User.phone == user.phone
    ).first()

    if existing_phone:

        raise HTTPException(
            status_code=400,
            detail="Phone already registered"
        )

    # --------------------------------------------------------
    # GENERATE OTP
    # --------------------------------------------------------

    otp = generate_otp()

    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    new_user = User(

        full_name=user.full_name,

        email=user.email,

        phone=user.phone,

        password=hash_password(
            user.password
        ),

        otp=otp,

        otp_expiry=get_otp_expiry(),

        is_verified=False
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    # --------------------------------------------------------
    # SEND EMAIL OTP
    # --------------------------------------------------------

    email_sent = send_otp_email(
        user.email,
        otp
    )

    # --------------------------------------------------------
    # SEND SMS OTP
    # --------------------------------------------------------

    sms_sent = send_otp_sms(
        user.phone,
        otp
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "message": "User registered. OTP sent.",

        "user_id": new_user.id,

        "email_sent": email_sent,

        "sms_sent": sms_sent
    }


# ============================================================
# VERIFY OTP
# ============================================================

@router.post("/verify-otp")
def verify_user_otp(
    data: VerifyOTP,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------------------------------
    # CHECK OTP
    # --------------------------------------------------------

    if not verify_otp(
        data.otp,
        user.otp,
        user.otp_expiry
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    # --------------------------------------------------------
    # VERIFY USER
    # --------------------------------------------------------

    user.is_verified = True

    user.otp = None

    user.otp_expiry = None

    db.commit()

    return {

        "message": "OTP verified successfully",

        "verified": True
    }


# ============================================================
# RESEND OTP
# ============================================================

@router.post("/resend-otp")
def resend_otp(
    email: str,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # FIND EXISTING USER
    # --------------------------------------------------------

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------------------------------
    # GENERATE NEW OTP
    # --------------------------------------------------------

    new_otp = generate_otp()

    user.otp = new_otp

    user.otp_expiry = get_otp_expiry()

    # --------------------------------------------------------
    # ALLOW OTP VERIFICATION AGAIN
    # --------------------------------------------------------

    user.is_verified = False

    db.commit()

    # --------------------------------------------------------
    # SEND EMAIL OTP
    # --------------------------------------------------------

    email_sent = send_otp_email(
        user.email,
        new_otp
    )

    # --------------------------------------------------------
    # SEND SMS OTP
    # --------------------------------------------------------

    sms_sent = send_otp_sms(
        user.phone,
        new_otp
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "message": "OTP sent successfully",

        "email_sent": email_sent,

        "sms_sent": sms_sent
    }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    if not verify_password(
        form_data.password,
        db_user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # OTP VERIFICATION CHECK
    # --------------------------------------------------------

    if not db_user.is_verified:

        raise HTTPException(
            status_code=403,
            detail="Please verify OTP first"
        )

    # --------------------------------------------------------
    # CREATE JWT
    # --------------------------------------------------------

    token = create_access_token({

        "sub": str(db_user.id)

    })

    return {

        "access_token": token,

        "token_type": "bearer"
    }


# ============================================================
# OAUTH2
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(

    token: str = Depends(oauth2_scheme),

    db: Session = Depends(get_db)

):

    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]

        )

        user_id = payload.get("sub")

        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except JWTError:

        raise HTTPException(

            status_code=401,

            detail="Invalid token"

        )

    # --------------------------------------------------------
    # CONVERT USER ID
    # --------------------------------------------------------

    try:

        user_id = int(user_id)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"

        )

    return user


# ============================================================
# CURRENT USER
# ============================================================

@router.get("/me")
def get_me(

    current_user: User = Depends(
        get_current_user
    )

):

    return {

        "id": current_user.id,

        "full_name": current_user.full_name,

        "email": current_user.email,

        "phone": current_user.phone,

        "verified": current_user.is_verified

    }