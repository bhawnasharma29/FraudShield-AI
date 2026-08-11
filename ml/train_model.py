import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# ==========================================
# LOAD DATASET
# ==========================================

DATASET_FILE = "fraud_dataset.csv"
MODEL_FILE = "fraud_model.pkl"


df = pd.read_csv(DATASET_FILE)

print("Dataset loaded successfully")
print("Total records:", len(df))


# ==========================================
# FEATURES
# ==========================================

features = [
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


X = df[features]

y = df["fraud"]


# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("Training records:", len(X_train))
print("Testing records:", len(X_test))


# ==========================================
# RANDOM FOREST MODEL
# ==========================================

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    random_state=42,
    class_weight="balanced"
)


# ==========================================
# TRAIN MODEL
# ==========================================

print()
print("Training Random Forest model...")

model.fit(
    X_train,
    y_train
)


print("Training completed.")


# ==========================================
# PREDICTION
# ==========================================

y_pred = model.predict(X_test)


# ==========================================
# MODEL ACCURACY
# ==========================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


print()
print("====================================")
print("MODEL RESULTS")
print("====================================")

print(
    "Accuracy:",
    round(accuracy * 100, 2),
    "%"
)


print()
print("Classification Report:")
print(
    classification_report(
        y_test,
        y_pred
    )
)


# ==========================================
# FEATURE IMPORTANCE
# ==========================================

print()
print("====================================")
print("FEATURE IMPORTANCE")
print("====================================")

importance = model.feature_importances_

for feature, value in zip(
    features,
    importance
):

    print(
        f"{feature}: {value:.4f}"
    )


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    model,
    MODEL_FILE
)


print()
print("====================================")
print("MODEL SAVED")
print("====================================")

print(
    f"File: {MODEL_FILE}"
)