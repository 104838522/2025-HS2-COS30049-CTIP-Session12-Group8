# linear_regression_comparison.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
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
DATA_PATH = "processed_dataset_final.csv"
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
# 5) Linear Regression model (for comparison only)
# -------------------------------------------------
lin_reg = LinearRegression()
lin_reg.fit(X_train_scaled, y_train_resampled)

# 예측값은 연속값 → 0.5 기준으로 이진화
y_pred_lin = lin_reg.predict(X_test_scaled)
y_pred_lin_class = (y_pred_lin >= 0.5).astype(int)

# -------------------------------------------------
# 6) Predictions & Evaluation
# -------------------------------------------------
print("Linear Regression (as classifier) Evaluation:")
print(f"Accuracy: {accuracy_score(y_test, y_pred_lin_class):.2f}")
print(f"Precision: {precision_score(y_test, y_pred_lin_class):.2f}")
print(f"Recall: {recall_score(y_test, y_pred_lin_class):.2f}")
print(f"F1-Score: {f1_score(y_test, y_pred_lin_class):.2f}")

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_lin_class))

print("\nClassification Report:")
print(classification_report(y_test, y_pred_lin_class))

# -------------------------------------------------
# 7) Decision Boundary Plot (using first 2 features)
# -------------------------------------------------
X_train_2D = X_train_scaled[:, :2]
X_test_2D = X_test_scaled[:, :2]

lin_reg_2D = LinearRegression()
lin_reg_2D.fit(X_train_2D, y_train_resampled)

def plot_decision_boundary_reg(model, X, y, ax, title):
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                         np.arange(y_min, y_max, 0.1))

    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = (Z >= 0.5).astype(int)
    Z = Z.reshape(xx.shape)

    ax.contourf(xx, yy, Z, alpha=0.4, cmap='coolwarm')
    ax.scatter(X[:, 0], X[:, 1], c=y, cmap='coolwarm', edgecolors='k')
    ax.set_title(title)
    ax.set_xlabel('Feature 1')
    ax.set_ylabel('Feature 2')

fig, ax = plt.subplots(figsize=(6, 6))
plot_decision_boundary_reg(lin_reg_2D, X_test_2D, y_test, ax, "Linear Regression (threshold=0.5)")

plt.tight_layout()
plt.show()