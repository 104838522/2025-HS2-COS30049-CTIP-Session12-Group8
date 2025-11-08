# ------------------------------------------------------------
# Endpoint - Visualization Data (Static)
# ------------------------------------------------------------
from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

# ---------- Helper: Compute Vulnerability Type Frequency ----------
def compute_vulntype_frequency(df):
    """Process top 15 common vulnerability type in the dataset."""
    vuln_type_col = df["vulnerability_type"].value_counts().head(15)
    return [{"vuln_type": vuln, "count": int(count)} for vuln, count in vuln_type_col.items()]


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
        "vuln_type_frequency": compute_vulntype_frequency(df),
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
