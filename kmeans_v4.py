# --------------------------------------------
# K-Means + Safe/Vulnerable distribution by PC1 slice
# --------------------------------------------
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# 1) Config
DATA_PATH   = "processed_dataset_final.csv"
K_RANGE     = range(2, 9)
SIL_SAMPLE  = 10000
PLOT_SAMPLE = 8000
RANDOM_SEED = 42
BATCH_SIZE  = 65536
MAX_ITER    = 100

# 2) Load dataset
df = pd.read_csv(DATA_PATH, low_memory=False)

# Features & labels (drop first 3 columns: id, vulnerability_type, label_encoded) to ensure DBSCAN doesn't cluster based on deterministic columns
X = df.iloc[:, 3:].to_numpy(dtype=np.float32)
y = df["label_encoded"].to_numpy(dtype=np.int32)   ### NEW

# 3) Standardize
Z = StandardScaler().fit_transform(X).astype(np.float32)

# 4) Sample for silhouette/plotting
rng = np.random.default_rng(RANDOM_SEED)
if SIL_SAMPLE and SIL_SAMPLE < Z.shape[0]:
    idx_sil = rng.choice(Z.shape[0], SIL_SAMPLE, replace=False)
    Z_sil = Z[idx_sil]
else:
    idx_sil = np.arange(Z.shape[0]); Z_sil = Z

if PLOT_SAMPLE and PLOT_SAMPLE < Z.shape[0]:
    idx_plot = rng.choice(Z.shape[0], PLOT_SAMPLE, replace=False)
    Z_plot, y_plot = Z[idx_plot], y[idx_plot]   ### NEW
else:
    idx_plot = np.arange(Z.shape[0]); Z_plot, y_plot = Z, y

# 5) Sweep K values
best_k, best_sil, best_model = None, -1.0, None
for k in K_RANGE:
    km = MiniBatchKMeans(
        n_clusters=k, random_state=RANDOM_SEED,
        batch_size=BATCH_SIZE, max_iter=MAX_ITER, n_init=10
    )
    km.fit(Z)
    if len(np.unique(km.labels_)) > 1:
        sil = silhouette_score(Z_sil, km.predict(Z_sil))
        if sil > best_sil:
            best_k, best_sil, best_model = k, sil, km

# 6) Results
if best_model is None:
    print("No valid clustering found.")
else:
    print(f"Best k: {best_k} | Silhouette: {best_sil:.3f}")

    # PCA for plotting
    pca = PCA(n_components=2, svd_solver="randomized", random_state=RANDOM_SEED)
    P = pca.fit_transform(Z_plot)
    labs_plot = best_model.predict(Z_plot)

    # Scatter with labels
    plt.figure(figsize=(6.5, 5))
    desired_pc1_inspect = 1
    scatter = plt.scatter(P[:,0], P[:,1], c=labs_plot, s=6, cmap="tab10")
    plt.axvline(x=desired_pc1_inspect, color="red", linestyle="--", label="PC1 = 10")   ### NEW
    plt.title(f"K-Means (best k={best_k})")
    plt.xlabel("PC1"); plt.ylabel("PC2")
    plt.legend(); plt.tight_layout(); plt.show()

    # --- Distribution around PC1 ≈ 10 ---
    margin = 0.5   # adjust as needed
    mask = (P[:,0] >= desired_pc1_inspect-margin) & (P[:,0] <= desired_pc1_inspect+margin)
    subset_labels = y_plot[mask]
    if subset_labels.size > 0:
        safe = np.sum(subset_labels == 0)
        vuln = np.sum(subset_labels == 1)
        total = safe + vuln
        print(f"Distribution near PC1={desired_pc1_inspect} ±{margin}:")
        print(f"  Safe        = {safe} ({safe/total:.1%})")
        print(f"  Vulnerable  = {vuln} ({vuln/total:.1%})")
    else:
        print(f"No samples found near PC1={desired_pc1_inspect}.")
