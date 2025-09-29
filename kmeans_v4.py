# --------------------------------------------
# Fast K-Means with automatic K sweep + visuals
# Metrics: Best-K Silhouette (sampled), Inertia
# Visuals: PCA(2D) scatter on a sample
# --------------------------------------------

# 1) Imports
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# 2) Config (edit here)
DATA_PATH   = "processed_dataset_final.csv"  # dataset path
K_RANGE     = range(2, 9)                    # K values to try
SIL_SAMPLE  = 10000                          # sample size for silhouette (None = full)
PLOT_SAMPLE = 8000                           # sample size for plotting (None = full, slower)
RANDOM_SEED = 42
BATCH_SIZE  = 16384                          # MiniBatchKMeans batch size
MAX_ITER    = 100

# 3) Load + select features (drop first 3 columns: id, vulnerability_type, label_encoded)
df = pd.read_csv(DATA_PATH, low_memory=False)
X = df.iloc[:, 3:].to_numpy(dtype=np.float32)

# 4) Standardize (float32 for speed/memory)
Z = StandardScaler().fit_transform(X).astype(np.float32)

# 5) Prepare samples for silhouette & plotting
rng = np.random.default_rng(RANDOM_SEED)
idx_sil = None
if SIL_SAMPLE is not None and SIL_SAMPLE < Z.shape[0]:
    idx_sil = rng.choice(Z.shape[0], SIL_SAMPLE, replace=False)
    Z_sil = Z[idx_sil]
else:
    Z_sil = Z

if PLOT_SAMPLE is not None and PLOT_SAMPLE < Z.shape[0]:
    idx_plot = rng.choice(Z.shape[0], PLOT_SAMPLE, replace=False)
    Z_plot = Z[idx_plot]
else:
    idx_plot = np.arange(Z.shape[0])
    Z_plot = Z

# 6) Sweep K values and pick best by silhouette (computed on sample)
best_k, best_sil, best_inertia, best_model = None, -1.0, None, None
for k in K_RANGE:
    km = MiniBatchKMeans(
        n_clusters=k, random_state=RANDOM_SEED, batch_size=BATCH_SIZE,
        max_iter=MAX_ITER, n_init=10
    )
    km.fit(Z)
    if len(np.unique(km.labels_)) > 1:
        sil = silhouette_score(Z_sil, km.predict(Z_sil))
        if np.isfinite(sil) and sil > best_sil:
            best_k, best_sil, best_inertia, best_model = k, sil, km.inertia_, km

# 7) Metrics
if best_model is None:
    print("No valid clustering found across K_RANGE (silhouette undefined).")
else:
    print(f"Best k: {best_k}")
    print(f"Silhouette Score (sampled): {best_sil:.3f}")
    print(f"Inertia (sum of squared distances): {best_inertia:.2f}")

    # 8) Visuals (PCA 2D on plot sample)
    pca = PCA(n_components=2, svd_solver="randomized", random_state=RANDOM_SEED)
    P = pca.fit_transform(Z_plot)
    labs_plot = best_model.predict(Z_plot)
    plt.figure(figsize=(6.5, 5.0))
    plt.scatter(P[:, 0], P[:, 1], c=labs_plot, s=6, cmap="tab10")
    plt.title(f"K-Means (best k={best_k})")
    plt.xlabel("PC1"); plt.ylabel("PC2")
    plt.tight_layout(); plt.show()
