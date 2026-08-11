from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

import models
import schemas

from fraud_detector import calculate_fraud
from ml_predictor import predict_fraud

from database import get_db
from auth import get_current_user


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


# =========================================================
# CREATE TRANSACTION
# =========================================================

@router.post(
    "/",
    response_model=schemas.TransactionResponse
)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    # =====================================================
    # PREVIOUS TRANSACTIONS
    # =====================================================

    previous_transactions = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == current_user.id
        )
        .order_by(
            models.Transaction.created_at.desc()
        )
        .limit(50)
        .all()
    )


    # =====================================================
    # RULE BASED FRAUD DETECTION
    # =====================================================

    fraud = calculate_fraud(

        amount=transaction.amount,

        merchant=transaction.merchant,

        location=transaction.location,

        device_id=transaction.device_id,

        ip_address=transaction.ip_address,

        previous_transactions=previous_transactions
    )


    merchant_risk = fraud["merchant_risk"]

    behavior_score = fraud["behavior_score"]


    # =====================================================
    # LOCATION CHANGE
    # =====================================================

    location_change = 0

    if previous_transactions:

        last_location = previous_transactions[0].location

        if (
            last_location
            and transaction.location
            and
            last_location.lower()
            != transaction.location.lower()
        ):

            location_change = 1


    # =====================================================
    # MULTIPLE TRANSACTIONS
    # =====================================================

    multiple_transactions = 0

    current_time = datetime.utcnow()

    recent_count = 0

    for previous in previous_transactions:

        if previous.created_at:

            difference = (
                current_time -
                previous.created_at
            )

            if difference <= timedelta(minutes=5):

                recent_count += 1


    if recent_count >= 3:

        multiple_transactions = 1


    # =====================================================
    # DEVICE CHANGE
    # =====================================================

    device_change = 0

    previous_devices = []

    for previous in previous_transactions:

        if previous.device_id:

            previous_devices.append(
                previous.device_id
            )


    if (
        transaction.device_id
        and
        transaction.device_id not in previous_devices
    ):

        device_change = 1


    # =====================================================
    # IP CHANGE
    # =====================================================

    ip_change = 0

    previous_ips = []

    for previous in previous_transactions:

        if previous.ip_address:

            previous_ips.append(
                previous.ip_address
            )


    if (
        transaction.ip_address
        and
        transaction.ip_address not in previous_ips
    ):

        ip_change = 1


    # =====================================================
    # DUPLICATE TRANSACTION
    # =====================================================

    duplicate_transaction = 0

    for previous in previous_transactions:

        if (
            previous.amount == transaction.amount
            and
            previous.merchant
            and
            transaction.merchant
            and
            previous.merchant.lower()
            ==
            transaction.merchant.lower()
        ):

            duplicate_transaction = 1

            break


    # =====================================================
    # NIGHT TRANSACTION
    # =====================================================

    current_hour = datetime.utcnow().hour

    night_transaction = 0

    if 0 <= current_hour <= 5:

        night_transaction = 1


    # =====================================================
    # MACHINE LEARNING PREDICTION
    # =====================================================

    ml_result = predict_fraud(

        amount=transaction.amount,

        merchant_risk=merchant_risk,

        location_change=location_change,

        multiple_transactions=multiple_transactions,

        behavior_score=behavior_score,

        device_change=device_change,

        ip_change=ip_change,

        duplicate_transaction=duplicate_transaction,

        night_transaction=night_transaction
    )


    ml_prediction = ml_result["ml_prediction"]

    fraud_percentage = ml_result["fraud_percentage"]


    # =====================================================
    # HYBRID RISK SCORE
    # =====================================================

    rule_score = fraud["risk_score"]

    ml_score = fraud_percentage

    final_risk_score = round(
        (rule_score * 0.60)
        +
        (ml_score * 0.40)
    )

    final_risk_score = min(
        final_risk_score,
        100
    )


    # =====================================================
    # FINAL DECISION
    # =====================================================

    if final_risk_score >= 60:

        fraud_status = "Fraud"

        transaction_status = "Blocked"

        fraud_alert = (
            "Immediate User Verification Required"
        )

        is_blocked = True

        verification_required = False


    elif final_risk_score >= 30:

        fraud_status = "Medium Risk"

        transaction_status = (
            "Pending Verification"
        )

        fraud_alert = (
            "Verify Transaction"
        )

        is_blocked = False

        verification_required = True


    else:

        fraud_status = "Safe"

        transaction_status = "Success"

        fraud_alert = (
            "Transaction Approved"
        )

        is_blocked = False

        verification_required = False


    # =====================================================
    # FRAUD REASONS
    # =====================================================

    reasons = list(
        fraud["fraud_reason"]
    )


    if ml_prediction == 1:

        reasons.append(
            "Machine Learning model detected high fraud probability"
        )


    if fraud_percentage >= 70:

        reasons.append(
            f"ML fraud probability: {fraud_percentage}%"
        )


    reasons = list(
        dict.fromkeys(reasons)
    )


    # =====================================================
    # SAVE TRANSACTION
    # =====================================================

    new_transaction = models.Transaction(

        user_id=current_user.id,

        amount=transaction.amount,

        transaction_type=(
            transaction.transaction_type
        ),

        merchant=(
            transaction.merchant
        ),

        location=(
            transaction.location
        ),

        status=transaction_status,

        risk_score=final_risk_score,

        fraud_status=fraud_status,

        fraud_reason=", ".join(
            reasons
        ),

        fraud_alert=fraud_alert,

        merchant_risk=merchant_risk,

        behavior_score=behavior_score,

        device_id=(
            transaction.device_id
        ),

        ip_address=(
            transaction.ip_address
        ),

        is_blocked=is_blocked,

        verification_required=(
            verification_required
        ),

        duplicate_transaction=(
            bool(duplicate_transaction)
        )
    )


    db.add(new_transaction)

    db.commit()

    db.refresh(new_transaction)

    return new_transaction


# =========================================================
# GET MY TRANSACTIONS
# =========================================================

@router.get(
    "/",
    response_model=list[schemas.TransactionResponse]
)
def get_my_transactions(

    db: Session = Depends(get_db),

    current_user: models.User = Depends(
        get_current_user
    )

):

    transactions = (

        db.query(models.Transaction)

        .filter(
            models.Transaction.user_id
            ==
            current_user.id
        )

        .order_by(
            models.Transaction.created_at.desc()
        )

        .all()

    )

    return transactions


# =========================================================
# GET FRAUD ALERTS
# =========================================================
#
# IMPORTANT:
# This route is BEFORE /{transaction_id}
# =========================================================

@router.get(
    "/fraud-alerts"
)
def get_fraud_alerts(

    db: Session = Depends(get_db),

    current_user: models.User = Depends(
        get_current_user
    )

):

    alerts = (

        db.query(models.Transaction)

        .filter(

            models.Transaction.user_id
            ==
            current_user.id,

            models.Transaction.fraud_status.in_(
                [
                    "Fraud",
                    "Medium Risk"
                ]
            )

        )

        .order_by(
            models.Transaction.created_at.desc()
        )

        .all()

    )


    result = []


    for transaction in alerts:

        result.append({

            "transaction_id":
                transaction.id,

            "amount":
                transaction.amount,

            "transaction_type":
                transaction.transaction_type,

            "merchant":
                transaction.merchant,

            "location":
                transaction.location,

            "status":
                transaction.status,

            "risk_score":
                transaction.risk_score,

            "fraud_status":
                transaction.fraud_status,

            "fraud_reason":
                transaction.fraud_reason,

            "fraud_alert":
                transaction.fraud_alert,

            "merchant_risk":
                transaction.merchant_risk,

            "behavior_score":
                transaction.behavior_score,

            "device_id":
                transaction.device_id,

            "ip_address":
                transaction.ip_address,

            "is_blocked":
                transaction.is_blocked,

            "verification_required":
                transaction.verification_required,

            "duplicate_transaction":
                transaction.duplicate_transaction,

            "created_at":
                transaction.created_at

        })


    return {

        "user_id":
            current_user.id,

        "total_alerts":
            len(result),

        "alerts":
            result

    }


# =========================================================
# GET SINGLE TRANSACTION
# =========================================================

@router.get(
    "/{transaction_id}",
    response_model=schemas.TransactionResponse
)
def get_transaction(

    transaction_id: int,

    db: Session = Depends(get_db),

    current_user: models.User = Depends(
        get_current_user
    )

):

    transaction = (

        db.query(models.Transaction)

        .filter(

            models.Transaction.id
            ==
            transaction_id,

            models.Transaction.user_id
            ==
            current_user.id

        )

        .first()

    )


    if transaction is None:

        raise HTTPException(

            status_code=404,

            detail="Transaction not found"

        )


    return transaction