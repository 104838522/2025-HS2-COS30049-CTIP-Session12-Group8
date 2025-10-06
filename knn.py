# =================================================
# KNN Implementation for Vulnerability Classification
# =================================================
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
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
# 2) Define Features & Target
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
# 4) Oversampling (1:1 ratio)
# -------------------------------------------------
# This perfectly balances safe/vulnerable classes for fairer model training
ros = RandomOverSampler(sampling_strategy=1.0, random_state=42)
X_train_resampled, y_train_resampled = ros.fit_resample(X_train, y_train)

print("Original Train distribution:")
print(y_train.value_counts())
print("\nAfter Oversampling (1:1 ratio):")
print(y_train_resampled.value_counts())
print("\nTest distribution (original ratio preserved):")
print(y_test.value_counts())

# -------------------------------------------------
# 5) Feature Scaling
# -------------------------------------------------
# Standardization is essential for KNN since it relies on distance metrics
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)

# -------------------------------------------------
# 6) KNN Model Training
# -------------------------------------------------
# Parameters manually optimized based on prior experiments
knn = KNeighborsClassifier(
    n_neighbors=7,          # slightly higher neighbors -> smoother decision boundary
    weights='distance',     # closer neighbors have stronger influence
    metric='cosine',        # better for TF-IDF-like high-dimensional data
    n_jobs=-1
)
knn.fit(X_train_scaled, y_train_resampled)
# -------------------------------------------------
# 7) Predictions & Evaluation
# -------------------------------------------------
y_pred = knn.predict(X_test_scaled)

print("\nKNN Evaluation Results:")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
print(f"Precision: {precision_score(y_test, y_pred):.2f}")
print(f"Recall: {recall_score(y_test, y_pred):.2f}")
print(f"F1-Score: {f1_score(y_test, y_pred):.2f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -------------------------------------------------
# 8) PCA for Visualization (reduce to 2D)
# -------------------------------------------------
pca = PCA(n_components=2)
X_train_pca = pca.fit_transform(X_train_scaled)
X_test_pca = pca.transform(X_test_scaled)

# Retrain model on PCA-reduced data for visualization
knn_pca = KNeighborsClassifier(
    n_neighbors=7,
    weights='distance',
    metric='cosine'
)
knn_pca.fit(X_train_pca, y_train_resampled)

# -------------------------------------------------
# 9) Decision Boundary Plot (PCA 2D)
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
plot_decision_boundary(knn_pca, X_test_pca, y_test, ax, "KNN (Optimized, PCA 2D)")
plt.tight_layout()
plt.show()



