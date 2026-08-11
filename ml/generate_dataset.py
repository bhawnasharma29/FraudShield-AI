import random
import csv

# ============================================================
# FRAUDSHIELD-AI REALISTIC DATASET GENERATOR
# ============================================================

OUTPUT_FILE = "fraud_dataset.csv"
TOTAL_RECORDS = 10000


def generate_record():

    # ========================================================
    # TRANSACTION AMOUNT
    # ========================================================

    amount = round(
        random.uniform(100, 100000),
        2
    )

    # ========================================================
    # MERCHANT RISK
    # ========================================================

    merchant_risk = random.choices(
        [0, 20, 40],
        weights=[65, 25, 10]
    )[0]

    # ========================================================
    # LOCATION CHANGE
    # ========================================================

    location_change = random.choices(
        [0, 1],
        weights=[82, 18]
    )[0]

    # ========================================================
    # MULTIPLE TRANSACTIONS
    # ========================================================

    multiple_transactions = random.choices(
        [0, 1],
        weights=[78, 22]
    )[0]

    # ========================================================
    # USER BEHAVIOR
    # ========================================================

    behavior_score = random.randint(0, 40)

    # ========================================================
    # DEVICE CHANGE
    # ========================================================

    device_change = random.choices(
        [0, 1],
        weights=[82, 18]
    )[0]

    # ========================================================
    # IP CHANGE
    # ========================================================

    ip_change = random.choices(
        [0, 1],
        weights=[82, 18]
    )[0]

    # ========================================================
    # DUPLICATE TRANSACTION
    # ========================================================

    duplicate_transaction = random.choices(
        [0, 1],
        weights=[90, 10]
    )[0]

    # ========================================================
    # NIGHT TRANSACTION
    # ========================================================

    night_transaction = random.choices(
        [0, 1],
        weights=[80, 20]
    )[0]

    # ========================================================
    # BASE RISK SCORE
    # ========================================================

    score = 0

    # High amount
    if amount > 50000:
        score += 30

    elif amount > 30000:
        score += 10

    # Merchant risk
    score += merchant_risk

    # Location
    if location_change:
        score += 20

    # Multiple transactions
    if multiple_transactions:
        score += 25

    # Behavior
    score += behavior_score

    # Device
    if device_change:
        score += 10

    # IP
    if ip_change:
        score += 10

    # Duplicate
    if duplicate_transaction:
        score += 20

    # Night
    if night_transaction:
        score += 10

    # ========================================================
    # REALISTIC COMBINATION EFFECTS
    # ========================================================

    # High amount + new location
    if amount > 50000 and location_change:
        score += 15

    # High amount + new device
    if amount > 50000 and device_change:
        score += 10

    # High amount + new IP
    if amount > 50000 and ip_change:
        score += 10

    # Risky merchant + new device
    if merchant_risk >= 40 and device_change:
        score += 15

    # Risky merchant + new IP
    if merchant_risk >= 40 and ip_change:
        score += 15

    # Multiple transactions + duplicate
    if multiple_transactions and duplicate_transaction:
        score += 15

    # Night + new device
    if night_transaction and device_change:
        score += 10

    # ========================================================
    # RANDOM NOISE
    # ========================================================
    #
    # Real-world fraud data is not perfectly deterministic.
    # A small amount of noise prevents the ML model from
    # simply memorizing one exact rule.
    # ========================================================

    noise = random.randint(-8, 8)

    score += noise

    # ========================================================
    # FRAUD LABEL
    # ========================================================

    # Use a small uncertain/borderline region.
    #
    # High score -> mostly fraud
    # Low score  -> mostly safe
    #
    # Borderline cases are intentionally mixed.

    if score >= 75:

        fraud = 1

    elif score <= 45:

        fraud = 0

    else:

        # Borderline transactions
        fraud = random.choices(
            [0, 1],
            weights=[60, 40]
        )[0]

    # ========================================================
    # RETURN RECORD
    # ========================================================

    return [
        amount,
        merchant_risk,
        location_change,
        multiple_transactions,
        behavior_score,
        device_change,
        ip_change,
        duplicate_transaction,
        night_transaction,
        fraud
    ]


# ============================================================
# DATASET COLUMNS
# ============================================================

columns = [
    "amount",
    "merchant_risk",
    "location_change",
    "multiple_transactions",
    "behavior_score",
    "device_change",
    "ip_change",
    "duplicate_transaction",
    "night_transaction",
    "fraud"
]


# ============================================================
# CREATE DATASET
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow(columns)

    for _ in range(TOTAL_RECORDS):

        writer.writerow(
            generate_record()
        )


# ============================================================
# COMPLETION MESSAGE
# ============================================================

print()
print("==============================================")
print("FraudShield-AI Dataset Generated Successfully")
print("==============================================")
print()
print(f"Records: {TOTAL_RECORDS}")
print(f"File: {OUTPUT_FILE}")
print()