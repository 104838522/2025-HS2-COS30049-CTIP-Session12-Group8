# clustering_comparison.py

import pandas as pd
import time, psutil, os
from sklearn.cluster import OPTICS, DBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler
import datetime

# -------------------------------------------------
# 1) Load dataset
# -------------------------------------------------
DATA_PATH = "../processed_dataset_final/processed_dataset_final.csv"
df = pd.read_csv(DATA_PATH, low_memory=False)

# -------------------------------------------------
# 2) Features (drop id, label columns)
# -------------------------------------------------
# Use only a subset for faster clustering (e.g., 5000 samples)
SUBSET_SIZE = 5000
df_subset = df.sample(n=SUBSET_SIZE, random_state=42) if len(df) > SUBSET_SIZE else df
X = df_subset.drop(columns=["id", "vulnerability_type", "label_encoded"])

# -------------------------------------------------
# 3) Standardize features
# -------------------------------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -------------------------------------------------
# 4) Helper function for clustering, timing & logging
# -------------------------------------------------
def cluster_and_evaluate(model, X, model_name="Clustering Model"):
    process = psutil.Process(os.getpid())

    # Memory before clustering
    start_mem = process.memory_info().rss / 1024**2

    print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting {model_name} clustering...")

    # Clustering
    start = time.time()
    labels = model.fit_predict(X)
    cluster_time = time.time() - start

    # Memory after clustering
    end_mem = process.memory_info().rss / 1024**2

    # Remove noise points for metrics if any (-1 label)
    mask = labels != -1
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

    if n_clusters > 1 and mask.sum() > 1:
        silhouette = silhouette_score(X[mask], labels[mask])
        calinski = calinski_harabasz_score(X[mask], labels[mask])
        davies = davies_bouldin_score(X[mask], labels[mask])
    else:
        silhouette = calinski = davies = float('nan')

    print(f"\n=== {model_name} ===")
    print(f"Clustering time: {cluster_time:.2f}s | Mem usage: {(end_mem - start_mem):.2f} MB")
    print(f"Clusters found: {n_clusters}")
    print(f"Silhouette Score: {silhouette:.3f}")
    print(f"Calinski-Harabasz Score: {calinski:.3f}")
    print(f"Davies-Bouldin Score: {davies:.3f}")

    return {
        "Model": model_name,
        "Clusters": n_clusters,
        "Silhouette": silhouette,
        "Calinski-Harabasz": calinski,
        "Davies-Bouldin": davies,
        "Clustering Time (s)": cluster_time,
        "Mem Usage (MB)": end_mem - start_mem
    }

# -------------------------------------------------
# 5) Initialize Models
# -------------------------------------------------
optics_clf = OPTICS(min_samples=5, n_jobs=-1)
dbscan_clf = DBSCAN(eps=0.5, min_samples=5, n_jobs=-1)

# -------------------------------------------------
# 6) Run Experiments
# -------------------------------------------------
results = []
results.append(cluster_and_evaluate(optics_clf, X_scaled, "OPTICS"))
results.append(cluster_and_evaluate(dbscan_clf, X_scaled, "DBSCAN"))

# -------------------------------------------------
# 7) Summary Table
# -------------------------------------------------
results_df = pd.DataFrame(results)
print("\n=== Clustering Model Comparison Summary ===")
print(results_df.round(3))