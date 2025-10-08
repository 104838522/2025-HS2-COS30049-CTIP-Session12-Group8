# Fast DBSCAN run with visuals (subsample + PCA for speed), modify config for dataset params

# Current config was fastest I found (maybe playing with PCA more will help)

# Metrics: Silhouette (non-noise, subsample), Number of noise points (subsample)
# Visuals: PCA scatter on the run subset
# x = PC1, y = PC2


# 1. Imports
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

# 2. Config 
DATA_PATH = "processed_dataset_final.csv" # dataset path
EPS = 0.7 # DBSCAN epsilon
MIN_SAMPLES = 20 # DBSCAN min_samples
SUBSAMPLE_N = 30000 # run DBSCAN on a subset (None = full)
PCA_COMPONENTS = 30 # speed-up neighborhood search
SIL_SAMPLE = 10000 # silhouette sample from clustered points, modifying above 20,000 exponentially increases calculation time
PLOT_SAMPLE = 4000 # plotting sample from the run subset
RANDOM_SEED = 42
TOP_CLUSTER_PRINT = 20

# 3. Load and select features (drop first 3 columns: id, vulnerability_type, label_encoded, they will bias clusters)
df = pd.read_csv(DATA_PATH, low_memory=False)
X = df.iloc[:, 3:].to_numpy(dtype=np.float32)

# 4. Standardize
Z = StandardScaler().fit_transform(X).astype(np.float32)

# 5. Dimensionality reduction (randomized PCA for speed)
pca_r = PCA(n_components=PCA_COMPONENTS, svd_solver="randomized", random_state=RANDOM_SEED)
Zp = pca_r.fit_transform(Z).astype(np.float32)

# 6. Subsample for DBSCAN to keep runtime low
rng = np.random.default_rng(RANDOM_SEED)
if SUBSAMPLE_N is not None and SUBSAMPLE_N < Zp.shape[0]:
    idx_run = rng.choice(Zp.shape[0], SUBSAMPLE_N, replace=False)
else:
    idx_run = np.arange(Zp.shape[0])
Z_run = Zp[idx_run]

# 7. Run DBSCAN on (sub)sampled data
db = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES, n_jobs=-1)
labels = db.fit_predict(Z_run)

# 8. Noise analysis: map to safe/vulnerable
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

# 9. Non-noise mapping: majority label + purity, plus overall breakdown
nn_mask = labels != -1
nn_total = int(nn_mask.sum())
if nn_total > 0:
    safe_nn = int(((y_sub == 0) & nn_mask).sum())
    vuln_nn = int(((y_sub == 1) & nn_mask).sum())
    print(f"Non-noise breakdown (subsample, {nn_total} total):")
    print(f"  Safe        = {safe_nn} ({safe_nn/nn_total:.1%})")
    print(f"  Vulnerable  = {vuln_nn} ({vuln_nn/nn_total:.1%})")

    # 10. Per-cluster majority mapping + purity (top-N by size)
    clusters = [c for c in np.unique(labels) if c != -1]
    sizes = {c: int((labels == c).sum()) for c in clusters}
    clusters_sorted = sorted(clusters, key=lambda c: sizes[c], reverse=True)[:TOP_CLUSTER_PRINT]
    print(f"Top {len(clusters_sorted)} clusters by size (cluster_id | size | majority | purity):")
    for c in clusters_sorted:
        m = labels == c
        n = sizes[c]
        safe_c = int(((y_sub == 0) & m).sum())
        vuln_c = n - safe_c
        majority = 0 if safe_c >= vuln_c else 1
        purity = max(safe_c, vuln_c) / n if n > 0 else 0.0
        print(f"  {c:>4} | {n:>6} | {majority} | {purity:.2f}")
else:
    print("No non-noise clusters formed.")

# 11. Metrics (silhouette on clustered points only, sampled)
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

# 12. Evaluate overall clustering using silhouette score
silhouette_avg = silhouette_score(Z_run, labels)
print(f'Silhouette Score: {silhouette_avg:.2f}')

# 13. Identifying noise points (labeled as -1)
n_noise = np.sum(labels == -1)
print(f'Number of noise points: {n_noise}')

# 14. Visuals (PCA 2D for display; project run subset to 2D)
pca_2d = PCA(n_components=2, svd_solver="randomized", random_state=RANDOM_SEED)
P2 = pca_2d.fit_transform(Z_run)

# 14.1 Optional extra down-sample just for plotting large runs
if PLOT_SAMPLE is not None and PLOT_SAMPLE < P2.shape[0]:
    plot_idx = rng.choice(P2.shape[0], PLOT_SAMPLE, replace=False)
    P2p = P2[plot_idx]; lp = labels[plot_idx]
else:
    P2p = P2; lp = labels
plt.figure(figsize=(6.5, 5.0))

# 15.Color noise as a light gray; clusters get colormap
is_noise = (lp == -1)
if np.any(~is_noise):
    plt.scatter(P2p[~is_noise, 0], P2p[~is_noise, 1], c=lp[~is_noise], s=6, cmap="plasma", label="clusters")
if np.any(is_noise):
    plt.scatter(P2p[is_noise, 0], P2p[is_noise, 1], s=6, c="#bbbbbb", label="noise")
plt.title(f"DBSCAN (eps={EPS}, min_samples={MIN_SAMPLES})")
plt.xlabel("PC1"); plt.ylabel("PC2")
plt.tight_layout(); plt.show()

