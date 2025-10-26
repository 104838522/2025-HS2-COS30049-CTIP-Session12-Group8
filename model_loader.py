# backend/model_loader.py
import joblib
import os

# -------------------------------------------------
# 1) 모델 폴더 경로 지정 (backend 안의 models)
# -------------------------------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

def load_models():
    """
    모델, 스케일러, 벡터라이저를 로드해서 반환한다.
    """
    vectorizer_path = os.path.join(MODEL_DIR, "vectorizer.joblib")
    scaler_path = os.path.join(MODEL_DIR, "scaler.joblib")
    model_path = os.path.join(MODEL_DIR, "knn_model.joblib")

    vectorizer = joblib.load(vectorizer_path) if os.path.exists(vectorizer_path) else None
    scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None
    knn_model = joblib.load(model_path) if os.path.exists(model_path) else None

    if not all([vectorizer, scaler, knn_model]):
        print("⚠️ Warning: Some model files are missing!")
    else:
        print("✅ All models loaded successfully.")

    return vectorizer, scaler, knn_model


# -------------------------------------------------
# 2) 앱 실행 시 자동 로드
# -------------------------------------------------
VECTORIZER, SCALER, KNN = load_models()
