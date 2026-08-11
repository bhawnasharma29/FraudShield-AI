from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean
)

from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# ==========================================
# USER MODEL
# ==========================================

class User(Base):

    __tablename__ = "users"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    full_name = Column(
        String(100),
        nullable=False
    )


    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )


    phone = Column(
        String(15),
        unique=True,
        nullable=False
    )


    password = Column(
        String(255),
        nullable=False
    )


    otp = Column(
        String(6),
        nullable=True
    )


    otp_expiry = Column(
        DateTime,
        nullable=True
    )


    is_verified = Column(
        Boolean,
        default=False
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )



# ==========================================
# TRANSACTION MODEL
# ==========================================

class Transaction(Base):

    __tablename__ = "transactions"



    id = Column(
        Integer,
        primary_key=True,
        index=True
    )



    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )



    amount = Column(
        Float,
        nullable=False
    )



    transaction_type = Column(
        String(50),
        nullable=False
    )



    merchant = Column(
        String(100),
        nullable=False
    )



    location = Column(
        String(100),
        nullable=False
    )



    status = Column(
        String(20),
        default="Success"
    )



    # ======================================
    # FRAUD DETECTION FIELDS
    # ======================================


    risk_score = Column(
        Integer,
        default=0
    )


    fraud_status = Column(
        String(30),
        default="Safe"
    )


    merchant_risk = Column(
        Integer,
        default=0
    )


    behavior_score = Column(
        Integer,
        default=0
    )


    fraud_reason = Column(
        String(500),
        nullable=True
    )


    fraud_alert = Column(
        String(200),
        nullable=True
    )



    # ======================================
    # ADVANCED FRAUD FEATURES
    # ======================================


    device_id = Column(
        String(100),
        nullable=True
    )


    ip_address = Column(
        String(50),
        nullable=True
    )


    is_blocked = Column(
        Boolean,
        default=False
    )


    verification_required = Column(
        Boolean,
        default=False
    )


    duplicate_transaction = Column(
        Boolean,
        default=False
    )



    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )



    user = relationship(
        "User",
        back_populates="transactions"
    )