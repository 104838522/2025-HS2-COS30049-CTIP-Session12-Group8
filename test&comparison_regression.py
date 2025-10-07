# regression_comparison_with_preliminary_tests.py

import pandas as pd
import numpy as np
import time, tracemalloc
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1) Load dataset
# -------------------------------------------------
DATA_PATH = "../processed_dataset_final/processed_dataset_final.csv"
df = pd.read_csv(DATA_PATH, low_memory=False)

print("[INFO] Dataset loaded successfully.")
print("Shape:", df.shape)

# -------------------------------------------------
# 2) Feature & Target setup
# -------------------------------------------------
X = df.drop(columns=["id", "vulnerability_type", "label_encoded"])
y_class = df["label_encoded"]

# Generate continuous vulnerability risk scores (soft labels)
print("[INFO] Generating continuous vulnerability scores...")
log_reg = LogisticRegression(max_iter=1000, solver="lbfgs", n_jobs=-1)
log_reg.fit(X, y_class)
y = log_reg.predict_proba(X)[:, 1]

# -------------------------------------------------
# 3) Split data
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y_class
)
print(f"[INFO] Training samples: {len(X_train)}, Testing samples: {len(X_test)}")

# -------------------------------------------------
# 4) Preliminary Tests
# -------------------------------------------------

## (a) Target Distribution
print("\n[TEST] Checking target (risk score) distribution...")
plt.hist(y, bins=30, color='skyblue', edgecolor='black')
plt.title("Distribution of Vulnerability Risk Scores")
plt.xlabel("Risk Score")
plt.ylabel("Frequency")
plt.show()
print(f"Mean risk score: {np.mean(y):.3f}, Std Dev: {np.std(y):.3f}")

## (b) Baseline Model Test
print("\n[TEST] Running baseline Dummy Regressor...")
dummy = DummyRegressor(strategy="mean")
dummy.fit(X_train, y_train)
y_pred_dummy = dummy.predict(X_test)
rmse_dummy = np.sqrt(mean_squared_error(y_test, y_pred_dummy))
mae_dummy = mean_absolute_error(y_test, y_pred_dummy)
r2_dummy = r2_score(y_test, y_pred_dummy)
print(f"Baseline RMSE: {rmse_dummy:.4f} | MAE: {mae_dummy:.4f} | R²: {r2_dummy:.4f}")

## (c) Overfitting Check (small subset)
print("\n[TEST] Overfitting check on small subset (5000 samples)...")
rf_temp = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_temp.fit(X_train[:5000], y_train[:5000])
train_r2 = rf_temp.score(X_train[:5000], y_train[:5000])
test_r2 = rf_temp.score(X_test[:5000], y_test[:5000])
print(f"Train R² (subset): {train_r2:.3f} | Test R² (subset): {test_r2:.3f}")

# -------------------------------------------------
# 5) Helper function for training and evaluation
# -------------------------------------------------
def train_and_evaluate(model, X_train, y_train, X_test, y_test, model_name="Model"):
    tracemalloc.start()
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mem = peak / 1024**2  # MB

    start = time.time()
    y_pred = model.predict(X_test)
    infer_time = time.time() - start

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\n=== {model_name} ===")
    print(f"Train Time: {train_time:.2f}s | Inference Time: {infer_time:.4f}s | Peak Mem: {peak_mem:.2f} MB")
    print(f"RMSE: {rmse:.4f} | MAE: {mae:.4f} | R²: {r2:.4f}")

    return {
        "Model": model_name,
        "RMSE": rmse,
        "MAE": mae,
        "R²": r2,
        "Train Time (s)": train_time,
        "Inference Time (s)": infer_time,
        "Mem (MB)": peak_mem
    }

# -------------------------------------------------
# 6) Train and Compare Models
# -------------------------------------------------
rf_reg = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
gb_reg = GradientBoostingRegressor(n_estimators=200, random_state=42)

results = []
results.append(train_and_evaluate(rf_reg, X_train, y_train, X_test, y_test, "Random Forest Regressor"))
results.append(train_and_evaluate(gb_reg, X_train, y_train, X_test, y_test, "Gradient Boosting Regressor"))

# -------------------------------------------------
# 7) Summary
# -------------------------------------------------
results_df = pd.DataFrame(results)
print("\n=== Regression Model Comparison Summary ===")
print(results_df.round(3))