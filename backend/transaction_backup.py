from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas

from fraud_detector import calculate_fraud

from database import get_db
from auth import get_current_user


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)



# ==========================================
# CREATE TRANSACTION
# ==========================================

@router.post(
    "/",
    response_model=schemas.TransactionResponse
)
def create_transaction(

    transaction: schemas.TransactionCreate,

    db: Session = Depends(get_db),

    current_user: models.User = Depends(get_current_user)

):


    # ======================================
    # FETCH PREVIOUS TRANSACTIONS
    # ======================================

    previous_transactions = (

        db.query(models.Transaction)

        .filter(
            models.Transaction.user_id
            ==
            current_user.id
        )

        .order_by(
            models.Transaction.created_at.desc()
        )

        .limit(50)

        .all()

    )



    # ======================================
    # FRAUD ANALYSIS
    # ======================================

    fraud = calculate_fraud(

        amount=transaction.amount,

        merchant=transaction.merchant,

        location=transaction.location,

        device_id=transaction.device_id,

        ip_address=transaction.ip_address,

        previous_transactions=previous_transactions

    )



    # ======================================
    # TRANSACTION STATUS
    # ======================================


    if fraud["is_blocked"]:


        transaction_status = "Blocked"



    elif fraud["verification_required"]:


        transaction_status = (
            "Pending Verification"
        )



    else:


        transaction_status = "Success"




    # ======================================
    # SAVE TRANSACTION
    # ======================================

    new_transaction = models.Transaction(


        user_id=current_user.id,


        amount=transaction.amount,


        transaction_type=
        transaction.transaction_type,


        merchant=
        transaction.merchant,


        location=
        transaction.location,


        status=
        transaction_status,



        # Fraud Details

        risk_score=
        fraud["risk_score"],


        fraud_status=
        fraud["fraud_status"],



        fraud_reason=
        ", ".join(
            fraud["fraud_reason"]
        ),



        fraud_alert=
        fraud["fraud_alert"],



        merchant_risk=
        fraud["merchant_risk"],



        behavior_score=
        fraud["behavior_score"],



        # Device Details

        device_id=
        transaction.device_id,



        ip_address=
        transaction.ip_address,



        # Security Flags

        is_blocked=
        fraud["is_blocked"],



        verification_required=
        fraud["verification_required"],



        duplicate_transaction=
        fraud["duplicate_transaction"]

    )



    db.add(new_transaction)


    db.commit()


    db.refresh(new_transaction)



    return new_transaction





# ==========================================
# GET MY TRANSACTIONS
# ==========================================

@router.get(
    "/",
    response_model=list[schemas.TransactionResponse]
)
def get_my_transactions(

    db: Session = Depends(get_db),

    current_user: models.User = Depends(get_current_user)

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





# ==========================================
# GET SINGLE TRANSACTION
# ==========================================

@router.get(
    "/{transaction_id}",
    response_model=schemas.TransactionResponse
)
def get_transaction(

    transaction_id: int,

    db: Session = Depends(get_db),

    current_user: models.User = Depends(get_current_user)

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