# ------ Load trained AI components
import os
import joblib
import pandas as pd
import numpy as np
import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# Load trained model components
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "../../ml_models")

    VECTORIZER = joblib.load(os.path.join(MODEL_DIR, "vectorizer.joblib"))
    KNN_SCALER = joblib.load(os.path.join(MODEL_DIR, "knn_scaler.joblib"))
    KNN = joblib.load(os.path.join(MODEL_DIR, "knn_model.joblib"))
    RF_SCALER = joblib.load(os.path.join(MODEL_DIR, "rf_scaler.joblib"))
    RF = joblib.load(os.path.join(MODEL_DIR, "rf_model.joblib"))

    print("Model components loaded successfully.")

except Exception as e:
    print(f"Error loading model components: {e}")
    VECTORIZER = KNN_SCALER = RF_SCALER = KNN = RF = None
