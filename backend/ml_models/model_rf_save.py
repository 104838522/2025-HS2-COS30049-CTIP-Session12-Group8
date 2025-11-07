import pandas as pd
import numpy as np
import os
import joblib
import shutil
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor

# Load dataset
current_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(current_dir, "../data/processed_dataset_final.csv")
df = pd.read_csv(DATA_PATH, low_memory=False)

# Features & Target
lang_cols = [col for col in df.columns if col.startswith("lang_")]
X = df.drop(columns=["id", "vulnerability_type", "label_encoded"] + lang_cols)
y_class = df["label_encoded"]

# Generate continuous vulnerability risk scores (soft labels)
log_reg = LogisticRegression(max_iter=1000, solver="lbfgs", n_jobs=1)
log_reg.fit(X, y_class)
y = log_reg.predict_proba(X)[:, 1]

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y_class
)

# Scaling
rf_scaler = StandardScaler()
X_train_scaled = rf_scaler.fit_transform(X_train)
X_test_scaled = rf_scaler.transform(X_test)

# Random Forest model implementation
rf_reg = RandomForestRegressor(
    n_estimators=500,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    bootstrap=False,
    random_state=42,
    n_jobs=-1
)
rf_reg.fit(X_train_scaled, y_train)

# Save Model and Scaler for FastAPI Inference
models_dir = os.path.join(current_dir)
joblib.dump(rf_scaler, os.path.join(models_dir, "rf_scaler.joblib"))
joblib.dump(rf_reg, os.path.join(models_dir, "rf_model.joblib"))
print(f"Saved rf_scaler.joblib & rf_model.joblib in: {models_dir}")

# Copy vectorizer.pkl -> vectorizer.joblib
src_vec = os.path.join(current_dir, "vectorizer.pkl")
dst_vec = os.path.join(current_dir, "vectorizer.joblib")

if os.path.exists(dst_vec):
    print("vectorizer.joblib already exists. Skipping copy.")
elif os.path.exists(src_vec):
    shutil.copy(src_vec, dst_vec)
    print("Copied vectorizer.pkl → vectorizer.joblib in same folder.")
else:
    print("vectorizer.pkl not found. Make sure dataprocess.py was run before training.")
