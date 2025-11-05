# KNN Implementation for Vulnerability Classification (without language features)
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
import joblib
import os
import shutil

# -------------------------------------------------
# 1) Load dataset
DATA_PATH = "./data/processed_dataset_final.csv"
df = pd.read_csv(DATA_PATH, low_memory=False)

# -------------------------------------------------
# 2) Define Features & Target
# Remove ID, label, vulnerability_type, and language columns
lang_cols = [col for col in df.columns if col.startswith("lang_")]
X = df.drop(columns=["id", "vulnerability_type", "label_encoded"] + lang_cols)
y = df["label_encoded"]

print(f"Feature count (TF-IDF only): {X.shape[1]}")

# -------------------------------------------------
# 3) Train/Test Split (80:20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -------------------------------------------------
# 4) Oversampling (1:1 ratio)
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
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)

# -------------------------------------------------
# 6) KNN Model Training
knn = KNeighborsClassifier(
    n_neighbors=7,
    weights='distance',
    metric='euclidean',
    n_jobs=-1
)
knn.fit(X_train_scaled, y_train_resampled)

# -------------------------------------------------
# 7) Predictions & Evaluation
y_pred = knn.predict(X_test_scaled)

print("\nKNN Evaluation Results:")
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.3f}")
print(f"Precision: {precision_score(y_test, y_pred):.3f}")
print(f"Recall:    {recall_score(y_test, y_pred):.3f}")
print(f"F1-Score:  {f1_score(y_test, y_pred):.3f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -------------------------------------------------
# 8) Save Model and Scaler for FastAPI Inference
# -------------------------------------------------
os.makedirs("./models", exist_ok=True)

joblib.dump(scaler, "./models/knn_scaler.joblib")
joblib.dump(knn, "./models/knn_model.joblib")
print("Saved scaler.joblib & knn_model.joblib inside backend/models")

src_vec = "./vectorizer.pkl"
dst_vec = "./models/vectorizer.joblib"

if os.path.exists(src_vec):
    shutil.copy(src_vec, dst_vec)
    print("Copied vectorizer.pkl to backend/models/vectorizer.joblib")
else:
    print("vectorizer.pkl not found – make sure dataprocess.py was run before training")
