import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import Normalizer

# --------------------------
# 0) Config
# --------------------------
DATA_PATH = Path(r"Z:\processed_dataset_final.csv")

SAMPLE_FOR_SEARCH = 5_000                                   # rows for small grid (reduce if needed)
BIG_SAMPLE = 100_000                                        # rows to cluster after picking params (reduce if needed)
PCA_FOR_CLUSTER = 30                                        # dims to keep for clustering
EPS_GRID = [0.5, 1.0, 1.5, 2.0, 2.5]                    
MIN_SAMPLES_GRID = [5, 10, 20, 40]
SIL_SAMP_SIZE = 1_000                                       # silhouette sample; lower if you hit memory
PLOT_N = 2_000                                              # points to show in scatter


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

# ---------- 4A) Euclidean representation: Standardize + PCA ----------
scaler = StandardScaler()
X_search_sc = scaler.fit_transform(X_search)
pca = PCA(n_components=min(PCA_FOR_CLUSTER, X_search_sc.shape[1]),
          random_state=42, svd_solver="randomized")
X_search_euc = pca.fit_transform(X_search_sc).astype("float32")

# We'll transform the big sample later with the same scaler+pca:
# X_big_sc = scaler.transform(X_big); X_big_euc = pca.transform(X_big_sc)

# ---------- 4B) Cosine representation: L2-normalize (no PCA needed) ----------
# Cosine distance works best on L2-normalized rows; scaling is not required.
norm = Normalizer(copy=False)
X_search_cos = norm.fit_transform(X_search.astype("float32"))
# For big sample later: X_big_cos = norm.transform(X_big.astype("float32"))


# --------------------------
# 5) Generic sweep, then run for EUC and COS
# --------------------------
# --------------------------
# 5) Grid search sweeps (Euclidean + Cosine) with auto-pick
# --------------------------
def sweep_dbscan(X_rep, metric, eps_grid, min_samples_grid, sil_samp_size):
    results = []
    best = {"score": -1.0, "eps": None, "min_samples": None}
    for eps in eps_grid:
        for ms in min_samples_grid:
            db = DBSCAN(eps=eps, min_samples=ms, metric=metric, n_jobs=1)
            labels = db.fit_predict(X_rep)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            noise_pct = (labels == -1).mean() * 100
            silhouette = -1.0
            if n_clusters >= 2 and np.any(labels != -1):
                try:
                    silhouette = silhouette_score(
                        X_rep, labels,
                        metric=metric,
                        sample_size=min(sil_samp_size, len(X_rep)),
                        random_state=42
                    )
                except Exception:
                    pass
            row = {
                "eps": eps, "min_samples": ms,
                "clusters": n_clusters,
                "noise%": round(noise_pct, 1),
                "silhouette": round(silhouette, 3)
            }
            results.append(row)
            if silhouette > best["score"]:
                best = {"score": silhouette, "eps": eps, "min_samples": ms}
    return results, best

# Define grids
EPS_GRID_EUC = [0.5, 1.0, 1.5, 2.0, 2.5]   # Euclidean
EPS_GRID_COS = [0.1, 0.2, 0.3, 0.5, 0.7]   # Cosine
MIN_SAMPLES_GRID = [5, 10, 20, 40]

# Run Euclidean sweep
print("\n=== EUCLIDEAN sweep (std+PCA) ===")
res_euc, best_euc = sweep_dbscan(X_search_euc, "euclidean",
                                 EPS_GRID_EUC, MIN_SAMPLES_GRID, SIL_SAMP_SIZE)
for r in res_euc:
    print(f"eps={r['eps']:>3}, min_samples={r['min_samples']:>2} "
          f"→ clusters={r['clusters']:>3}, noise={r['noise%']:>5}%, "
          f"silhouette={r['silhouette']:>6}")
print(f"[EUC] best: eps={best_euc['eps']}, min_samples={best_euc['min_samples']}, silhouette={best_euc['score']:.3f}")

# Run Cosine sweep
print("\n=== COSINE sweep (L2-normalized) ===")
res_cos, best_cos = sweep_dbscan(X_search_cos, "cosine",
                                 EPS_GRID_COS, MIN_SAMPLES_GRID, SIL_SAMP_SIZE)
for r in res_cos:
    print(f"eps={r['eps']:>3}, min_samples={r['min_samples']:>2} "
          f"→ clusters={r['clusters']:>3}, noise={r['noise%']:>5}%, "
          f"silhouette={r['silhouette']:>6}")
print(f"[COS] best: eps={best_cos['eps']}, min_samples={best_cos['min_samples']}, silhouette={best_cos['score']:.3f}")


# --------------------------
# 6) Big run using the better metric (with cosine safeguards)
# --------------------------
from time import time
from sklearn.decomposition import TruncatedSVD

# separate caps: cosine must be MUCH smaller
BIG_SAMPLE_EUC = BIG_SAMPLE          # e.g., 100_000 as you set
BIG_SAMPLE_COS = 25_000              # tune for your laptop (try 20_000–40_000)

score_euc = best_euc["score"] if best_euc["score"] is not None else float("-inf")
score_cos = best_cos["score"] if best_cos["score"] is not None else float("-inf")
use_cosine = score_cos > score_euc

# choose subset size
if use_cosine:
    cap = min(BIG_SAMPLE_COS, len(X))
else:
    cap = min(BIG_SAMPLE_EUC, len(X))

# sample the same rows for features & labels
X_big = X.sample(n=cap, random_state=123) if len(X) > cap else X.copy()

t0 = time()
if use_cosine:
    # ---- Cosine path: (optional) SVD -> L2 normalize -> DBSCAN(cosine) ----
    # SVD helps if original X had many columns; harmless if it doesn't.
    SVD_COMPS = min(100, X_big.shape[1])   # 50–200 typical; keep modest on low-spec
    svd = TruncatedSVD(n_components=SVD_COMPS, random_state=42)
    X_big_svd = svd.fit_transform(X_big.astype("float32"))
    X_big_rep = norm.transform(X_big_svd.astype("float32"))  # L2 normalize rows

    db = DBSCAN(eps=best_cos["eps"], min_samples=best_cos["min_samples"],
                metric="cosine", n_jobs=1)
    metric_for_sil = "cosine"
    print(f"[INFO] Using COSINE: eps={best_cos['eps']}, min_samples={best_cos['min_samples']}, "
          f"sweep_sil={score_cos:.3f}, rows={len(X_big_rep)}")
else:
    # ---- Euclidean path: Standardize + PCA (same scaler/pca as search) ----
    X_big_sc  = scaler.transform(X_big)
    X_big_rep = pca.transform(X_big_sc).astype("float32")

    db = DBSCAN(eps=best_euc["eps"], min_samples=best_euc["min_samples"],
                metric="euclidean", n_jobs=1)
    metric_for_sil = "euclidean"
    print(f"[INFO] Using EUCLIDEAN: eps={best_euc['eps']}, min_samples={best_euc['min_samples']}, "
          f"sweep_sil={score_euc:.3f}, rows={len(X_big_rep)}")

labels_big = db.fit_predict(X_big_rep)
n_clusters_big = len(set(labels_big)) - (1 if -1 in labels_big else 0)
noise_pct = (labels_big == -1).mean() * 100.0
print(f"[INFO] Clusters on big run: {n_clusters_big}, noise %: {noise_pct:.2f}, "
      f"elapsed: {time()-t0:.1f}s")

# Silhouette on big sample (sampled) with the correct metric
try:
    if n_clusters_big >= 2 and np.any(labels_big != -1):
        samp = min(SIL_SAMP_SIZE, len(X_big_rep))
        sil_big = silhouette_score(X_big_rep, labels_big, metric=metric_for_sil,
                                   sample_size=samp, random_state=42)
        print(f"[INFO] Silhouette (big sample, {metric_for_sil}): {sil_big:.4f}")
except Exception:
    pass

# keep legacy name for downstream mapping/plot
X_big_red = X_big_rep



# --------------------------
# 6.1) Map clusters to vulnerability labels
# --------------------------
# Align the subset used for clustering with the original dataframe
df_big = df.loc[X_big.index]  # keep only the same rows as in X_big

if "label_encoded" in df_big.columns:   # adjust if your label column has a different name
    cluster_df = pd.DataFrame({
        "cluster": labels_big,
        "label": df_big["label_encoded"].values
    })

    # Noise points = cluster -1
    print("Noise points:", (cluster_df["cluster"] == -1).sum())

    # Cross-tab counts
    ct_counts = pd.crosstab(cluster_df["cluster"], cluster_df["label"])

    # Proportions per cluster
    ct_props = ct_counts.div(ct_counts.sum(axis=1), axis=0)

    print("\nCounts per cluster:")
    print(ct_counts)

    print("\nProportion vulnerable per cluster:")
    print(ct_props.round(3))

    # Optional: sort clusters by vulnerability ratio
    if 1 in ct_props.columns:
        sorted_clusters = ct_props[1].sort_values(ascending=False)
        print("\nClusters ranked by vulnerability ratio:")
        print(sorted_clusters)
else:
    print("[WARN] No 'label_encoded' column found in dataframe. Cannot map clusters to labels.")



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

# Prepare big representations
if len(X) > BIG_SAMPLE:
    X_big = X.sample(n=BIG_SAMPLE, random_state=123)
else:
    X_big = X

# Euclidean big
X_big_sc  = scaler.transform(X_big)
X_big_euc = pca.transform(X_big_sc).astype("float32")
db_euc = DBSCAN(eps=best_euc["eps"], min_samples=best_euc["min_samples"], metric="euclidean", n_jobs=1)
labels_euc = db_euc.fit_predict(X_big_euc)
ncl_euc = len(set(labels_euc)) - (1 if -1 in labels_euc else 0)
noise_euc = (labels_euc == -1).mean() * 100
sil_euc = silhouette_score(X_big_euc, labels_euc, metric="euclidean",
                           sample_size=min(SIL_SAMP_SIZE, len(X_big_euc)), random_state=42) if ncl_euc>=2 and np.any(labels_euc!=-1) else float("nan")
print(f"\n[EUC big] clusters={ncl_euc}, noise={noise_euc:.2f}%, silhouette={sil_euc:.3f}")

# Cosine big
X_big_cos = norm.transform(X_big.astype("float32"))
db_cos = DBSCAN(eps=best_cos["eps"], min_samples=best_cos["min_samples"], metric="cosine", n_jobs=1)
labels_cos = db_cos.fit_predict(X_big_cos)
ncl_cos = len(set(labels_cos)) - (1 if -1 in labels_cos else 0)
noise_cos = (labels_cos == -1).mean() * 100
sil_cos = silhouette_score(X_big_cos, labels_cos, metric="cosine",
                           sample_size=min(SIL_SAMP_SIZE, len(X_big_cos)), random_state=42) if ncl_cos>=2 and np.any(labels_cos!=-1) else float("nan")
print(f"[COS big] clusters={ncl_cos}, noise={noise_cos:.2f}%, silhouette={sil_cos:.3f}")

def map_clusters_to_labels(labels, X_subset, df_all, label_col="label_encoded", header=""):
    df_sub = df_all.loc[X_subset.index]
    if label_col not in df_sub.columns:
        print(f"[WARN] No '{label_col}' column found. Skip mapping for {header}."); return
    cluster_df = pd.DataFrame({"cluster": labels, "label": df_sub[label_col].values})
    print(f"\n[{header}] Noise points:", (cluster_df["cluster"] == -1).sum())
    ct_counts = pd.crosstab(cluster_df["cluster"], cluster_df["label"])
    ct_props  = ct_counts.div(ct_counts.sum(axis=1), axis=0)
    print(f"\n[{header}] Counts per cluster:\n", ct_counts)
    print(f"\n[{header}] Proportion vulnerable per cluster:\n", ct_props.round(3))

# Call it:
map_clusters_to_labels(labels_euc, X_big, df, label_col="label_encoded", header="EUC")
map_clusters_to_labels(labels_cos, X_big, df, label_col="label_encoded", header="COS")

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


# Visualize EUC 
# For COS: just to plot, do a 2D PCA over X_big_cos (doesn't change clustering)
pca2 = PCA(n_components=2, random_state=42, svd_solver="randomized")
X2d_cos = pca2.fit_transform(X_big_cos)
idx = np.random.default_rng(42).choice(len(labels_cos), size=min(PLOT_N, len(labels_cos)), replace=False)
plt.figure(figsize=(7,6))
plt.scatter(X2d_cos[idx,0], X2d_cos[idx,1], c=labels_cos[idx], s=8)
plt.title("DBSCAN (cosine, 2D PCA for viz; sampled)")
plt.xlabel("PCA 1"); plt.ylabel("PCA 2"); plt.tight_layout(); plt.show()
