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
    # FETCH PREVIOUS TRANSACTIONS
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
    # RULE-BASED FRAUD ANALYSIS
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
    # PREVIOUS LOCATION DETECTION
    # =====================================================

    location_change = 0
    new_location = 0

    current_location = (
        transaction.location.strip()
        if transaction.location
        else ""
    )

    # Collect all previously used locations
    previous_locations = []

    for previous in previous_transactions:

        if previous.location:

            previous_location = (
                previous.location.strip().lower()
            )

            if previous_location:
                previous_locations.append(
                    previous_location
                )

    # Remove duplicate locations
    previous_locations = list(
        dict.fromkeys(previous_locations)
    )

    # -----------------------------------------------------
    # Check whether current location was used before
    # -----------------------------------------------------

    if current_location:

        if (
            current_location.lower()
            not in previous_locations
        ):

            new_location = 1

            location_change = 1

        elif previous_transactions:

            last_location = (
                previous_transactions[0].location
            )

            if (
                last_location
                and last_location.strip().lower()
                != current_location.lower()
            ):

                location_change = 1

    # =====================================================
    # MULTIPLE TRANSACTIONS DETECTION
    # LAST 5 MINUTES
    # =====================================================

    multiple_transactions = 0

    current_time = datetime.utcnow()

    recent_transactions = []

    for previous in previous_transactions:

        if previous.created_at:

            difference = (
                current_time -
                previous.created_at
            )

            if (
                timedelta(0)
                <= difference
                <= timedelta(minutes=5)
            ):

                recent_transactions.append(
                    previous
                )

    # Current transaction + previous transactions
    # If 3 or more previous transactions occurred
    # within 5 minutes, mark as suspicious.

    if len(recent_transactions) >= 3:

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
        and transaction.device_id not in previous_devices
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
        and transaction.ip_address not in previous_ips
    ):

        ip_change = 1

    # =====================================================
    # DUPLICATE TRANSACTION
    # =====================================================

    duplicate_transaction = 0

    for previous in previous_transactions:

        if (
            previous.amount == transaction.amount
            and previous.merchant
            and transaction.merchant
            and previous.merchant.lower()
            == transaction.merchant.lower()
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
    # FINAL FRAUD STATUS
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

        fraud_alert = "Verify Transaction"

        is_blocked = False

        verification_required = True

    else:

        fraud_status = "Safe"

        transaction_status = "Success"

        fraud_alert = "Transaction Approved"

        is_blocked = False

        verification_required = False

    # =====================================================
    # FRAUD REASONS
    # =====================================================

    reasons = list(
        fraud["fraud_reason"]
    )

    # -----------------------------------------------------
    # Previous / New Location Reason
    # -----------------------------------------------------

    if new_location == 1:

        reasons.append(
            f"Transaction from a new location: "
            f"{transaction.location}"
        )

    elif location_change == 1:

        reasons.append(
            f"Location changed from previous transaction "
            f"to {transaction.location}"
        )

    # -----------------------------------------------------
    # Multiple Transaction Reason
    # -----------------------------------------------------

    if multiple_transactions == 1:

        reasons.append(
            "Multiple transactions detected within 5 minutes"
        )

    # -----------------------------------------------------
    # Device Change Reason
    # -----------------------------------------------------

    if device_change == 1:

        reasons.append(
            "Transaction made from a previously unused device"
        )

    # -----------------------------------------------------
    # IP Change Reason
    # -----------------------------------------------------

    if ip_change == 1:

        reasons.append(
            "Transaction detected from a previously unused IP address"
        )

    # -----------------------------------------------------
    # Duplicate Transaction Reason
    # -----------------------------------------------------

    if duplicate_transaction == 1:

        reasons.append(
            "Possible duplicate transaction detected"
        )

    # -----------------------------------------------------
    # Night Transaction Reason
    # -----------------------------------------------------

    if night_transaction == 1:

        reasons.append(
            "Transaction occurred during unusual night hours"
        )

    # -----------------------------------------------------
    # Machine Learning Reason
    # -----------------------------------------------------

    if ml_prediction == 1:

        reasons.append(
            "Machine Learning model detected high fraud probability"
        )

    if fraud_percentage >= 70:

        reasons.append(
            f"ML fraud probability: {fraud_percentage}%"
        )

    # Remove duplicate reasons
    reasons = list(
        dict.fromkeys(reasons)
    )

    # =====================================================
    # SAVE TRANSACTION
    # =====================================================

    new_transaction = models.Transaction(

        user_id=current_user.id,

        amount=transaction.amount,

        transaction_type=transaction.transaction_type,

        merchant=transaction.merchant,

        location=transaction.location,

        status=transaction_status,

        risk_score=final_risk_score,

        fraud_status=fraud_status,

        fraud_reason=", ".join(
            reasons
        ),

        fraud_alert=fraud_alert,

        merchant_risk=merchant_risk,

        behavior_score=behavior_score,

        device_id=transaction.device_id,

        ip_address=transaction.ip_address,

        is_blocked=is_blocked,

        verification_required=verification_required,

        duplicate_transaction=bool(
            duplicate_transaction
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
            == current_user.id
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

# IMPORTANT:
# FRAUD-ALERTS MUST COME BEFORE /{transaction_id}

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
            == current_user.id,

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

# IMPORTANT:
# THIS MUST BE THE LAST GET ROUTE

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
            == transaction_id,

            models.Transaction.user_id
            == current_user.id
        )
        .first()
    )

    if transaction is None:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction