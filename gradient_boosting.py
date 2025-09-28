import pandas as pd
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from imblearn.over_sampling import RandomOverSampler

# -------------------------------------------------
# 1) Load dataset
# -------------------------------------------------
DATA_PATH = "../processed_dataset_final/processed_dataset_final.csv"
df = pd.read_csv(DATA_PATH, low_memory=False)

# -------------------------------------------------
# 2) Features & Target
# -------------------------------------------------
X = df.drop(columns=["id", "vulnerability_type", "label_encoded"])
y = df["label_encoded"]

# -------------------------------------------------
# 3) Train/Test split
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -------------------------------------------------
# 3-1) Oversampling
# -------------------------------------------------
ros = RandomOverSampler(sampling_strategy=0.67, random_state=42)
X_train_resampled, y_train_resampled = ros.fit_resample(X_train, y_train)

print("Original Train distribution:")
print(y_train.value_counts())
print("\nTrain distribution after oversampling:")
print(y_train_resampled.value_counts())
print("\nTest distribution:")
print(y_test.value_counts())

# -------------------------------------------------
# 4) Scaling (not required for trees, but keep consistent)
# -------------------------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)

# -------------------------------------------------
# 5) Gradient Boosting model (XGBoost)
# -------------------------------------------------
xgb_clf = XGBClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1
)

# --- Training with timer ---
start_train = time.time()
xgb_clf.fit(X_train_scaled, y_train_resampled)
train_time = time.time() - start_train
print(f"\n[INFO] Training completed in {train_time:.2f} seconds")

# --- Inference with timer ---
start_infer = time.time()
y_pred_xgb = xgb_clf.predict(X_test_scaled)
infer_time = time.time() - start_infer
print(f"[INFO] Inference (prediction) completed in {infer_time:.4f} seconds")

# -------------------------------------------------

print("\n=== Gradient Boosting (XGBoost) Evaluation ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_xgb):.2f}")
print(f"Precision: {precision_score(y_test, y_pred_xgb):.2f}")
print(f"Recall: {recall_score(y_test, y_pred_xgb):.2f}")
print(f"F1-Score: {f1_score(y_test, y_pred_xgb):.2f}")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_xgb))
print("\nClassification Report:")
print(classification_report(y_test, y_pred_xgb))

# -------------------------------------------------
# 6) Summarize results for comparison table
# -------------------------------------------------
def summarize_results(model_name, y_true, y_pred, train_time, infer_time):
    return {
        "Model": model_name,
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred),
        "Recall": recall_score(y_true, y_pred),
        "F1-Score": f1_score(y_true, y_pred),
        "Train Time (s)": train_time,
        "Inference Time (s)": infer_time
    }

rf_results = summarize_results("Gradient Boosting", y_test, y_pred_xgb, train_time, infer_time)

results_df = pd.DataFrame([rf_results])

print("\n=== Model Performance Summary ===")
print(results_df.round(3))
