# =================================================
# Logistic Regression Implementation (Same Condition as KNN)
# =================================================
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
from imblearn.over_sampling import RandomOverSampler
from sklearn.decomposition import PCA
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
# 3) Train/Test Split (80:20)
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -------------------------------------------------
# 3-1) Logistic Oversampling
# -------------------------------------------------
ros = RandomOverSampler(sampling_strategy=0.5, random_state=42)
X_train_resampled, y_train_resampled = ros.fit_resample(X_train, y_train)

print("Original Train distribution:")
print(y_train.value_counts())

print("\nTrain distribution after oversampling (5:5 ratio):")
print(y_train_resampled.value_counts())

print("\nTest distribution (original ratio preserved 7:3):")
print(y_test.value_counts())

# -------------------------------------------------
# 4) Feature Scaling
# -------------------------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)

# -------------------------------------------------
# 5) Logistic Regression Model Training
# -------------------------------------------------
log_reg = LogisticRegression(
    C=0.01,               # stronger regularization (helps prevent overfitting)
    penalty="l1",         # feature selection through sparsity
    solver="saga",        # supports l1 and works with large datasets
    max_iter=5000,
    n_jobs=-1,
    verbose=0
)
log_reg.fit(X_train_scaled, y_train_resampled)

# -------------------------------------------------
# 6) Predictions & Evaluation
# -------------------------------------------------
# Use default threshold (0.5)
y_pred = log_reg.predict(X_test_scaled)

print("\nLogistic Regression Evaluation:")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
print(f"Precision: {precision_score(y_test, y_pred):.2f}")
print(f"Recall: {recall_score(y_test, y_pred):.2f}")
print(f"F1-Score: {f1_score(y_test, y_pred):.2f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -------------------------------------------------
# 7) PCA for Visualization (reduce to 2D)
# -------------------------------------------------
pca = PCA(n_components=2)
X_train_pca = pca.fit_transform(X_train_scaled)
X_test_pca = pca.transform(X_test_scaled)

log_reg_pca = LogisticRegression(C=0.01, solver="saga", max_iter=5000, random_state=42)
log_reg_pca.fit(X_train_pca, y_train_resampled)

# -------------------------------------------------
# 8) Decision Boundary Plot (PCA 2D)
# -------------------------------------------------
def plot_decision_boundary(model, X, y, ax, title):
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                         np.arange(y_min, y_max, 0.1))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    ax.contourf(xx, yy, Z, alpha=0.4, cmap='coolwarm')
    ax.scatter(X[:, 0], X[:, 1], c=y, cmap='coolwarm', edgecolors='k', s=20)
    ax.set_title(title)
    ax.set_xlabel('PCA Component 1')
    ax.set_ylabel('PCA Component 2')

fig, ax = plt.subplots(figsize=(6, 6))
plot_decision_boundary(log_reg_pca, X_test_pca, y_test, ax, "Logistic Regression (PCA 2D)")
plt.tight_layout()
plt.show()
