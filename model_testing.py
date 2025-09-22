import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# -------------------------------------------------
# 1) Load data
# -------------------------------------------------
pd.set_option("display.max_columns", 120)
pd.set_option("display.width", 160)

DATA_PATH = "/Users/gianniedwards-hernandez/Desktop/uni/2025_s2/Technology_Innovation_project/processed_dataset_final.csv"
df = pd.read_csv(DATA_PATH, low_memory=False)

# -------------------------------------------------
# 2) Choose features (numeric only) + light cleaning
#    - drop ultra-sparse cols (>70% NaN)
#    - drop near-constant cols (<=1 unique)
#    - drop ID-like cols (unique ratio > 0.9)
# -------------------------------------------------
num_df = df.select_dtypes(include=[np.number]).copy()

drop_cols = []
for col in num_df.columns:
    s = num_df[col]
    if s.isna().mean() > 0.7:
        drop_cols.append(col)
        continue
    if s.nunique(dropna=True) <= 1:
        drop_cols.append(col)
        continue
    if (s.nunique(dropna=True) / max(1, len(s))) > 0.9:
        drop_cols.append(col)

X = num_df.drop(columns=drop_cols, errors="ignore").dropna(axis=0)
if X.shape[0] < 10 or X.shape[1] == 0:
    raise ValueError(f"Not enough clean numeric data after filtering. Shape: {X.shape}")


# -------------------------------------------------
# 3) Scale (DBSCAN needs comparable feature scales)
# -------------------------------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X.values)

# -------------------------------------------------
# 4) Small grid search for eps/min_samples using silhouette
#    (valid only when >=2 clusters and not all noise)
# -------------------------------------------------
eps_grid = np.linspace(0.3, 3.0, 10)  # widen/narrow as needed
min_samples_grid = [3, 5, 10, 20]

best = {"score": -1.0, "eps": None, "min_samples": None, "labels": None}

for eps in eps_grid:
    for ms in min_samples_grid:
        db = DBSCAN(eps=eps, min_samples=ms, n_jobs=-1)
        labels = db.fit_predict(X_scaled)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        if n_clusters >= 2 and np.any(labels != -1):
            try:
                score = silhouette_score(X_scaled, labels)
            except Exception:
                score = -1.0
            if score > best["score"]:
                best = {"score": score, "eps": eps, "min_samples": ms, "labels": labels}

# Fallback if everything collapsed to noise / single cluster
if best["eps"] is None:
    best["eps"] = 1.0
    best["min_samples"] = 10 if X.shape[0] > 100 else 5

# -------------------------------------------------
# 5) Final fit with the chosen params + quick report
# -------------------------------------------------
db_best = DBSCAN(eps=best["eps"], min_samples=best["min_samples"], n_jobs=-1)
labels = db_best.fit_predict(X_scaled)

n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
noise_pct = (labels == -1).mean() * 100

print("\nDBSCAN quick report")
print("-" * 60)
print(f"Rows used:           {X.shape[0]}")
print(f"Features used:       {X.shape[1]}")
print(f"eps:                 {best['eps']}")
print(f"min_samples:         {best['min_samples']}")
print(f"clusters found:      {n_clusters}")
print(f"noise percentage:    {noise_pct:.2f}%")
if best["score"] is not None:
    print(f"silhouette (approx): {best['score']:.4f}")
print(
    f"Dropped columns (partial): {drop_cols[:15]}{' ...' if len(drop_cols)>15 else ''}"
)

# -------------------------------------------------
# 6) 2D plot via PCA (for visualization only)
#    Clustering is done in full scaled space above.
# -------------------------------------------------
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)

plt.figure(figsize=(7, 6))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, s=12)
plt.title("DBSCAN clusters (PCA projection)")
plt.xlabel("PCA 1")
plt.ylabel("PCA 2")
plt.tight_layout()
plt.show()
