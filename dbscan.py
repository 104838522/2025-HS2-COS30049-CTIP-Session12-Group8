# Low-spec DBSCAN on your dataset (drop-in)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

# --------------------------
# 0) Config (tune these)
# --------------------------
DATA_PATH = Path(
    "/Users/gianniedwards-hernandez/Desktop/uni/2025_s2/Technology_Innovation_project/processed_dataset_final.csv"
)
SAMPLE_FOR_SEARCH = 50_000  # rows for small grid (reduce if needed)
BIG_SAMPLE = 400_000  # rows to cluster after picking params (reduce if needed)
PCA_FOR_CLUSTER = 10  # dims to keep for clustering (10–30 is typical)
EPS_GRID = [0.5, 1.0, 1.5]  # small, fast grid
MIN_SAMPLES_GRID = [5, 10]
SIL_SAMP_SIZE = 10_000  # silhouette sample; lower if you hit memory
PLOT_N = 2_000  # points to show in scatter


# --------------------------
# 1) Load
# --------------------------
def load_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, low_memory=True)
    # try JSONL then JSON
    try:
        return pd.read_json(path, lines=True)
    except Exception:
        return pd.read_json(path)


df = load_any(DATA_PATH)

# --------------------------
# 2) Numeric feature picking + pruning (ID-like, sparse, constant)
# --------------------------
num = df.select_dtypes(include=[np.number]).copy()

drop_cols = []
n = len(num)
for c in num.columns:
    s = num[c]
    if s.isna().mean() > 0.70:  # too sparse
        drop_cols.append(c)
        continue
    if s.nunique(dropna=True) <= 1:  # constant
        drop_cols.append(c)
        continue
    if s.nunique(dropna=True) / max(1, n) > 0.90:  # ID-like
        drop_cols.append(c)

X = num.drop(columns=drop_cols, errors="ignore").dropna(axis=0).astype("float32")

if X.shape[0] < 10 or X.shape[1] == 0:
    raise ValueError(
        f"Not enough usable numeric data after filtering. Shape: {X.shape}"
    )

print(f"[INFO] Rows after cleaning: {X.shape[0]}, features: {X.shape[1]}")
if drop_cols:
    print(
        f"[INFO] Dropped columns (partial): {drop_cols[:15]}{' ...' if len(drop_cols) > 15 else ''}"
    )

# --------------------------
# 3) Subsample for param search
# --------------------------
if len(X) > SAMPLE_FOR_SEARCH:
    X_search = X.sample(n=SAMPLE_FOR_SEARCH, random_state=42)
else:
    X_search = X

# --------------------------
# 4) Scale + PCA (cluster in reduced space to speed up DBSCAN)
# --------------------------
scaler = StandardScaler()
X_search_sc = scaler.fit_transform(X_search)

pca = PCA(
    n_components=min(PCA_FOR_CLUSTER, X_search_sc.shape[1]),
    random_state=42,
    svd_solver="randomized",
)
X_search_red = pca.fit_transform(X_search_sc).astype("float32")

# --------------------------
# 5) Tiny grid search for eps/min_samples (robust + cheap)
# --------------------------
best = {"score": -1.0, "eps": None, "min_samples": None}

for eps in EPS_GRID:
    for ms in MIN_SAMPLES_GRID:
        labels = DBSCAN(eps=eps, min_samples=ms, n_jobs=1).fit_predict(X_search_red)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        if n_clusters >= 2 and np.any(labels != -1):
            # silhouette on a sample to avoid O(N^2) blow-up
            samp = min(SIL_SAMP_SIZE, len(X_search_red))
            try:
                score = silhouette_score(
                    X_search_red, labels, sample_size=samp, random_state=42
                )
            except Exception:
                score = -1.0
            if score > best["score"]:
                best = {
                    "score": float(score),
                    "eps": float(eps),
                    "min_samples": int(ms),
                }

# Fallback if no good clustering emerged
if best["eps"] is None:
    best = {"score": None, "eps": 1.0, "min_samples": 10}
print(
    f"[INFO] Chosen params -> eps: {best['eps']}, min_samples: {best['min_samples']}, silhouette: {best['score']}"
)

# --------------------------
# 6) Refit DBSCAN on a bigger sample (still PCA-reduced)
# --------------------------
if len(X) > BIG_SAMPLE:
    X_big = X.sample(n=BIG_SAMPLE, random_state=123)
else:
    X_big = X

X_big_sc = scaler.transform(X_big)
X_big_red = pca.transform(X_big_sc).astype("float32")

db = DBSCAN(eps=best["eps"], min_samples=best["min_samples"], n_jobs=1)
labels_big = db.fit_predict(X_big_red)
n_clusters_big = len(set(labels_big)) - (1 if -1 in labels_big else 0)
noise_pct = (labels_big == -1).mean() * 100.0
print(f"[INFO] Clusters on big run: {n_clusters_big}, noise %: {noise_pct:.2f}")

# Optional: silhouette on big sample (keep it sampled!)
try:
    if n_clusters_big >= 2 and np.any(labels_big != -1):
        samp = min(SIL_SAMP_SIZE, len(X_big_red))
        sil_big = silhouette_score(
            X_big_red, labels_big, sample_size=samp, random_state=42
        )
        print(f"[INFO] Silhouette (big sample): {sil_big:.4f}")
except Exception:
    pass

# --------------------------
# 7) Plot with a small sample
# --------------------------
plot_n = min(PLOT_N, len(labels_big))
idx = np.random.default_rng(42).choice(len(labels_big), size=plot_n, replace=False)

# 2D just for visualization (separate from PCA_FOR_CLUSTER)
pca2 = PCA(n_components=2, random_state=42, svd_solver="randomized")
X2d = pca2.fit_transform(X_big_red)

plt.figure(figsize=(7, 6))
plt.scatter(X2d[idx, 0], X2d[idx, 1], c=labels_big[idx], s=8)
plt.title("DBSCAN clusters (PCA projection; sampled)")
plt.xlabel("PCA 1")
plt.ylabel("PCA 2")
plt.tight_layout()
plt.show()
