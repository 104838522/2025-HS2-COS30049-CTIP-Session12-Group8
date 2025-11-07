# Endpoint: Update user profile (PUT method using BaseModel)
from fastapi import APIRouter, Request, Depends, HTTPException
from app.core.helpers import get_db, authenticate_token
from app.models.schemas import UpdateUserIn
from app.db.memory_db import USERS

router = APIRouter()

# ---------- Endpoint: Update user profile ----------
@router.put("/update")
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
