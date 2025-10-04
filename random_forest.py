import pandas as pd
import numpy as np
import time
import tracemalloc
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV

# -------------------------------------------------
# 1) Load dataset
# -------------------------------------------------
DATA_PATH = "../processed_dataset_final/processed_dataset_final.csv"
df = pd.read_csv(DATA_PATH, low_memory=False)

# -------------------------------------------------
# 2) Features & Target
# -------------------------------------------------
# X = df.drop(columns=["id", "vulnerability_type", "label_encoded"])
# y_class = df["label_encoded"]

# --- IGNORE ---
# Use only a subset for quick testing
X = df.drop(columns=["id", "vulnerability_type", "label_encoded"])
y_class = df["label_encoded"]

# Generate continuous vulnerability risk scores (soft labels)
print("[INFO] Generating continuous vulnerability scores")
log_reg = LogisticRegression(max_iter=1000, solver="lbfgs", n_jobs=-1)
log_reg.fit(X, y_class)
y = log_reg.predict_proba(X)[:, 1]

# -------------------------------------------------
# 3) Train/Test split
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y_class
)
print(f"[INFO] Training samples: {len(X_train)}, Testing samples: {len(X_test)}")
# -------------------------------------------------
# 4) Scaling
# -------------------------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -------------------------------------------------
# 5) Random Forest model (best technical setup)
# -------------------------------------------------
# Hyperparameter tuning (commented out after finding best params)
# param_grid = {
#     'n_estimators': [100, 300, 500],
#     'max_depth': [10, 20, None],
#     'min_samples_split': [2, 5, 10],
#     'min_samples_leaf': [1, 2, 4],
#     'max_features': ['sqrt', 'log2'],
#     'bootstrap': [True, False]
# }
# scoring = {
#     'rmse': 'neg_root_mean_squared_error',
#     'mae': 'neg_mean_absolute_error',
#     'r2': 'r2'
# }
# grid_search = GridSearchCV(
#     RandomForestRegressor(random_state=42, n_jobs=-1),
#     param_grid,
#     cv=3,
#     scoring=scoring,
#     refit='rmse',
#     verbose=2
# )
# grid_search.fit(X_train_scaled, y_train)
# print("Best parameters:", grid_search.best_params_)
# results_df = pd.DataFrame(grid_search.cv_results_)
# results_df.to_csv("random_forest_grid_search_results.csv", index=False)

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

# default parameters
# n_estimators=200, 
# random_state=42, 
# n_jobs=-1

# --- Training with time and memory tracking ---
tracemalloc.start()
start_train = time.time()
rf_reg.fit(X_train_scaled, y_train)
train_time = time.time() - start_train
current, peak_train_mem = tracemalloc.get_traced_memory()

# # --- Prediction with time and memory tracking ---
start_infer = time.time()
y_pred_rf = rf_reg.predict(X_test_scaled)
infer_time = time.time() - start_infer
current, peak_infer_mem = tracemalloc.get_traced_memory()
tracemalloc.stop()
peak_mem_mb = max(peak_train_mem, peak_infer_mem) / 1024**2

# # -------------------------------------------------
# # 6) Evaluation
# # -------------------------------------------------
rmse = np.sqrt(mean_squared_error(y_test, y_pred_rf))
mae = mean_absolute_error(y_test, y_pred_rf)
r2 = r2_score(y_test, y_pred_rf)

print("\n=== Random Forest Regression Evaluation ===")
print(f"RMSE: {rmse:.3f}")
print(f"MAE: {mae:.3f}")
print(f"R²: {r2:.3f}")
print(f"Peak Memory Usage: {peak_mem_mb:.2f} MB")
print(f"Training Time: {train_time:.2f} s")
print(f"Inference Time: {infer_time:.4f} s")
print("============================================\n")