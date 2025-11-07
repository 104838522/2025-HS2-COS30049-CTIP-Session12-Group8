# ------------------------------------------------------------
# Step 9. Authentication endpoints
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.helpers import get_db, _generate_token, authenticate_token
from app.models.schemas import SignupIn, LoginIn, UpdateUserIn
from app.db.memory_db import USERS, TOKENS

router = APIRouter()

@router.post("/signup")
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


@router.post("/login")
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
