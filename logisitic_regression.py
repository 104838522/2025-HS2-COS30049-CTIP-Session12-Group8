import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from imblearn.over_sampling import RandomOverSampler #5:5
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
# 3-1) Train data 6:4 
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
# 5) Logistic Regression model (robust version)
# -------------------------------------------------
log_reg = LogisticRegression(
    max_iter=5000,        # 수렴을 위한 충분한 반복
    solver="saga",        # 대규모 데이터 적합
    n_jobs=-1,
    verbose=1             # 학습 진행 상황 출력
)
log_reg.fit(X_train_scaled,y_train_resampled)

y_pred = log_reg.predict(X_test_scaled)

# -------------------------------------------------
# 6) Predictions & Evaluation
# -------------------------------------------------
print("Logistic Regression Evaluation:")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
print(f"Precision: {precision_score(y_test, y_pred):.2f}")
print(f"Recall: {recall_score(y_test, y_pred):.2f}")
print(f"F1-Score: {f1_score(y_test, y_pred):.2f}")

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred)) 
#   0   1
#0 [TN, FP]
#1 [FN, TP]]

print("\nClassification Report:")
print(classification_report(y_test, y_pred))
# -------------------------------------------------
# 7) Decision Boundary Plot (using first 2 features)
# -------------------------------------------------
def plot_decision_boundary(model, X, y, ax, title):
    # Create mesh grid for the first two features
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                         np.arange(y_min, y_max, 0.1))

    # Predict classes over the mesh grid
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Plot decision boundary
    ax.contourf(xx, yy, Z, alpha=0.4, cmap='coolwarm')
    ax.scatter(X[:, 0], X[:, 1], c=y, cmap='coolwarm', edgecolors='k')
    ax.set_title(title)
    ax.set_xlabel('Feature 1')
    ax.set_ylabel('Feature 2')


# Only first two features for visualization
X_train_2D = X_train_scaled[:, :2]
X_test_2D = X_test_scaled[:, :2]

# Train Logistic Regression with 2 features
log_reg_2D = LogisticRegression(random_state=42, max_iter=5000, solver="saga")
log_reg_2D.fit(X_train_2D, y_train_resampled)

# Plot decision boundary for Logistic Regression
fig, ax = plt.subplots(figsize=(6, 6))
plot_decision_boundary(log_reg_2D, X_test_2D, y_test, ax, "Logistic Regression")

plt.tight_layout()
plt.show()