# ------------------------------------------------------------
# Step 8. Load trained AI components
import joblib
import pandas as pd
import numpy as np
import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

try:
    VECTORIZER = joblib.load("./models/vectorizer.joblib")

    KNN_SCALER = joblib.load("./models/knn_scaler.joblib")
    KNN = joblib.load("./models/knn_model.joblib")

    RF_SCALER = joblib.load("./models/rf_scaler.joblib")
    RF = joblib.load("./models/rf_model.joblib")

    print("Model components loaded successfully.")
except Exception as e:
    print(f"Error loading model components: {e}")
    VECTORIZER = KNN_SCALER = RF_SCALER = KNN = RF = None
