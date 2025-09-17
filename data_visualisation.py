import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, sys

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


def top_cwes():
    top_n = 15
    cwe_counts = df["vulnerability_cwe_id"].value_counts().head(top_n)
    fig, ax = plt.subplots(figsize=(12, 6))
    cwe_counts.plot(kind="bar", ax=ax)
    ax.set_title(f"Top {top_n} CWE Types in Dataset")
    ax.set_xlabel("CWE ID")
    ax.set_ylabel("Count")
    # annotate vs total dataset so % reflects overall share
    annotate_counts_and_pct(ax, totals=len(df))
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


def main():
    safe_vs_vul()
    c_vs_cplus()
    top_cwes()
    safe_vul_per_lang()
    av_tfidf_weight()


main()
