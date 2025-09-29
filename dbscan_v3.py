# --------------------------------------------
# Fast DBSCAN with visuals (subsample + PCA for speed)
# Metrics: Silhouette (non-noise, subsample), Number of noise points (subsample)
# Visuals: PCA(2D) scatter on the run subset
# --------------------------------------------

# 1) Imports
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

# 2) Config (edit here)
DATA_PATH      = "processed_dataset_final.csv"  # dataset path
EPS            = 0.6                         # DBSCAN epsilon
MIN_SAMPLES    = 20                             # DBSCAN min_samples
SUBSAMPLE_N    = 120000                          # run DBSCAN on a subset (None = full)
PCA_COMPONENTS = 40                             # speed-up neighborhood search
SIL_SAMPLE     = 10000                          # silhouette sample from clustered points
PLOT_SAMPLE    = 8000                           # plotting sample from the run subset
RANDOM_SEED    = 42

# 3) Load + select features (drop first 3 columns: id, vulnerability_type, label_encoded)
df = pd.read_csv(DATA_PATH, low_memory=False)
X = df.iloc[:, 3:].to_numpy(dtype=np.float32)

# 4) Standardize
Z = StandardScaler().fit_transform(X).astype(np.float32)

# 5) Dimensionality reduction (randomized PCA for speed)
pca_r = PCA(n_components=PCA_COMPONENTS, svd_solver="randomized", random_state=RANDOM_SEED)
Zp = pca_r.fit_transform(Z).astype(np.float32)

# 6) Subsample for DBSCAN to keep runtime low
rng = np.random.default_rng(RANDOM_SEED)
if SUBSAMPLE_N is not None and SUBSAMPLE_N < Zp.shape[0]:
    idx_run = rng.choice(Zp.shape[0], SUBSAMPLE_N, replace=False)
else:
    idx_run = np.arange(Zp.shape[0])
Z_run = Zp[idx_run]

# 7) Run DBSCAN on (sub)sampled data
db = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES, n_jobs=-1)
labels = db.fit_predict(Z_run)

# --- Noise analysis: map to safe/vulnerable ---
y_sub = df["label_encoded"].to_numpy()[idx_run]  # ground truth labels for subsample
noise_mask = labels == -1
n_noise = int(noise_mask.sum())

if n_noise > 0:
    safe_noise = int(((y_sub == 0) & noise_mask).sum())
    vuln_noise = int(((y_sub == 1) & noise_mask).sum())
    print(f"Noise breakdown (subsample, {n_noise} total):")
    print(f"  Safe        = {safe_noise} ({safe_noise/n_noise:.1%})")
    print(f"  Vulnerable  = {vuln_noise} ({vuln_noise/n_noise:.1%})")
else:
    print("No noise points detected.")

# 8) Metrics (silhouette on clustered points only, sampled)
mask = labels != -1
sil_out = "N/A"
if np.any(mask) and len(np.unique(labels[mask])) > 1:
    if SIL_SAMPLE is not None and SIL_SAMPLE < mask.sum():
        nz_idx = np.where(mask)[0]
        take = rng.choice(nz_idx, SIL_SAMPLE, replace=False)
        sil = silhouette_score(Z_run[take], labels[take])
    else:
        sil = silhouette_score(Z_run[mask], labels[mask])
    sil_out = f"{sil:.3f}"
n_noise = int(np.sum(labels == -1))

print(f"Silhouette Score (non-noise, subsample): {sil_out}")
print(f"Number of noise points (on subsample): {n_noise}")

# 9) Visuals (PCA 2D for display; project run subset to 2D)
pca_2d = PCA(n_components=2, svd_solver="randomized", random_state=RANDOM_SEED)
P2 = pca_2d.fit_transform(Z_run)

# Optional extra down-sample just for plotting large runs
if PLOT_SAMPLE is not None and PLOT_SAMPLE < P2.shape[0]:
    plot_idx = rng.choice(P2.shape[0], PLOT_SAMPLE, replace=False)
    P2p = P2[plot_idx]; lp = labels[plot_idx]
else:
    P2p = P2; lp = labels

plt.figure(figsize=(6.5, 5.0))
# Color noise as a light gray; clusters get colormap
is_noise = (lp == -1)
if np.any(~is_noise):
    plt.scatter(P2p[~is_noise, 0], P2p[~is_noise, 1], c=lp[~is_noise], s=6, cmap="plasma", label="clusters")
if np.any(is_noise):
    plt.scatter(P2p[is_noise, 0], P2p[is_noise, 1], s=6, c="#bbbbbb", label="noise")
plt.title(f"DBSCAN (eps={EPS}, min_samples={MIN_SAMPLES})")
plt.xlabel("PC1"); plt.ylabel("PC2")
plt.tight_layout(); plt.show()

