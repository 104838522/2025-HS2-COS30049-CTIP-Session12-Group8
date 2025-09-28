# compare_neural_network.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from imblearn.over_sampling import RandomOverSampler

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
# 3-1) Oversampling
# -------------------------------------------------
ros = RandomOverSampler(sampling_strategy=0.67, random_state=42)
X_train_resampled, y_train_resampled = ros.fit_resample(X_train, y_train)

print("Original Train distribution:")
print(y_train.value_counts())
print("\nTrain distribution after oversampling:")
print(y_train_resampled.value_counts())
print("\nTest distribution:")
print(y_test.value_counts())

# -------------------------------------------------
# 4) Scaling (very important for NN!)
# -------------------------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)

# -------------------------------------------------
# 5) Neural Network model
# -------------------------------------------------
mlp = MLPClassifier(
    hidden_layer_sizes=(128, 64),  # two hidden layers
    activation='relu',
    solver='adam',
    max_iter=20,                   # increase if loss not converging
    random_state=42,
    verbose=True
)
mlp.fit(X_train_scaled, y_train_resampled)
y_pred_mlp = mlp.predict(X_test_scaled)

print("\n=== Neural Network (MLP) Evaluation ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_mlp):.2f}")
print(f"Precision: {precision_score(y_test, y_pred_mlp):.2f}")
print(f"Recall: {recall_score(y_test, y_pred_mlp):.2f}")
print(f"F1-Score: {f1_score(y_test, y_pred_mlp):.2f}")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_mlp))
print("\nClassification Report:")
print(classification_report(y_test, y_pred_mlp))

# -------------------------------------------------
# 6) Summarize results for comparison table
# -------------------------------------------------
def summarize_results(model_name, y_true, y_pred):
    return {
        "Model": model_name,
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred),
        "Recall": recall_score(y_true, y_pred),
        "F1-Score": f1_score(y_true, y_pred)
    }

rf_results = summarize_results("Neural Networks", y_test, y_pred_mlp)

results_df = pd.DataFrame([rf_results])

print("\n=== Model Performance Summary ===")
print(results_df.round(3))
