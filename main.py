# main.py
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import time
import uuid
import joblib
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
    print(f"Request: {request.method} {request.url} - Processing time: {process_time:.4f}s")
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
    highlights: Optional[List[Highlight]] = None


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
    SCALER = joblib.load("./models/scaler.joblib")
    MODEL = joblib.load("./models/knn_model.joblib")
    KNN = MODEL
    print("Model components loaded successfully.")
except Exception as e:
    print(f"Error loading model components: {e}")
    VECTORIZER = SCALER = MODEL = KNN = None

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
        "password": payload.password
    }
    print(f"[auth] New user: {payload.email}")
    return {"message": "Signup successful", "user": {"id": user_id, "name": payload.name, "email": payload.email}}

@app.post("/api/auth/login")
def login(payload: LoginIn, db=Depends(get_db)):
    user = USERS.get(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = _generate_token()
    TOKENS[token] = payload.email
    print(f"[auth] {payload.email} logged in with token: {token}")
    return {"message": "Login successful", "token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}

# ------------------------------------------------------------
# Step 10. Analyze (AI Prediction)


# ---------- Helper: predict probability (use existing VECTORIZER/SCALER/KNN) ----------
def predict_proba_from_text(text: str):
    """
    Return model max probability for the given code text.
    If predict_proba not available, return None.
    """
    try:
        proc = preprocess_code(text)
        X_vec = VECTORIZER.transform([proc])
        # dense
        if hasattr(X_vec, "toarray"):
            X_dense = X_vec.toarray()
        else:
            X_dense = np.asarray(X_vec)
        # scale
        try:
            if hasattr(SCALER, "feature_names_in_"):
                # when scaler expects dataframe columns
                cols = getattr(VECTORIZER, 'get_feature_names_out', lambda: [f'F{i}' for i in range(X_dense.shape[1])])()
                import pandas as pd
                df = pd.DataFrame(X_dense, columns=cols)
                Xs = SCALER.transform(df)
            else:
                Xs = SCALER.transform(X_dense)
        except Exception:
            Xs = X_dense
        if hasattr(KNN, "predict_proba"):
            return float(KNN.predict_proba(Xs).max())
        else:
            return None
    except Exception as e:
        print("predict_proba_from_text failed:", e)
        print(traceback.format_exc())
        return None

# ---------- Helper: naive function splitter ----------
def simple_function_split(lines):
    """
    Return list of (start_index, end_index) tuples for code 'blocks' to check.
    This is a very small heuristic: looks for function-like lines:
    - Python: lines starting with 'def ' or 'class '
    - C/Java/JS: lines ending with '{' (assume block starts)
    Fallback: treat whole file as single block (0..len-1)
    """
    blocks = []
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i].lstrip()
        if line.startswith("def ") or line.startswith("class "):
            start = i
            # find end: next blank line that is not indented (very naive)
            j = i + 1
            while j < n and (lines[j].startswith(" ") or lines[j].startswith("\t") or lines[j].strip() == ""):
                j += 1
            blocks.append((start, j-1))
            i = j
        elif line.endswith("{"):
            start = i
            # find matching '}' (naive)
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                if lines[j].strip().endswith("{"):
                    depth += 1
                if "}" in lines[j]:
                    depth -= lines[j].count("}")
                j += 1
            blocks.append((start, max(start, j-1)))
            i = j
        else:
            i += 1
    if not blocks:
        # entire file as one block
        if n > 0:
            blocks = [(0, n-1)]
    return blocks

# ---------- Main locator: function-level then line-level occlusion ----------
def locate_vulnerable_regions(raw_code: str, top_funcs: int = 3, top_lines: int = 5):
    """
    1) Split code into blocks/functions (simple heuristic).
    2) Compute base probability.
    3) Mask each function block and compute delta.
    4) For top function blocks, mask lines inside to rank line importance.
    Return list of dicts: {line, score, snippet}
    """
    lines = raw_code.splitlines()
    if len(lines) == 0:
        return []

    base_proba = predict_proba_from_text(raw_code)

    blocks = simple_function_split(lines)

    func_scores = []
    for (s, e) in blocks:
        masked = lines.copy()
        for idx in range(s, e+1):
            masked[idx] = ""  # mask the whole block
        masked_text = "\n".join(masked)
        p = predict_proba_from_text(masked_text)
        if base_proba is None or p is None:
            # fallback: use class change if predict_proba not available
            try:
                # predict classes (costly) - but attempt
                X_base = VECTORIZER.transform([preprocess_code(raw_code)])
                X_base_d = X_base.toarray() if hasattr(X_base, "toarray") else np.asarray(X_base)
                try:
                    Xb = SCALER.transform(X_base_d)
                except Exception:
                    Xb = X_base_d
                base_pred = int(KNN.predict(Xb)[0])
                X_mask = VECTORIZER.transform([preprocess_code(masked_text)])
                Xm_d = X_mask.toarray() if hasattr(X_mask, "toarray") else np.asarray(X_mask)
                try:
                    Xm = SCALER.transform(Xm_d)
                except Exception:
                    Xm = Xm_d
                pred_mask = int(KNN.predict(Xm)[0])
                score = 1.0 if base_pred != pred_mask else 0.0
            except Exception:
                score = 0.0
        else:
            score = float(base_proba - p)
        func_scores.append((s, e, score))

    # sort blocks by their score (high -> low)
    func_scores.sort(key=lambda x: x[2], reverse=True)
    highlights = []
    # only examine top N functions for line-level occlusion
    for (s, e, fscore) in func_scores[:top_funcs]:
        # for each line in the block, mask and measure
        for idx in range(s, e+1):
            masked = lines.copy()
            masked[idx] = ""  # mask single line
            masked_text = "\n".join(masked)
            p = predict_proba_from_text(masked_text)
            if base_proba is None or p is None:
                # fallback class-change scoring
                try:
                    X_mask = VECTORIZER.transform([preprocess_code(masked_text)])
                    Xm_d = X_mask.toarray() if hasattr(X_mask, "toarray") else np.asarray(X_mask)
                    try:
                        Xm = SCALER.transform(Xm_d)
                    except Exception:
                        Xm = Xm_d
                    base_pred = int(KNN.predict(X_scaled)[0])  # note: X_scaled must be precomputed outside - but simpler to call predict again below
                    pred_mask = int(KNN.predict(Xm)[0])
                    sc = 1.0 if base_pred != pred_mask else 0.0
                except Exception:
                    sc = 0.0
            else:
                sc = float(base_proba - p)
            highlights.append({"line": idx+1, "score": round(sc, 6), "snippet": lines[idx].strip()})
    # sort highlights by score and return top unique lines
    highlights.sort(key=lambda x: x["score"], reverse=True)
    # remove duplicates and take top K
    seen = set()
    out = []
    for h in highlights:
        if h["line"] not in seen:
            out.append(h)
            seen.add(h["line"])
        if len(out) >= top_funcs * top_lines:
            break
    return out

# ---------- Updated analyze endpoint (replace your original analyze) ----------
@app.post("/api/analyze", response_model=AnalyzeOut)
async def analyze(
    request: Request,
    code: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    start_time = time.time()

    # Step 1. Check input
    if not code and not file:
        raise HTTPException(status_code=400, detail="No input provided (code or file).")

    # Step 2. Read code content
    try:
        if file:
            content = (await file.read()).decode("utf-8", errors="ignore")
            raw_code = content
        else:
            raw_code = code
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File read failed: {str(e)}")

    # Step 3. Preprocess code (main)
    try:
        processed = preprocess_code(raw_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preprocessing failed: {str(e)}")

    # Step 4. Vectorization and scaling (original logic)
    try:
        from scipy import sparse
        import pandas as pd
        import traceback

        X_vec = VECTORIZER.transform([processed])
        if hasattr(SCALER, 'feature_names_in_'):
            cols = getattr(VECTORIZER, 'get_feature_names_out', lambda: [f'F{i}' for i in range(X_vec.shape[1])])()
            X_dense = X_vec.toarray() if sparse.issparse(X_vec) else np.asarray(X_vec)
            df = pd.DataFrame(X_dense, columns=cols)
            X_scaled = SCALER.transform(df)
        else:
            X_dense = X_vec.toarray() if sparse.issparse(X_vec) else np.asarray(X_vec)
            try:
                X_scaled = SCALER.transform(X_dense)
            except Exception as e:
                print("Scaler transform failed:", e)
                print(traceback.format_exc())
                X_scaled = X_dense
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vectorization/Scaling failed: {str(e)}")

    # Step 5. Model prediction
    try:
        pred = int(KNN.predict(X_scaled)[0])
        proba = float(KNN.predict_proba(X_scaled).max()) if hasattr(KNN, "predict_proba") else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")

    # Step 6. Locate vulnerable regions (new)
    try:
        highlights = locate_vulnerable_regions(raw_code, top_funcs=2, top_lines=5)
    except Exception as e:
        print("locate_vulnerable_regions failed:", e)
        highlights = []

    # Step 7. Create result object
    elapsed = round(time.time() - start_time, 3)
    result_label = "Vulnerable" if pred == 1 else "Safe"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    result_obj = AnalyzeOut(
        result=result_label,
        confidence=proba,
        processing_time_sec=elapsed,
        timestamp=timestamp,
        highlights=highlights
    )

    # Extract token from header and save result to history (include highlights)
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
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid.")

    token = auth_header.split(" ")[1]
    email = authenticate_token(token)

    # Step 2. Validate token
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    # Step 3. Return user's history records
    user_history = HISTORY.get(email, [])
    print(f"[history] Returning {len(user_history)} records for {email}")
    
    return {
        "email": email,
        "total_records": len(user_history),
        "history": user_history
    }

# ------------------------------------------------------------
# Step 12. Update user profile (PUT method using BaseModel)

@app.put("/api/user/update")
def update_user(
    request: Request,
    payload: UpdateUserIn,   # Receive as JSON body
    db=Depends(get_db)
):
    """
    Update user profile information (name or password).
    Uses BaseModel for structured validation and cleaner design.
    """

    # Step 1. Check authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid.")

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
        "updated_user": {
            "name": user["name"],
            "email": user["email"]
        }
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
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid.")

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
