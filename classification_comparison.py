# classification_comparison.py

import pandas as pd
import time, psutil, os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

# -------------------------------------------------
# 1) Load dataset
# -------------------------------------------------
DATA_PATH = "../processed_dataset_final/processed_dataset_final.csv"
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
# 4) Helper function for training, timing & logging
# -------------------------------------------------
def train_and_evaluate(model, X_train, y_train, X_test, y_test, model_name="Model"):
    process = psutil.Process(os.getpid())

    # Memory before training
    start_mem = process.memory_info().rss / 1024**2

    # Training
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start

    # Memory after training
    end_mem = process.memory_info().rss / 1024**2

    # Inference
    start = time.time()
    y_pred = model.predict(X_test)
    infer_time = time.time() - start

    # Evaluation
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"\n=== {model_name} ===")
    print(f"Training time: {train_time:.2f}s | Inference time: {infer_time:.4f}s | Mem usage: {(end_mem - start_mem):.2f} MB")
    print(f"Accuracy: {acc:.3f} | Precision: {prec:.3f} | Recall: {rec:.3f} | F1: {f1:.3f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    return {
        "Model": model_name,
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1-Score": f1,
        "Train Time (s)": train_time,
        "Inference Time (s)": infer_time,
        "Mem Usage (MB)": end_mem - start_mem
    }

# -------------------------------------------------
# 5) Initialize Models
# -------------------------------------------------
rf_clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
gb_clf = GradientBoostingClassifier(n_estimators=200, random_state=42)
lr_clf = LogisticRegression(max_iter=1000, n_jobs=-1, solver="lbfgs")

# -------------------------------------------------
# 6) Run Experiments
# -------------------------------------------------
results = []
results.append(train_and_evaluate(rf_clf, X_train, y_train, X_test, y_test, "Random Forest"))
results.append(train_and_evaluate(gb_clf, X_train, y_train, X_test, y_test, "Gradient Boosting"))
results.append(train_and_evaluate(lr_clf, X_train, y_train, X_test, y_test, "Logistic Regression"))

# -------------------------------------------------
# 7) Summary Table
# -------------------------------------------------
results_df = pd.DataFrame(results)
print("\n=== Model Comparison Summary ===")
print(results_df.round(3))
