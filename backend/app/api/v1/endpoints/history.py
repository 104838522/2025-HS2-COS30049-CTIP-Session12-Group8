# ------------------------------------------------------------
# Step 11 & 13. Retrieve user history + Delete all history
from fastapi import APIRouter, Request, Depends, HTTPException
from app.core.helpers import get_db, authenticate_token
from app.db.memory_db import HISTORY, USERS

router = APIRouter()

# ------------------------------------------------------------
# Step 11. Retrieve user history (used by HistoryPage.js)
@router.get("/")
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
# Step 13. Delete all analysis history for the authenticated user (DELETE method)
@router.delete("/delete")
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
