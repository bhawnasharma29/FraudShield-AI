import os
import joblib
import pandas as pd


# ============================================================
# FIND TRAINED MODEL
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "fraud_model.pkl"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "amount",
    "merchant_risk",
    "location_change",
    "multiple_transactions",
    "behavior_score",
    "device_change",
    "ip_change",
    "duplicate_transaction",
    "night_transaction"
]


# ============================================================
# ML PREDICTION
# ============================================================

def predict_fraud(
    amount,
    merchant_risk,
    location_change,
    multiple_transactions,
    behavior_score,
    device_change,
    ip_change,
    duplicate_transaction,
    night_transaction
):

    data = {
        "amount": [amount],
        "merchant_risk": [merchant_risk],
        "location_change": [location_change],
        "multiple_transactions": [multiple_transactions],
        "behavior_score": [behavior_score],
        "device_change": [device_change],
        "ip_change": [ip_change],
        "duplicate_transaction": [duplicate_transaction],
        "night_transaction": [night_transaction]
    }

    df = pd.DataFrame(data)

    prediction = model.predict(df)[0]

    probabilities = model.predict_proba(df)[0]

    fraud_probability = probabilities[1]

    return {
        "ml_prediction": int(prediction),
        "fraud_probability": round(
            float(fraud_probability),
            4
        ),
        "fraud_percentage": round(
            float(fraud_probability * 100),
            2
        )
    }