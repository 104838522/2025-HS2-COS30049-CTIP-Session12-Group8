# compare_logistic_linear.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from imblearn.over_sampling import RandomOverSampler
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1) Load dataset
# -------------------------------------------------
DATA_PATH = "processed_dataset_final4.csv"
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
# 3-1) Oversampling (6:4 ratio)
# -------------------------------------------------
ros = RandomOverSampler(sampling_strategy=0.67, random_state=42)
X_train_resampled, y_train_resampled = ros.fit_resample(X_train, y_train)

print("Original Train distribution:")
print(y_train.value_counts())

print("\nTrain distribution after oversampling:")
print(y_train_resampled.value_counts())

print("\nTest distribution (7:3 ratio preserved):")
print(y_test.value_counts())

# -------------------------------------------------
# 4) Scale features
# -------------------------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)

# -------------------------------------------------
# 5) Logistic Regression model
# -------------------------------------------------
log_reg = LogisticRegression(
    max_iter=5000,
    solver="saga",
    n_jobs=-1,
    verbose=1
)
log_reg.fit(X_train_scaled, y_train_resampled)
y_pred_logistic = log_reg.predict(X_test_scaled)

print("\n=== Logistic Regression Evaluation ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_logistic):.2f}")
print(f"Precision: {precision_score(y_test, y_pred_logistic):.2f}")
print(f"Recall: {recall_score(y_test, y_pred_logistic):.2f}")
print(f"F1-Score: {f1_score(y_test, y_pred_logistic):.2f}")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_logistic))
print("\nClassification Report:")
print(classification_report(y_test, y_pred_logistic))

# -------------------------------------------------
# 6) Linear Regression model (for comparison only)
# -------------------------------------------------
lin_reg = LinearRegression()
lin_reg.fit(X_train_scaled, y_train_resampled)

y_pred_lin = lin_reg.predict(X_test_scaled)
y_pred_lin_class = (y_pred_lin >= 0.5).astype(int)

print("\n=== Linear Regression (as classifier) Evaluation ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_lin_class):.2f}")
print(f"Precision: {precision_score(y_test, y_pred_lin_class):.2f}")
print(f"Recall: {recall_score(y_test, y_pred_lin_class):.2f}")
print(f"F1-Score: {f1_score(y_test, y_pred_lin_class):.2f}")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_lin_class))
print("\nClassification Report:")
print(classification_report(y_test, y_pred_lin_class))

# -------------------------------------------------
# 7) 성능 비교 결과 표로 정리
# -------------------------------------------------
def summarize_results(model_name, y_true, y_pred):
    return {
        "Model": model_name,
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred),
        "Recall": recall_score(y_true, y_pred),
        "F1-Score": f1_score(y_true, y_pred)
    }

logistic_results = summarize_results("Logistic Regression", y_test, y_pred_logistic)
linear_results = summarize_results("Linear Regression", y_test, y_pred_lin_class)

results_df = pd.DataFrame([logistic_results, linear_results])

print("\n=== Model Performance Comparison ===")
print(results_df.round(3))