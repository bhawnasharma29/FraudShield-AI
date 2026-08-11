from datetime import datetime, timedelta


# ==========================================
# MERCHANT RISK DATABASE
# ==========================================

HIGH_RISK_MERCHANTS = [
    "crypto",
    "casino",
    "betting",
    "gambling",
    "unknown"
]


MEDIUM_RISK_MERCHANTS = [
    "online marketplace",
    "international store",
    "new merchant"
]


# ==========================================
# MERCHANT RISK DETECTION
# ==========================================

def detect_merchant_risk(merchant):

    merchant = merchant.lower()


    for item in HIGH_RISK_MERCHANTS:

        if item in merchant:
            return 40


    for item in MEDIUM_RISK_MERCHANTS:

        if item in merchant:
            return 20


    return 0



# ==========================================
# LOCATION RISK DETECTION
# ==========================================

def detect_location_risk(
    location,
    previous_transactions
):

    if not previous_transactions:
        return 0


    last_location = previous_transactions[0].location


    if (
        last_location
        and
        last_location.lower()
        !=
        location.lower()
    ):

        return 20


    return 0



# ==========================================
# MULTIPLE TRANSACTION DETECTION
# ==========================================

def detect_multiple_transactions(
    previous_transactions
):

    current_time = datetime.utcnow()

    count = 0


    for transaction in previous_transactions:

        difference = (
            current_time -
            transaction.created_at
        )


        if difference <= timedelta(minutes=5):

            count += 1



    if count >= 3:

        return 25


    return 0



# ==========================================
# USER BEHAVIOR ANALYSIS
# ==========================================

def analyze_user_behavior(
    amount,
    device_id,
    ip_address,
    previous_transactions
):

    score = 0

    reasons = []


    if not previous_transactions:

        return score, reasons



    # Spending Pattern

    total = 0


    for transaction in previous_transactions:

        total += transaction.amount



    average_amount = (
        total /
        len(previous_transactions)
    )


    if amount > average_amount * 3:

        score += 15

        reasons.append(
            "Unusual spending behavior"
        )



    # Device Analysis

    devices = []


    for transaction in previous_transactions:

        if transaction.device_id:

            devices.append(
                transaction.device_id
            )


    if (
        device_id
        and
        device_id not in devices
    ):

        score += 10

        reasons.append(
            "New device detected"
        )



    # IP Analysis

    ips = []


    for transaction in previous_transactions:

        if transaction.ip_address:

            ips.append(
                transaction.ip_address
            )


    if (
        ip_address
        and
        ip_address not in ips
    ):

        score += 10

        reasons.append(
            "New IP address detected"
        )



    return score, reasons



# ==========================================
# DUPLICATE TRANSACTION
# ==========================================

def detect_duplicate_transaction(
    amount,
    merchant,
    previous_transactions
):

    for transaction in previous_transactions:


        if (
            transaction.amount == amount
            and
            transaction.merchant.lower()
            ==
            merchant.lower()
        ):

            return True


    return False



# ==========================================
# NIGHT TRANSACTION
# ==========================================

def detect_night_transaction():

    hour = datetime.utcnow().hour


    if 0 <= hour <= 5:

        return 10


    return 0



# ==========================================
# MAIN FRAUD ENGINE
# ==========================================

def calculate_fraud(
    amount,
    merchant,
    location,
    device_id,
    ip_address,
    previous_transactions=None
):


    if previous_transactions is None:

        previous_transactions = []



    risk_score = 0

    reasons = []



    merchant_risk = 0

    behavior_score = 0


    is_blocked = False

    verification_required = False

    duplicate_transaction = False



    # -------------------------------
    # Amount Detection
    # -------------------------------

    if amount > 50000:

        risk_score += 30

        reasons.append(
            "High transaction amount"
        )



    # -------------------------------
    # Merchant Risk
    # -------------------------------

    merchant_risk = detect_merchant_risk(
        merchant
    )


    if merchant_risk:

        risk_score += merchant_risk

        reasons.append(
            "Risky merchant category"
        )



    # -------------------------------
    # Location Detection
    # -------------------------------

    location_risk = detect_location_risk(
        location,
        previous_transactions
    )


    if location_risk:

        risk_score += location_risk

        reasons.append(
            "New location detected"
        )



    # -------------------------------
    # Multiple Transactions
    # -------------------------------

    multiple_risk = detect_multiple_transactions(
        previous_transactions
    )


    if multiple_risk:

        risk_score += multiple_risk

        reasons.append(
            "Multiple transactions in 5 minutes"
        )



    # -------------------------------
    # User Behavior
    # -------------------------------

    behavior_score, behavior_reasons = analyze_user_behavior(
        amount,
        device_id,
        ip_address,
        previous_transactions
    )


    if behavior_score:

        risk_score += behavior_score

        reasons.extend(
            behavior_reasons
        )



    # -------------------------------
    # Duplicate Check
    # -------------------------------

    duplicate_transaction = detect_duplicate_transaction(
        amount,
        merchant,
        previous_transactions
    )


    if duplicate_transaction:

        risk_score += 20

        reasons.append(
            "Duplicate transaction detected"
        )



    # -------------------------------
    # Night Risk
    # -------------------------------

    night_risk = detect_night_transaction()


    if night_risk:

        risk_score += night_risk

        reasons.append(
            "Night time transaction"
        )



    # -------------------------------
    # Combined Intelligence
    # -------------------------------


    if (
        amount > 50000
        and
        behavior_score >= 20
    ):

        risk_score += 20

        reasons.append(
            "High amount with new device and IP"
        )



    if (
        merchant_risk >= 40
        and
        behavior_score >= 10
    ):

        risk_score += 20

        reasons.append(
            "Risky merchant with unusual behavior"
        )



    if (
        location_risk >= 20
        and
        amount > 30000
    ):

        risk_score += 15

        reasons.append(
            "High amount from new location"
        )



    # Maximum Score

    risk_score = min(
        risk_score,
        100
    )



    # -------------------------------
    # Final Decision
    # -------------------------------

    if risk_score >= 60:


        fraud_status = "Fraud"

        fraud_alert = (
            "Immediate User Verification Required"
        )

        is_blocked = True



    elif risk_score >= 30:


        fraud_status = "Medium Risk"

        fraud_alert = (
            "Verify Transaction"
        )

        verification_required = True



    else:


        fraud_status = "Safe"

        fraud_alert = (
            "Transaction Approved"
        )



    return {


        "risk_score":
            risk_score,


        "fraud_status":
            fraud_status,


        "fraud_reason":
            reasons,


        "fraud_alert":
            fraud_alert,


        "merchant_risk":
            merchant_risk,


        "behavior_score":
            behavior_score,


        "is_blocked":
            is_blocked,


        "verification_required":
            verification_required,


        "duplicate_transaction":
            duplicate_transaction

    }