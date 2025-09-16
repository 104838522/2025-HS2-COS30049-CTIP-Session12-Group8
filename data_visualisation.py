import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, sys

pd.set_option("display.max_columns", 120)
pd.set_option("display.width", 160)

DATA_PATH = "/Users/gianniedwards-hernandez/Desktop/uni/2025_s2/Technology_Innovation_project/A2 repo/processed_dataset_final/processed_dataset_final.csv"  # change if needed


def load_df(path):
    # Try CSV first (your sample is definitely CSV)
    try:
        # wide TF-IDF files benefit from low_memory=False
        return pd.read_csv(path, low_memory=False)
    except Exception as e_csv:
        # Fallback to JSONL in case the extension misleads us
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
print(list(df.columns[:20]))  # list the columns

print("\n5 lines\n")
print(df.head(5).to_string(index=False))  # 5 lines

print("\nsample row\n")
print(df.iloc[0].to_dict())  # sample row

# ----- -----

# simple bar chart for safe vs. vulnerable
safe_or_vuln = df["label_encoded"].value_counts().sort_index()
safe_or_vuln = safe_or_vuln.rename(index={0: "safe", 1: "vulnerable"})
plt.figure(figsize=(10, 6))
safe_or_vuln.plot(kind="bar")
plt.title("label_encoded Distribution")
plt.xlabel("encoded_label")
plt.ylabel("Count")
plt.tight_layout()
plt.show()
