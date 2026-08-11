from pydantic import BaseModel, EmailStr
from datetime import datetime



# ==========================================
# USER SCHEMAS
# ==========================================

class UserRegister(BaseModel):

    full_name: str
    email: EmailStr
    phone: str
    password: str



class UserLogin(BaseModel):

    email: EmailStr
    password: str



class UserResponse(BaseModel):

    id: int
    full_name: str
    email: EmailStr
    phone: str
    is_verified: bool


    class Config:
        from_attributes = True



# ==========================================
# OTP SCHEMAS
# ==========================================

class SendOTP(BaseModel):

    email: EmailStr



class VerifyOTP(BaseModel):

    email: EmailStr
    otp: str



# ==========================================
# TRANSACTION SCHEMAS
# ==========================================

class TransactionCreate(BaseModel):

    amount: float

    transaction_type: str

    merchant: str

    location: str


    # Advanced Fraud Tracking

    device_id: str | None = None

    ip_address: str | None = None



class TransactionResponse(BaseModel):

    id: int

    user_id: int

    amount: float

    transaction_type: str

    merchant: str

    location: str

    status: str



    # ======================================
    # FRAUD DETECTION RESPONSE
    # ======================================


    risk_score: int

    fraud_status: str

    merchant_risk: int

    behavior_score: int


    fraud_reason: str | None = None

    fraud_alert: str | None = None



    # ======================================
    # ADVANCED FRAUD FEATURES
    # ======================================


    device_id: str | None = None

    ip_address: str | None = None


    is_blocked: bool

    verification_required: bool

    duplicate_transaction: bool



    created_at: datetime



    class Config:

        from_attributes = True