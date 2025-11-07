# ------------------------------------------------------------
# Step 7. Helper functions and dependencies
import uuid
from typing import Optional, Dict, List
from app.db.memory_db import TOKENS, HISTORY

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
