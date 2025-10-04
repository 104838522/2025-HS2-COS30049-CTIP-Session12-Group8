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
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# -------------------------------------------------
# 1) Load dataset
# -------------------------------------------------
DATA_PATH = "processed_dataset_final.csv"
df = pd.read_csv(DATA_PATH, low_memory=False)

# -------------------------------------------------
# 2) Features & Target
# -------------------------------------------------
# Drop id, vulnerability_type, and label_encoded from features
X = df.drop(columns=["id", "vulnerability_type", "label_encoded"])
# Target variable: encoded label (safe/vulnerable)
y = df["label_encoded"]

# -------------------------------------------------
# 3) Train/Test split (80:20)
# -------------------------------------------------
# Stratify=y ensures class proportions are preserved in both train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -------------------------------------------------
# 3-1) Oversampling (only training set)
# -------------------------------------------------
# Oversample minority class in training data
# s minority:majority ratio = 5:5
ros = RandomOverSampler(sampling_strategy=0.5 , random_state=42)
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
# Standardize features: mean=0, std=1
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)

# -------------------------------------------------
# 5) Logistic Regression model (all features)
# -------------------------------------------------
# Train logistic regression on full feature set
log_reg = LogisticRegression(
    C=0.01,              # small C -> stronger regularization -> model becomes more conservative -> reduces false positives -> increases Precision
    penalty="l1",        # drives some weights to zero -> removes irrelevant features -> increases Precision
    solver="saga",       # supports l1 and is suitable for large/sparse data
    max_iter=5000,
    n_jobs=-1,           
    verbose=1
)
log_reg.fit(X_train_scaled, y_train_resampled)

# Get probability values (probability of the vulnerable class)
y_probs = log_reg.predict_proba(X_test_scaled)[:, 1]

# Apply custom threshold 
threshold = 0.55
y_pred = (y_probs >= threshold).astype(int)
#y_pred = log_reg.predict(X_test_scaled)

# -------------------------------------------------
# 6) Predictions & Evaluation
# -------------------------------------------------
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
# Reduce features to 2 principal components for plotting
pca = PCA(n_components=2)
X_train_pca = pca.fit_transform(X_train_scaled)
X_test_pca = pca.transform(X_test_scaled)

# Train logistic regression again on PCA-transformed features
log_reg_pca = LogisticRegression(C=0.01,max_iter=5000, solver="saga", random_state=42)
log_reg_pca.fit(X_train_pca, y_train_resampled)

# -------------------------------------------------
# 8) Decision Boundary Plot with PCA
# -------------------------------------------------
def plot_decision_boundary(model, X, y, ax, title):
    # Create a mesh grid across PCA components
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                         np.arange(y_min, y_max, 0.1))
    
    # Predict over the grid
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Plot decision regions
    ax.contourf(xx, yy, Z, alpha=0.4, cmap='coolwarm')
    ax.scatter(X[:, 0], X[:, 1], c=y, cmap='coolwarm', edgecolors='k')
    ax.set_title(title)
    ax.set_xlabel('PCA Component 1')
    ax.set_ylabel('PCA Component 2')

# Plot decision boundary
fig, ax = plt.subplots(figsize=(6, 6))
plot_decision_boundary(log_reg_pca, X_test_pca, y_test, ax, "Logistic Regression (PCA 2D)")
plt.tight_layout()
plt.show()