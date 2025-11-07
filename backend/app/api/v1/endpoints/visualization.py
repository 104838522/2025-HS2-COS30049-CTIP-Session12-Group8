# ------------------------------------------------------------
# Endpoint - Visualization Data (Static)
# ------------------------------------------------------------
from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

# ---------- Helper: Compute Token Frequency ----------
def compute_token_frequency(df):
    """Count how many SAFE (0) and VULNERABLE (1) samples contain each token (weight > 0)."""
    token_start_col = df.columns.get_loc("break")  # first token column
    token_cols = df.columns[token_start_col:]

    result = []
    for token in token_cols:
        safe_count = df[(df["label_encoded"] == 0) & (df[token] > 0)].shape[0]
        vuln_count = df[(df["label_encoded"] == 1) & (df[token] > 0)].shape[0]
        result.append(
            {"token": token, "safe": int(safe_count), "vulnerable": int(vuln_count)}
        )

    return sorted(result, key=lambda x: x["vulnerable"], reverse=True)


# ---------- Helper: Compute Language Distribution ----------
def compute_language_distribution(df):
    """Compute distribution of programming languages in the dataset."""
    lang_start_col = df.columns.get_loc("lang_C")
    lang_end_col = df.columns.get_loc("lang_Scala") + 1
    lang_cols = df.columns[lang_start_col:lang_end_col]

    result = []
    for lang in lang_cols:
        count = df[df[lang] > 0].shape[0]
        result.append({"language": lang.replace("lang_", ""), "count": int(count)})

    return result


# ---------- Helper: Prepare Visualization Payload ----------
def prepare_visualization_payload(df):
    return {
        "token_frequency": compute_token_frequency(df),
        "language_distribution": compute_language_distribution(df),
    }


# ---------- Endpoint: Get All Visualization Data ----------..
@router.get("/")
def get_all_visualization_data():
    try:
        # Path setup to load dataset
        data_dir = os.path.join(os.path.dirname(__file__), "../../../../data")
        csv_path = os.path.join(data_dir, "processed_dataset_final.csv")
        gz_path = csv_path + ".gz"

        # Try loading .csv first, then .csv.gz -
        if os.path.exists(csv_path):
            print(f"Loading dataset from {csv_path}")
            df = pd.read_csv(csv_path, low_memory=False)
        elif os.path.exists(gz_path):
            print(f"Loading compressed dataset from {gz_path}")
            df = pd.read_csv(gz_path, compression="gzip", low_memory=False)
        else:
            raise FileNotFoundError("Dataset file not found (.csv or .csv.gz)")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dataset: {str(e)}")

    if df is None or df.empty:
        raise HTTPException(status_code=501, detail="Dataset not loaded or empty.")

    return prepare_visualization_payload(df)
