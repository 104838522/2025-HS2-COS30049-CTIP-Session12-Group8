import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, sys

pd.set_option("display.max_columns", 120)
pd.set_option("display.width", 160)

# put your own data path here
DATA_PATH = "/Users/gianniedwards-hernandez/Desktop/uni/2025_s2/Technology_Innovation_project/A2 repo/processed_dataset_final/processed_dataset_final.csv"  # change if needed


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

# print("\n5 lines\n")
# print(df.head(5).to_string(index=False))  # 5 lines

print("\nsample row\n")
print(df.iloc[0].to_dict())  # sample row

# ----- -----

# printing count of unique CWEs to console
unique_cwes = df["vulnerability_cwe_id"].unique()
print("\nnumber of CWEs:")
print(unique_cwes.size)

# bar chart for safe vs. vulnerable
safe_or_vuln = df["label_encoded"].value_counts().sort_index()
safe_or_vuln = safe_or_vuln.rename(index={0: "safe", 1: "vulnerable"})
plt.figure(figsize=(10, 8))
safe_or_vuln.plot(kind="bar")
plt.title("label_encoded Distribution")
plt.xlabel("encoded_label")
plt.ylabel("Count")
total = safe_or_vuln.sum()  # raw counts & percentages
ax = safe_or_vuln.plot(kind="bar", color=["steelblue", "salmon"])
for p in ax.patches:
    count = int(p.get_height())
    percent = 100 * count / total
    ax.annotate(
        f"{count:,}\n({percent:.1f}%)",  # e.g. "12,345\n(67.8%)"
        (p.get_x() + p.get_width() / 2.0, p.get_height()),
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )
plt.tight_layout()
plt.show()


# bar chart for records in C vs. C++
lang_count = df["lang_C"].value_counts().sort_index()
lang_count = lang_count.rename(index={0: "C++", 1: "C"})
plt.figure(figsize=(10, 8))
lang_count.plot(kind="bar")
plt.title("Language Distribution")
plt.xlabel("Language")
plt.ylabel("Count")
total = lang_count.sum()
ax = lang_count.plot(kind="bar", color=["steelblue", "salmon"])
for p in ax.patches:
    count = int(p.get_height())
    percent = 100 * count / total
    ax.annotate(
        f"{count:,}\n({percent:.1f}%)",
        (p.get_x() + p.get_width() / 2.0, p.get_height()),
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )
plt.tight_layout()
plt.show()
