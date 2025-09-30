# regression_comparison.py

import pandas as pd
import time, psutil, os
import tracemalloc
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

# -------------------------------------------------
# 1) Load dataset
# -------------------------------------------------
DATA_PATH = "../processed_dataset_final/processed_dataset_final.csv"
df = pd.read_csv(DATA_PATH, low_memory=False)

# -------------------------------------------------
# 2) Features & Target
# -------------------------------------------------
X = df.drop(columns=["id", "vulnerability_type", "label_encoded"])
y_class = df["label_encoded"]

# Generate continuous regression target
# Use probability of vulnerability from Logistic Regression as "risk score"
print("[INFO] Generating continuous labels (probability of vulnerability)...")
log_reg = LogisticRegression(max_iter=1000, solver="lbfgs", n_jobs=-1)
log_reg.fit(X, y_class)
y = log_reg.predict_proba(X)[:, 1]  # continuous score between 0 and 1

# -------------------------------------------------
# 3) Train/Test split
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y_class
)

# -------------------------------------------------
# 4) Helper function for training, timing & logging
# -------------------------------------------------
def train_and_evaluate(model, X_train, y_train, X_test, y_test, model_name="Model"):
    # Start tracing memory allocations
    tracemalloc.start()

    # Training
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start

    # Inference
    start = time.time()
    y_pred = model.predict(X_test)
    infer_time = time.time() - start

    # Get peak memory usage in MB
    current, peak = tracemalloc.get_traced_memory()
    peak_mem_mb = peak / 1024**2
    tracemalloc.stop()

    # Metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\n=== {model_name} ===")
    print(f"Training time: {train_time:.2f}s | Inference time: {infer_time:.4f}s | Mem usage: {(peak_mem_mb):.2f} MB")
    print(f"RMSE: {rmse:.3f} | MAE: {mae:.3f} | R²: {r2:.3f}")

    return {
        "Model": model_name,
        "RMSE": rmse,
        "MAE": mae,
        "R²": r2,
        "Train Time (s)": train_time,
        "Inference Time (s)": infer_time,
        "Mem Usage (MB)": peak_mem_mb
    }

# -------------------------------------------------
# 5) Initialize Models
# -------------------------------------------------
rf_reg = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
gb_reg = GradientBoostingRegressor(n_estimators=200, random_state=42)

# -------------------------------------------------
# 6) Run Experiments
# -------------------------------------------------
results = []
results.append(train_and_evaluate(rf_reg, X_train, y_train, X_test, y_test, "Random Forest"))
results.append(train_and_evaluate(gb_reg, X_train, y_train, X_test, y_test, "Gradient Boosting"))

# -------------------------------------------------
# 7) Summary Table
# -------------------------------------------------
results_df = pd.DataFrame(results)
print("\n=== Regression Model Comparison Summary ===")
print(results_df.round(3))
