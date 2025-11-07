#  In-memory temporary database (for user accounts and history)
from typing import Dict, List 

USERS: Dict[str, Dict] = {}
TOKENS: Dict[str, str] = {}
HISTORY: Dict[str, List[Dict]] = {}
