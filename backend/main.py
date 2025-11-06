# main.py
from fastapi import (
    FastAPI,
    HTTPException,
    APIRouter,
    Depends,
    Request,
    BackgroundTasks,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import time
import uuid
import joblib
import pandas as pd
import numpy as np
from preprocess import preprocess_code
import warnings
from sklearn.exceptions import InconsistentVersionWarning
import traceback

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)


# ------------------------------------------------------------
# Step 1. Initialize FastAPI
app = FastAPI(title="VulnLocator AI API")

# ------------------------------------------------------------
# Step 2. Configure CORS (for React frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# Step 3. Request timing middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(
        f"Request: {request.method} {request.url} - Processing time: {process_time:.4f}s"
    )
    return response


# ------------------------------------------------------------
# Step 4. Global error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# ------------------------------------------------------------
# Step 5. In-memory temporary database (for user accounts and history)
USERS: Dict[str, Dict] = {}
TOKENS: Dict[str, str] = {}
HISTORY: Dict[str, List[Dict]] = {}


# ------------------------------------------------------------
# Step 6. Pydantic models
class SignupIn(BaseModel):
    name: str
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class Highlight(BaseModel):
    line: int
    score: float
    snippet: str


class AnalyzeOut(BaseModel):
    result: str
    confidence: Optional[float]
    processing_time_sec: float
    timestamp: str
    highlights: Optional[List[dict]] = None


class UpdateUserIn(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None


# ------------------------------------------------------------
# Step 7. Helper functions and dependencies
def get_db():
    return {"db": "Simulated database connection"}


def _generate_token() -> str:
    return str(uuid.uuid4())


def authenticate_token(token: str) -> Optional[str]:
    return TOKENS.get(token)


def _save_history(email: str, entry: dict):
    lst = HISTORY.setdefault(email, [])
    lst.append(entry)
    print(f"[history] Saved record for {email} (total {len(lst)})")


# ------------------------------------------------------------
# Step 8. Load trained AI components
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


# ------------------------------------------------------------
# Step 9. Authentication endpoints
@app.post("/api/auth/signup")
def signup(payload: SignupIn, db=Depends(get_db)):
    if payload.email in USERS:
        raise HTTPException(status_code=400, detail="Email already registered.")
    user_id = f"user-{len(USERS)+1}"
    USERS[payload.email] = {
        "id": user_id,
        "name": payload.name,
        "email": payload.email,
        "password": payload.password,
    }
    print(f"[auth] New user: {payload.email}")
    return {
        "message": "Signup successful",
        "user": {"id": user_id, "name": payload.name, "email": payload.email},
    }


@app.post("/api/auth/login")
def login(payload: LoginIn, db=Depends(get_db)):
    user = USERS.get(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = _generate_token()
    TOKENS[token] = payload.email
    print(f"[auth] {payload.email} logged in with token: {token}")
    return {
        "message": "Login successful",
        "token": token,
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
    }


# ------------------------------------------------------------
# Step 10. Analyze (AI Prediction)

# ---------- Helper: predict probability/score (works for KNN or RF) ----------
def predict_score_from_text(text: str, model_name: str = "knn"):
    """
    Return a single score for the given code text.
    - For KNN (classification) return the max probability (0..1) if available.
    - For RF (regression) return the predicted risk score (assumed 0..1).
    - If the required model/scaler/vectorizer is not available, return None.
    """
    try:
        proc = preprocess_code(text)
        X_vec = VECTORIZER.transform([proc])

        # convert to dense array
        if hasattr(X_vec, "toarray"):
            X_dense = X_vec.toarray()
        else:
            X_dense = np.asarray(X_vec)

        # choose scaler and model depending on model_name
        if model_name == "rf":
            scaler = RF_SCALER
            model = RF
        else:
            scaler = KNN_SCALER
            model = KNN

        # apply scaler if available (handle dataframe-compatible scaler)
        try:
            if scaler is not None and hasattr(scaler, "feature_names_in_"):
                cols = getattr(
                    VECTORIZER,
                    "get_feature_names_out",
                    lambda: [f"F{i}" for i in range(X_dense.shape[1])],
                )()
                df = pd.DataFrame(X_dense, columns=cols)
                Xs = scaler.transform(df)
            elif scaler is not None:
                Xs = scaler.transform(X_dense)
            else:
                Xs = X_dense
        except Exception:
            Xs = X_dense

        # predict using chosen model
        if model_name == "rf":
            if model is None:
                return None
            score = float(model.predict(Xs)[0])
            return score
        else:  # knn default
            if model is None:
                return None
            if hasattr(model, "predict_proba"):
                return float(model.predict_proba(Xs).max())
            else:
                # fallback: if KNN does not have predict_proba, return class as 0/1
                pred = int(model.predict(Xs)[0])
                return float(pred)
    except Exception as e:
        print("predict_score_from_text failed:", e)
        print(traceback.format_exc())
        return None


# ---------- Helper: naive function splitter (unchanged) ----------
def simple_function_split(lines):
    # (same implementation as your original)
    blocks = []
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i].lstrip()
        if line.startswith("def ") or line.startswith("class "):
            start = i
            j = i + 1
            while j < n and (
                lines[j].startswith(" ")
                or lines[j].startswith("\t")
                or lines[j].strip() == ""
            ):
                j += 1
            blocks.append((start, j - 1))
            i = j
        elif line.endswith("{"):
            start = i
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                if lines[j].strip().endswith("{"):
                    depth += 1
                if "}" in lines[j]:
                    depth -= lines[j].count("}")
                j += 1
            blocks.append((start, max(start, j - 1)))
            i = j
        else:
            i += 1
    if not blocks and n > 0:
        blocks = [(0, n - 1)]
    return blocks


# ---------- Main locator: function-level then line-level occlusion (model-aware) ----------
def locate_vulnerable_regions(raw_code: str, model_name: str = "knn", top_funcs: int = 3, top_lines: int = 5, base_score: float = None):
    """
    Identify lines that reduce the model score when removed.
    - model_name: "knn" or "rf"
    - base_score: if provided, reuse instead of recalculating
    Returns list of dicts: {line, score, snippet}
    """
    lines = raw_code.splitlines()
    if len(lines) == 0:
        return []

    # compute base score if not provided
    if base_score is None:
        base_score = predict_score_from_text(raw_code, model_name=model_name)

    blocks = simple_function_split(lines)
    func_scores = []

    for s, e in blocks:
        # mask the whole block
        masked = lines.copy()
        for idx in range(s, e + 1):
            masked[idx] = ""
        masked_text = "\n".join(masked)
        p = predict_score_from_text(masked_text, model_name=model_name)

        # unify scoring: always use non-negative delta if base_score is available
        if base_score is None or p is None:
            # fallback: use class-change if classification model exists
            try:
                # attempt class-based fallback for KNN-like behavior
                if model_name == "knn" and KNN is not None:
                    X_base = VECTORIZER.transform([preprocess_code(raw_code)])
                    Xb = X_base.toarray() if hasattr(X_base, "toarray") else np.asarray(X_base)
                    try:
                        Xb_scaled = KNN_SCALER.transform(Xb)
                    except Exception:
                        Xb_scaled = Xb
                    base_pred = int(KNN.predict(Xb_scaled)[0])

                    X_mask = VECTORIZER.transform([preprocess_code(masked_text)])
                    Xm = X_mask.toarray() if hasattr(X_mask, "toarray") else np.asarray(X_mask)
                    try:
                        Xm_scaled = KNN_SCALER.transform(Xm)
                    except Exception:
                        Xm_scaled = Xm
                    pred_mask = int(KNN.predict(Xm_scaled)[0])
                    score = 0.5 if base_pred != pred_mask else 0.0  # softened fallback
                else:
                    score = 0.0
            except Exception:
                score = 0.0
        else:
            # positive impact only (clamp to zero)
            try:
                score = float(max(base_score - p, 0.0))
            except Exception:
                score = 0.0

        func_scores.append((s, e, score))

    # sort blocks by score descending
    func_scores.sort(key=lambda x: x[2], reverse=True)

    highlights = []
    MIN_LINE_SCORE = 0.05

    for s, e, fscore in func_scores[:top_funcs]:
        for idx in range(s, e + 1):
            masked = lines.copy()
            masked[idx] = ""
            masked_text = "\n".join(masked)
            p = predict_score_from_text(masked_text, model_name=model_name)

            if base_score is None or p is None:
                # fallback class-change
                try:
                    X_mask = VECTORIZER.transform([preprocess_code(masked_text)])
                    Xm_d = X_mask.toarray() if hasattr(X_mask, "toarray") else np.asarray(X_mask)
                    try:
                        Xm = KNN_SCALER.transform(Xm_d)
                    except Exception:
                        Xm = Xm_d
                    # attempt to get a base_pred from original full code
                    X_full = VECTORIZER.transform([preprocess_code(raw_code)])
                    X_full_d = X_full.toarray() if hasattr(X_full, "toarray") else np.asarray(X_full)
                    try:
                        X_full_s = KNN_SCALER.transform(X_full_d)
                    except Exception:
                        X_full_s = X_full_d
                    base_pred = int(KNN.predict(X_full_s)[0])
                    pred_mask = int(KNN.predict(Xm)[0])
                    sc = 0.5 if base_pred != pred_mask else 0.0
                except Exception:
                    sc = 0.0
            else:
                sc = float(max(base_score - p, 0.0))

            line_text = lines[idx].strip()
            if not line_text or line_text in {"{", "}"}:
                continue

            score_val = round(sc, 6)
            if sc >= MIN_LINE_SCORE:
                highlights.append({"line": idx + 1, "score": score_val, "snippet": line_text})

    # sort and unique top results
    highlights.sort(key=lambda x: x["score"], reverse=True)
    seen = set()
    out = []
    for h in highlights:
        if h["line"] not in seen:
            out.append(h)
            seen.add(h["line"])
        if len(out) >= top_funcs * top_lines:
            break

    return out


# ---------- Updated analyze endpoint (calls the new helpers and skips highlights when safe) ----------
@app.post("/api/analyze", response_model=AnalyzeOut)
async def analyze(
    request: Request,
    code: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    model: str = Form("knn"),
):
    start_time = time.time()

    if not code and not file:
        raise HTTPException(status_code=400, detail="No input provided (code or file).")

    try:
        raw_code = (await file.read()).decode("utf-8", errors="ignore") if file else code
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File read failed: {str(e)}")

    # vectorize + scale for prediction
    try:
        processed = preprocess_code(raw_code)
        X_vec = VECTORIZER.transform([processed])
        X_dense = X_vec.toarray() if hasattr(X_vec, "toarray") else np.asarray(X_vec)
        # select scaler
        scaler = RF_SCALER if model == "rf" else KNN_SCALER
        try:
            X_scaled = scaler.transform(X_dense) if scaler is not None else X_dense
        except Exception:
            X_scaled = X_dense
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vectorization failed: {str(e)}")

    # compute main prediction and base_score (single call)
    result_label = None
    confidence = None
    base_score = None

    try:
        if model == "knn":
            if KNN is None:
                raise HTTPException(status_code=500, detail="KNN model not loaded.")
            pred = int(KNN.predict(X_scaled)[0])
            proba = float(KNN.predict_proba(X_scaled).max()) if hasattr(KNN, "predict_proba") else None
            result_label = "Vulnerable" if pred == 1 else "Safe"
            confidence = proba
            base_score = proba if proba is not None else float(pred)
        elif model == "rf":
            if RF is None:
                raise HTTPException(status_code=500, detail="RF model not loaded.")
            risk_score = float(RF.predict(X_scaled)[0])
            result_label = "Safe" if risk_score < 0.3 else "Vulnerable"
            confidence = risk_score
            base_score = risk_score
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model '{model}'")
    except Exception as e:
        print(f"Model prediction failed ({model}):", e)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    # Determine whether to run detailed region search
    MIN_CONF_TO_EXPLAIN = 0.35  # only explain if base_score >= threshold
    highlights = []
    if base_score is not None and result_label == "Vulnerable" and base_score >= MIN_CONF_TO_EXPLAIN:
        try:
            highlights = locate_vulnerable_regions(raw_code, model_name=model, top_funcs=2, top_lines=5, base_score=base_score)
        except Exception as e:
            print("locate_vulnerable_regions failed:", e)
            highlights = []
    else:
        # if safe or low confidence, do not show highlights
        highlights = []

    elapsed = round(time.time() - start_time, 3)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    result_obj = AnalyzeOut(
        result=result_label,
        confidence=confidence,
        processing_time_sec=elapsed,
        timestamp=timestamp,
        highlights=highlights,
    )

    # Save to history (only if token is valid)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        email = authenticate_token(token)
        if email:
            _save_history(email, result_obj.dict())

    return result_obj


# ------------------------------------------------------------
# Step 11. Retrieve user history (used by HistoryPage.js)
@app.get("/api/history")
def get_history(request: Request, db=Depends(get_db)):
    # Step 1. Extract token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Authorization header missing or invalid."
        )

    token = auth_header.split(" ")[1]
    email = authenticate_token(token)

    # Step 2. Validate token
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    # Step 3. Return user's history records
    user_history = HISTORY.get(email, [])
    print(f"[history] Returning {len(user_history)} records for {email}")

    return {"email": email, "total_records": len(user_history), "history": user_history}


# ------------------------------------------------------------
# Step 12. Update user profile (PUT method using BaseModel)


@app.put("/api/user/update")
def update_user(
    request: Request, payload: UpdateUserIn, db=Depends(get_db)  # Receive as JSON body
):
    """
    Update user profile information (name or password).
    Uses BaseModel for structured validation and cleaner design.
    """

    # Step 1. Check authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Authorization header missing or invalid."
        )

    # Step 2. Validate token and get user email
    token = auth_header.split(" ")[1]
    email = authenticate_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    # Step 3. Check if user exists
    user = USERS.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Step 4. Validate input (at least one field must be provided)
    if not payload.name and not payload.password:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    # Step 5. Update user information
    if payload.name:
        user["name"] = payload.name
    if payload.password:
        user["password"] = payload.password

    USERS[email] = user
    print(f"[update] Profile updated for {email}")

    # Step 6. Return success response
    return {
        "message": "User profile updated successfully.",
        "updated_user": {"name": user["name"], "email": user["email"]},
    }


# ------------------------------------------------------------
# Step 13. Delete all analysis history for the authenticated user (DELETE method)
@app.delete("/api/history/delete")
def delete_history(request: Request, db=Depends(get_db)):
    """
    Clear all analysis history for the currently authenticated user.
    Keeps the user account intact.
    """

    # Step 1. Extract token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Authorization header missing or invalid."
        )

    # Step 2. Validate token and get email
    token = auth_header.split(" ")[1]
    email = authenticate_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    # Step 3. Check if user exists
    if email not in USERS:
        raise HTTPException(status_code=404, detail="User not found.")

    # Step 4. Clear user's history
    if email in HISTORY:
        HISTORY[email].clear()
        print(f"[history] All records deleted for {email}")
    else:
        HISTORY[email] = []

    # Step 5. Return confirmation message
    return {"message": "All analysis history has been cleared successfully."}


# ------------------------------------------------------------
# Visualization endpoints => by Will
# ------------------------------------------------------------


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


def compute_class_distribution(df):
    """"""


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


def prepare_visualization_payload(df):
    return {
        "token_frequency": compute_token_frequency(df),
        "class_distribution": compute_class_distribution(df),
        "language_distribution": compute_language_distribution(df),
    }


@app.get("/api/visualization")
def get_all_visualization_data():
    try:
        DATAFRAME = pd.read_csv("./data/processed_dataset_final.csv", low_memory=False)
    except Exception as e:
        DATAFRAME = None
        raise HTTPException(status_code=500, detail=f"Failed to load dataset: {str(e)}")
    if DATAFRAME is None:
        raise HTTPException(status_code=501, detail="Dataset not loaded.")
    return prepare_visualization_payload(DATAFRAME)


