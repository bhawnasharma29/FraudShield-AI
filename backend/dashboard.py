from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models

from database import get_db
from auth import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ============================================================
# BASIC DASHBOARD
# ============================================================

@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    transactions = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == current_user.id
        )
        .all()
    )

    total_transactions = len(transactions)

    fraud_transactions = 0
    safe_transactions = 0
    blocked_transactions = 0

    total_risk = 0

    for transaction in transactions:

        total_risk += transaction.risk_score or 0

        if transaction.fraud_status == "Fraud":
            fraud_transactions += 1
        else:
            safe_transactions += 1

        if getattr(transaction, "is_blocked", False):
            blocked_transactions += 1

    if total_transactions > 0:
        average_risk = total_risk / total_transactions
    else:
        average_risk = 0

    return {
        "user_id": current_user.id,
        "total_transactions": total_transactions,
        "fraud_transactions": fraud_transactions,
        "safe_transactions": safe_transactions,
        "blocked_transactions": blocked_transactions,
        "average_risk_score": round(average_risk, 2)
    }


# ============================================================
# GENERAL ANALYTICS
# ============================================================

@router.get("/analytics")
def analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    transactions = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == current_user.id
        )
        .all()
    )

    total_transactions = len(transactions)

    fraud_transactions = [
        t for t in transactions
        if t.fraud_status == "Fraud"
    ]

    safe_transactions = [
        t for t in transactions
        if t.fraud_status != "Fraud"
    ]

    blocked_transactions = [
        t for t in transactions
        if getattr(t, "is_blocked", False)
    ]

    total_amount = sum(
        t.amount or 0
        for t in transactions
    )

    fraud_amount = sum(
        t.amount or 0
        for t in fraud_transactions
    )

    safe_amount = sum(
        t.amount or 0
        for t in safe_transactions
    )

    average_risk = (
        sum(t.risk_score or 0 for t in transactions)
        / total_transactions
        if total_transactions > 0
        else 0
    )

    return {
        "user_id": current_user.id,
        "total_transactions": total_transactions,
        "fraud_transactions": len(fraud_transactions),
        "safe_transactions": len(safe_transactions),
        "blocked_transactions": len(blocked_transactions),
        "total_amount": total_amount,
        "fraud_amount": fraud_amount,
        "safe_amount": safe_amount,
        "average_risk_score": round(average_risk, 2)
    }


# ============================================================
# MERCHANT + LOCATION FRAUD ANALYSIS
# ============================================================

@router.get("/fraud-analysis")
def fraud_analysis(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    transactions = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == current_user.id
        )
        .all()
    )

    merchant_data = {}
    location_data = {}

    for transaction in transactions:

        merchant = transaction.merchant or "Unknown"
        location = transaction.location or "Unknown"
        amount = transaction.amount or 0

        is_fraud = transaction.fraud_status == "Fraud"


        # ====================================================
        # MERCHANT
        # ====================================================

        if merchant not in merchant_data:

            merchant_data[merchant] = {
                "total_transactions": 0,
                "fraud_transactions": 0,
                "safe_transactions": 0,
                "total_amount": 0,
                "fraud_amount": 0
            }

        merchant_data[merchant]["total_transactions"] += 1

        merchant_data[merchant]["total_amount"] += amount

        if is_fraud:

            merchant_data[merchant]["fraud_transactions"] += 1

            merchant_data[merchant]["fraud_amount"] += amount

        else:

            merchant_data[merchant]["safe_transactions"] += 1


        # ====================================================
        # LOCATION
        # ====================================================

        if location not in location_data:

            location_data[location] = {
                "total_transactions": 0,
                "fraud_transactions": 0,
                "safe_transactions": 0,
                "total_amount": 0,
                "fraud_amount": 0
            }

        location_data[location]["total_transactions"] += 1

        location_data[location]["total_amount"] += amount

        if is_fraud:

            location_data[location]["fraud_transactions"] += 1

            location_data[location]["fraud_amount"] += amount

        else:

            location_data[location]["safe_transactions"] += 1


    return {

        "user_id": current_user.id,

        "merchant_analysis": merchant_data,

        "location_analysis": location_data

    }