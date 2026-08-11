from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models

from database import get_db
from auth import get_current_user


# ============================================================
# DASHBOARD ROUTER
# ============================================================

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ============================================================
# 1. BASIC DASHBOARD
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

    # --------------------------------------------------------
    # BASIC COUNTS
    # --------------------------------------------------------

    total_transactions = len(transactions)

    fraud_transactions = 0

    safe_transactions = 0

    blocked_transactions = 0

    total_risk = 0


    # --------------------------------------------------------
    # PROCESS TRANSACTIONS
    # --------------------------------------------------------

    for transaction in transactions:

        total_risk += transaction.risk_score or 0


        # Fraud / Safe

        if transaction.fraud_status == "Fraud":

            fraud_transactions += 1

        else:

            safe_transactions += 1


        # Blocked

        if getattr(transaction, "is_blocked", False):

            blocked_transactions += 1


    # --------------------------------------------------------
    # AVERAGE RISK
    # --------------------------------------------------------

    if total_transactions > 0:

        average_risk = (
            total_risk /
            total_transactions
        )

    else:

        average_risk = 0


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "user_id":
            current_user.id,

        "total_transactions":
            total_transactions,

        "fraud_transactions":
            fraud_transactions,

        "safe_transactions":
            safe_transactions,

        "blocked_transactions":
            blocked_transactions,

        "average_risk_score":
            round(
                average_risk,
                2
            )

    }


# ============================================================
# 2. GENERAL ANALYTICS
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


    # --------------------------------------------------------
    # TOTAL TRANSACTIONS
    # --------------------------------------------------------

    total_transactions = len(transactions)


    # --------------------------------------------------------
    # FRAUD TRANSACTIONS
    # --------------------------------------------------------

    fraud_transactions = [

        transaction

        for transaction in transactions

        if transaction.fraud_status == "Fraud"

    ]


    # --------------------------------------------------------
    # SAFE TRANSACTIONS
    # --------------------------------------------------------

    safe_transactions = [

        transaction

        for transaction in transactions

        if transaction.fraud_status != "Fraud"

    ]


    # --------------------------------------------------------
    # BLOCKED TRANSACTIONS
    # --------------------------------------------------------

    blocked_transactions = [

        transaction

        for transaction in transactions

        if getattr(
            transaction,
            "is_blocked",
            False
        )

    ]


    # --------------------------------------------------------
    # TOTAL AMOUNT
    # --------------------------------------------------------

    total_amount = sum(

        transaction.amount or 0

        for transaction in transactions

    )


    # --------------------------------------------------------
    # FRAUD AMOUNT
    # --------------------------------------------------------

    fraud_amount = sum(

        transaction.amount or 0

        for transaction in fraud_transactions

    )


    # --------------------------------------------------------
    # SAFE AMOUNT
    # --------------------------------------------------------

    safe_amount = sum(

        transaction.amount or 0

        for transaction in safe_transactions

    )


    # --------------------------------------------------------
    # AVERAGE RISK
    # --------------------------------------------------------

    if total_transactions > 0:

        average_risk = (

            sum(
                transaction.risk_score or 0
                for transaction in transactions
            )

            / total_transactions

        )

    else:

        average_risk = 0


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "user_id":
            current_user.id,

        "total_transactions":
            total_transactions,

        "fraud_transactions":
            len(fraud_transactions),

        "safe_transactions":
            len(safe_transactions),

        "blocked_transactions":
            len(blocked_transactions),

        "total_amount":
            total_amount,

        "fraud_amount":
            fraud_amount,

        "safe_amount":
            safe_amount,

        "average_risk_score":
            round(
                average_risk,
                2
            )

    }


# ============================================================
# 3. MERCHANT + LOCATION FRAUD ANALYSIS
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


    # ========================================================
    # MERCHANT DATA
    # ========================================================

    merchant_data = defaultdict(
        lambda: {

            "total_transactions": 0,

            "fraud_transactions": 0,

            "safe_transactions": 0,

            "total_amount": 0,

            "fraud_amount": 0

        }
    )


    # ========================================================
    # LOCATION DATA
    # ========================================================

    location_data = defaultdict(
        lambda: {

            "total_transactions": 0,

            "fraud_transactions": 0,

            "safe_transactions": 0,

            "total_amount": 0,

            "fraud_amount": 0

        }
    )


    # ========================================================
    # PROCESS TRANSACTIONS
    # ========================================================

    for transaction in transactions:


        # ----------------------------------------------------
        # MERCHANT
        # ----------------------------------------------------

        merchant = (
            transaction.merchant
            if transaction.merchant
            else "Unknown"
        )


        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        location = (
            transaction.location
            if transaction.location
            else "Unknown"
        )


        # ----------------------------------------------------
        # AMOUNT
        # ----------------------------------------------------

        amount = (
            transaction.amount
            if transaction.amount
            else 0
        )


        # ----------------------------------------------------
        # FRAUD CHECK
        # ----------------------------------------------------

        is_fraud = (

            transaction.fraud_status
            == "Fraud"

        )


        # ====================================================
        # MERCHANT ANALYSIS
        # ====================================================

        merchant_data[
            merchant
        ][
            "total_transactions"
        ] += 1


        merchant_data[
            merchant
        ][
            "total_amount"
        ] += amount


        if is_fraud:

            merchant_data[
                merchant
            ][
                "fraud_transactions"
            ] += 1


            merchant_data[
                merchant
            ][
                "fraud_amount"
            ] += amount

        else:

            merchant_data[
                merchant
            ][
                "safe_transactions"
            ] += 1


        # ====================================================
        # LOCATION ANALYSIS
        # ====================================================

        location_data[
            location
        ][
            "total_transactions"
        ] += 1


        location_data[
            location
        ][
            "total_amount"
        ] += amount


        if is_fraud:

            location_data[
                location
            ][
                "fraud_transactions"
            ] += 1


            location_data[
                location
            ][
                "fraud_amount"
            ] += amount

        else:

            location_data[
                location
            ][
                "safe_transactions"
            ] += 1


    # ========================================================
    # MERCHANT RESPONSE
    # ========================================================

    merchants = []


    for merchant, data in merchant_data.items():

        fraud_rate = (

            data["fraud_transactions"]

            / data["total_transactions"]

            * 100

            if data["total_transactions"] > 0

            else 0

        )


        merchants.append({

            "merchant":
                merchant,

            "total_transactions":
                data[
                    "total_transactions"
                ],

            "fraud_transactions":
                data[
                    "fraud_transactions"
                ],

            "safe_transactions":
                data[
                    "safe_transactions"
                ],

            "total_amount":
                data[
                    "total_amount"
                ],

            "fraud_amount":
                data[
                    "fraud_amount"
                ],

            "fraud_rate":
                round(
                    fraud_rate,
                    2
                )

        })


    # ========================================================
    # LOCATION RESPONSE
    # ========================================================

    locations = []


    for location, data in location_data.items():

        fraud_rate = (

            data["fraud_transactions"]

            / data["total_transactions"]

            * 100

            if data["total_transactions"] > 0

            else 0

        )


        locations.append({

            "location":
                location,

            "total_transactions":
                data[
                    "total_transactions"
                ],

            "fraud_transactions":
                data[
                    "fraud_transactions"
                ],

            "safe_transactions":
                data[
                    "safe_transactions"
                ],

            "total_amount":
                data[
                    "total_amount"
                ],

            "fraud_amount":
                data[
                    "fraud_amount"
                ],

            "fraud_rate":
                round(
                    fraud_rate,
                    2
                )

        })


    # ========================================================
    # SORT HIGH-RISK FIRST
    # ========================================================

    merchants.sort(

        key=lambda x:
            x["fraud_transactions"],

        reverse=True

    )


    locations.sort(

        key=lambda x:
            x["fraud_transactions"],

        reverse=True

    )


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {

        "user_id":
            current_user.id,

        "merchant_analysis":
            merchants,

        "location_analysis":
            locations

    }