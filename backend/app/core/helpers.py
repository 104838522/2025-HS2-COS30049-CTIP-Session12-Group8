# ------- Helper functions and dependencies
import uuid
from typing import Optional, Dict, List
from app.db.memory_db import TOKENS, HISTORY

# Simulated database dependency
def get_db():
    return {"db": "Simulated database connection"}

# Token generation and authentication
def _generate_token() -> str:
    return str(uuid.uuid4())

# Authenticate token and return associated email
def authenticate_token(token: str) -> Optional[str]:
    return TOKENS.get(token)

# Save history entry for a user
def _save_history(email: str, entry: dict):
    lst = HISTORY.setdefault(email, [])
    lst.append(entry)
    print(f"[history] Saved record for {email} (total {len(lst)})")
