# Endpoint - Analyze (AI Prediction)
from fastapi import APIRouter, Form, File, UploadFile, HTTPException, Request, Depends
import time, traceback, hashlib, warnings
import numpy as np
import pandas as pd
from app.utils.preprocess import preprocess_code
from app.services.ai_service import VECTORIZER, KNN_SCALER, RF_SCALER, KNN, RF
from app.core.helpers import get_db, authenticate_token, _save_history
from app.models.schemas import AnalyzeOut

router = APIRouter()


# ---------- Helper function for analyze: predict probability/score ----------
def predict_score_from_text(text: str, model_name: str = "knn"):
    """
    Return a single score for the given code text.
    If the required model/scaler/vectorizer is not available, return None.
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

        # apply scaler safely (handle feature names)
        try:
            if scaler is not None:
                feature_names = getattr(scaler, "feature_names_in_", None)
                if feature_names is not None and len(feature_names) == X_dense.shape[1]:
                    X_df = pd.DataFrame(X_dense, columns=feature_names)
                    Xs = scaler.transform(X_df)
                else:
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
        else:
            if model is None:
                return None
            if hasattr(model, "predict_proba"):
                return float(model.predict_proba(Xs).max())
            else:
                pred = int(model.predict(Xs)[0])
                return float(pred)
    except Exception as e:
        print("predict_score_from_text failed:", e)
        print(traceback.format_exc())
        return None


# ---------- Helper: simple function splitter ----------
def simple_function_split(lines):
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


# ---------- Main locator ----------
def locate_vulnerable_regions(
    raw_code: str,
    model_name: str = "knn",
    top_funcs: int = 3,
    top_lines: int = 5,
    base_score: float = None,
):
    """
    Identify lines that reduce the model score when removed.
        - model_name: "knn" or "rf"
    - base_score: if provided, reuse instead of recalculating
    Returns list of dicts: {line, score, snippet}"""
    lines = raw_code.splitlines()
    if len(lines) == 0:
        return []
    if base_score is None:
        base_score = predict_score_from_text(raw_code, model_name=model_name)
    blocks = simple_function_split(lines)
    func_scores = []

    for s, e in blocks:
        masked = lines.copy()
        for idx in range(s, e + 1):
            masked[idx] = ""
        masked_text = "\n".join(masked)
        p = predict_score_from_text(masked_text, model_name=model_name)
        if base_score is None or p is None:
            score = 0.0
        else:
            try:
                score = float(max(base_score - p, 0.0))
            except Exception:
                score = 0.0
        func_scores.append((s, e, score))

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
                sc = 0.0
            else:
                sc = float(max(base_score - p, 0.0))
            line_text = lines[idx].strip()
            if not line_text or line_text in {"{", "}"}:
                continue
            score_val = round(sc, 6)
            if sc >= MIN_LINE_SCORE:
                highlights.append(
                    {"line": idx + 1, "score": score_val, "snippet": line_text}
                )

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


# ---------- Endpoint ----------
@router.post("/analyze", response_model=AnalyzeOut)
async def analyze(
    request: Request,
    code: str = Form(None),
    file: UploadFile = File(None),
    model: str = Form("knn"),
    db=Depends(get_db),
):
    start_time = time.time()
    if not code and not file:
        raise HTTPException(status_code=400, detail="No input provided (code or file).")

    try:
        raw_code = (
            (await file.read()).decode("utf-8", errors="ignore") if file else code
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File read failed: {str(e)}")

    # deterministic hash for history
    content_hash = hashlib.md5(raw_code.encode("utf-8", errors="ignore")).hexdigest()

    try:
        warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

        processed = preprocess_code(raw_code)
        X_vec = VECTORIZER.transform([processed])
        X_dense = X_vec.toarray() if hasattr(X_vec, "toarray") else np.asarray(X_vec)
        scaler = RF_SCALER if model == "rf" else KNN_SCALER

        # Apply scaler safely (handle feature names)
        if scaler is not None:
            feature_names = getattr(scaler, "feature_names_in_", None)
            if feature_names is not None and len(feature_names) == X_dense.shape[1]:
                X_df = pd.DataFrame(X_dense, columns=feature_names)
                X_scaled = scaler.transform(X_df)
            else:
                X_scaled = scaler.transform(X_dense)
        else:
            X_scaled = X_dense
        # ================================================

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vectorization failed: {str(e)}")

    result_label = None
    confidence = None
    base_score = None

    try:
        if model == "knn":
            pred = int(KNN.predict(X_scaled)[0])
            proba = (
                float(KNN.predict_proba(X_scaled).max())
                if hasattr(KNN, "predict_proba")
                else None
            )
            result_label = "Vulnerable" if pred == 1 else "Safe"
            confidence = proba
            base_score = proba if proba is not None else float(pred)
        elif model == "rf":
            risk_score = float(RF.predict(X_scaled)[0])
            result_label = "Safe" if risk_score < 0.3 else "Vulnerable"
            confidence = risk_score
            base_score = risk_score
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model '{model}'")
    except Exception as e:
        print(f"Model prediction failed ({model}):", e)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    MIN_CONF_TO_EXPLAIN = 0.35
    highlights = []
    if (
        base_score is not None
        and result_label == "Vulnerable"
        and base_score >= MIN_CONF_TO_EXPLAIN
    ):
        try:
            highlights = locate_vulnerable_regions(
                raw_code,
                model_name=model,
                top_funcs=2,
                top_lines=5,
                base_score=base_score,
            )
        except Exception as e:
            print("locate_vulnerable_regions failed:", e)
            highlights = []
    else:
        highlights = []

    elapsed = round(time.time() - start_time, 3)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    result_obj = AnalyzeOut(
        result=result_label,
        confidence=confidence,
        processing_time_sec=elapsed,
        timestamp=timestamp,
        content_hash=content_hash,
        highlights=highlights,
    )

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        email = authenticate_token(token)
        if email:
            _save_history(email, result_obj.dict())

    return result_obj
