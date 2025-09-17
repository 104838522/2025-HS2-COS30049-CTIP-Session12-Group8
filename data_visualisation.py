import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, sys
import seaborn as sns

pd.set_option("display.max_columns", 120)
pd.set_option("display.width", 160)

# put your own data path here
DATA_PATH = "/Users/gianniedwards-hernandez/Desktop/uni/2025_s2/Technology_Innovation_project/A2 repo/processed_dataset_final/processed_dataset_final.csv"  # change if needed


# helper function to annotate charts with raw count and percentages
def annotate_counts_and_pct(ax, totals=None, fmt="{:,}\n({:.1f}%)", fontsize=11):
    bars = ax.patches
    heights = np.array([b.get_height() for b in bars])
    if totals is None:
        base = heights.sum()
        percs = (heights / base) * 100 if base else np.zeros_like(heights)
    elif np.isscalar(totals):
        base = totals
        percs = (heights / base) * 100 if base else np.zeros_like(heights)
    else:
        totals = np.asarray(totals)
        # repeat each total for grouped bars if needed
        if len(totals) != len(bars):
            # try to broadcast row totals for grouped bars
            # infer group size from unique x positions
            xs = [b.get_x() for b in bars]
            uniq_x = sorted(set(xs))
            group_size = int(len(bars) / len(uniq_x))
            totals = np.repeat(totals, group_size)
        percs = (heights / totals) * 100
    for b, pct in zip(bars, percs):
        ax.annotate(
            fmt.format(int(round(b.get_height())), pct),
            (b.get_x() + b.get_width() / 2, b.get_height()),
            ha="center",
            va="bottom",
            fontsize=fontsize,
            fontweight="bold",
        )


# dataset checking
def load_df(path):
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception as e_csv:
        try:
            return pd.read_json(path, lines=True)
        except Exception as e_json:
            print("Failed to read as CSV and JSONL.")
            print("CSV error:", e_csv)
            print("JSONL error:", e_json)
            sys.exit(1)


df = pd.read_csv(DATA_PATH)

# -----REMOVE THIS CODE LATER-----

print("\nshape\n")
print(df.shape)  # dataset shape

print("\nfirst 20 columns\n")
print(list(df.columns[:100]))  # list the columns

print("\nsample row\n")
print(df.iloc[0].to_dict())  # sample row

# ----- -----

# printing count of unique CWEs to console
unique_cwes = df["vulnerability_cwe_id"].unique()
print("\nnumber of CWEs:")
print(unique_cwes.size)


# confirming dataset quality


def missing_unknown_plot(df):
    # count missing values (NaN) per column
    missing_counts = df.isna().sum()
    # count unknown string vals
    unknown_counts = (
        df.astype(str).apply(lambda col: col.str.lower().eq("unknown").sum())
        if not df.empty
        else pd.Series(0, index=df.columns)
    )

    # combine into one Series
    total_issues = missing_counts + unknown_counts
    total_issues = total_issues[total_issues > 0].sort_values(ascending=False)
    if total_issues.empty:
        print("No missing or 'Unknown' values found. Dataset looks clean!")
        return
    plt.figure(figsize=(12, 6))
    total_issues.plot(kind="bar", color="firebrick")
    plt.title("Missing/Unknown Values per Column")
    plt.xlabel("Column")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


# safe vs. vulnerable records


def safe_vs_vul():
    safe_or_vuln = df["label_encoded"].value_counts().sort_index()
    safe_or_vuln = safe_or_vuln.rename(index={0: "safe", 1: "vulnerable"})
    fig, ax = plt.subplots(figsize=(10, 8))
    safe_or_vuln.plot(kind="bar", ax=ax, color=["steelblue", "salmon"])
    ax.set_title("label_encoded Distribution")
    ax.set_xlabel("encoded_label")
    ax.set_ylabel("Count")
    annotate_counts_and_pct(ax, totals=safe_or_vuln.sum())
    plt.tight_layout()
    plt.show()


# records in C vs. C++


def c_vs_cplus():
    lang_count = df["lang_C"].value_counts().sort_index()
    lang_count = lang_count.rename(index={0: "C++", 1: "C"})
    fig, ax = plt.subplots(figsize=(10, 8))
    lang_count.plot(kind="bar", ax=ax, color=["steelblue", "salmon"])
    ax.set_title("Language Distribution")
    ax.set_xlabel("Language")
    ax.set_ylabel("Count")
    annotate_counts_and_pct(ax, totals=lang_count.sum())
    plt.tight_layout()
    plt.show()


# bar chart for the 15 most common CWEs


def top_cwes(top_n=15):
    vc = df["vulnerability_cwe_id"].value_counts(dropna=False)
    plot = pd.concat([vc.head(top_n), pd.Series({"Other": vc.iloc[top_n:].sum()})])
    pct = (plot / len(df) * 100).sort_values()

    plt.figure(figsize=(9, 0.45 * len(pct) + 1.2))
    ax = pct.plot.barh()
    for p, v in zip(ax.patches, pct.values):
        ax.text(v, p.get_y() + p.get_height() / 2, f" {v:.1f}%", va="center")
    ax.set_xlabel("% of dataset")
    ax.set_ylabel("")
    ax.set_title(f"Top {top_n} CWE types (+ Other)")
    plt.tight_layout()
    plt.show()


# safe vs. vulnerable per language


def safe_vul_per_lang():
    lang_map = {1: "C", 0: "C++"}
    tmp = df.assign(Language=df["lang_C"].map(lang_map))
    lang_vuln = tmp.groupby(["Language", "label_encoded"]).size().unstack(fill_value=0)
    lang_vuln.columns = ["safe", "vulnerable"]  # 0=safe 1=vulnerable

    fig, ax = plt.subplots(figsize=(10, 8))
    lang_vuln.plot(kind="bar", ax=ax)
    ax.set_title("safe vs vulnerable per language")
    ax.set_xlabel("Language")
    ax.set_ylabel("Count")
    ax.legend(title="label")
    row_totals = lang_vuln.sum(axis=1).values
    group_size = lang_vuln.shape[1]
    row_totals_rep = np.repeat(row_totals, group_size)
    annotate_counts_and_pct(ax, totals=row_totals_rep)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()


# compare average tf-idf scores in safe and vulnerable records


def av_tfidf_weight():
    keyword_cols = [
        col
        for col in df.columns
        if col
        not in ["id", "vulnerability_cwe_id", "label_encoded", "lang_C", "lang_C++"]
    ]
    means = df.groupby("label_encoded")[keyword_cols].mean().T
    means.columns = ["Safe", "Vulnerable"]

    diff = (means["Vulnerable"] - means["Safe"]).sort_values(ascending=False).head(15)

    plt.figure(figsize=(12, 6))
    diff.plot(kind="bar", color="crimson")
    plt.title("Top 15 Keywords More Frequent in Vulnerable Code")
    plt.xlabel("Keyword")
    plt.ylabel("Mean TF-IDF Difference (Vulnerable - Safe)")
    plt.tight_layout()
    plt.show()


# heatmap, keyword frequencies and safe or vuln


def feature_heatmap(top_k=15):
    use_cols = [
        c
        for c in df.select_dtypes(include=[np.number]).columns
        if df[c].var() > 0 and c != "id"
    ]
    if "label_encoded" not in df.columns:
        print("Missing 'label_encoded' column")
        return

    use_cols = ["label_encoded"] + [c for c in use_cols if c != "label_encoded"]
    corr = df[use_cols].corr(numeric_only=True)
    target_corr = corr.loc[use_cols[1:], "label_encoded"]  # in series
    top_features = target_corr.abs().nlargest(min(top_k, len(target_corr))).index
    top_features = top_features.sort_values()
    cols = ["label_encoded"] + list(top_features)
    corr_subset = df[cols].corr(numeric_only=True)
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr_subset,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        cbar=True,
        xticklabels=corr_subset.columns,
        yticklabels=corr_subset.columns,
    )
    plt.title("Correlation Heatmap (Top TF-IDF Features vs Vulnerability)")
    plt.tight_layout()
    plt.show()


# top k tokens vs safe or vuln (better readability)


def label_only_corr_heatmap(df, top_k=15, label_col="label_encoded"):
    excl = {"id", label_col, "vulnerability_cwe_id", "lang_C", "lang_C++"}
    num_cols = df.select_dtypes(include=[np.number]).columns
    feat_cols = [c for c in num_cols if c not in excl and df[c].var() > 0]
    if label_col not in df.columns or not feat_cols:
        print("Missing label or no usable numeric features.")
        return
    r = df[feat_cols].corrwith(df[label_col]).dropna()
    top_feats = r.abs().nlargest(min(top_k, len(r))).index.tolist()
    vals = r[top_feats].values[np.newaxis, :]  # shape (1, K)
    vmax = np.max(np.abs(vals))
    vmin = -vmax
    plt.figure(figsize=(1.0 + 0.55 * len(top_feats), 3.2))
    im = plt.imshow(vals, aspect="auto", vmin=vmin, vmax=vmax, cmap="coolwarm")
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.xticks(range(len(top_feats)), top_feats, rotation=45, ha="right", fontsize=10)
    plt.yticks([0], [label_col], fontsize=11)
    for j, v in enumerate(vals[0]):
        plt.text(
            j, 0, f"{v:+.2f}", ha="center", va="center", fontsize=10, fontweight="bold"
        )
    plt.title(f"Correlation with {label_col} (Top {len(top_feats)})", fontsize=13)
    plt.tight_layout()
    plt.show()


# tf-idf feature correlation, safe vs. vul bar charts


def label_corr_bars(df, top_k=10, label_col="label_encoded"):
    excl = {"id", label_col, "vulnerability_cwe_id", "lang_C", "lang_C++"}
    num_cols = df.select_dtypes(include=[np.number]).columns
    feat_cols = [c for c in num_cols if c not in excl and df[c].var() > 0]
    if label_col not in df.columns or not feat_cols:
        print("Missing label or no usable numeric features.")
        return
    r = df[feat_cols].corrwith(df[label_col]).dropna()
    # top positive / negative
    pos = r[r > 0].sort_values(ascending=False).head(top_k)
    neg = r[r < 0].sort_values(ascending=True).head(top_k)  # most negative

    # POSITIVE
    if not pos.empty:
        fig, ax = plt.subplots(figsize=(1.0 + 0.6 * len(pos), 4.0))
        ax.bar(pos.index, pos.values)
        ax.set_title(f"Top {len(pos)} Positively Correlated Tokens vs {label_col}")
        ax.set_xlabel("Token")
        ax.set_ylabel("Pearson r")
        ax.set_ylim(0, max(pos.values) * 1.15)
        ax.tick_params(axis="x", rotation=45)
        for i, v in enumerate(pos.values):
            ax.text(
                i,
                v,
                f"{v:+.2f}",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )
        plt.tight_layout()
        plt.show()

    # NEGATIVE
    if not neg.empty:
        fig, ax = plt.subplots(figsize=(1.0 + 0.6 * len(neg), 4.0))
        ax.bar(neg.index, neg.values)
        ax.set_title(f"Top {len(neg)} Negatively Correlated Tokens vs {label_col}")
        ax.set_xlabel("Token")
        ax.set_ylabel("Pearson r")
        ax.set_ylim(min(neg.values) * 1.15, 0)
        ax.tick_params(axis="x", rotation=45)
        for i, v in enumerate(neg.values):
            ax.text(
                i, v, f"{v:+.2f}", ha="center", va="top", fontsize=10, fontweight="bold"
            )
        plt.tight_layout()
        plt.show()


# histogram for safe vs. vul tokens PER function


def function_length(df, label_col="label_encoded", top_n=2):
    # have to 'estimate' function length as the SUM of token weights PER each row
    meta = {"id", label_col, "vulnerability_cwe_id", "lang_C", "lang_C++"}
    num_cols = [
        c for c in df.select_dtypes(include=[np.number]).columns if c not in meta
    ]
    # ffs why was that so hard
    if not num_cols:
        print("No token columns found.")
        return
    df["function_length"] = df[num_cols].sum(axis=1)
    labels = {0: "Safe", 1: "Vulnerable"}
    plt.figure(figsize=(8, 6))
    for val, label in labels.items():
        subset = df[df[label_col] == val]["function_length"]
        plt.hist(subset, bins=100, alpha=0.35, label=label, density=True)
    plt.title("Function Length Distribution i.e. tokens per function")
    plt.xlabel("~Number of Tokens")
    plt.yscale("log")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    missing_unknown_plot(df)
    safe_vs_vul()
    c_vs_cplus()
    top_cwes()
    safe_vul_per_lang()
    av_tfidf_weight()
    feature_heatmap()
    label_only_corr_heatmap(df, top_k=15, label_col="label_encoded")
    label_corr_bars(df, top_k=12, label_col="label_encoded")
    function_length(df, label_col="label_encoded", top_n=2)


main()
