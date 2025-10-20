from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import time
import uuid

#  Step 1. Create FastAPI instance
app = FastAPI(title="VulnLocator API")

#  Step 2. CORS settings (allow communication with React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Step 3. Request processing time logging (Middleware)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request: {request.method} {request.url} - Processing time: {process_time:.4f}s")
    return response

#  Step 4. Error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": "An error occurred"}
    )
#========================================================================
#  Step 5. Temporary "database" (in-memory storage)
USERS: Dict[str, Dict] = {}         # email -> user info
TOKENS: Dict[str, str] = {}        # token -> email
HISTORY: Dict[str, List[Dict]] = {} # email -> analysis history

#  Step 6. Pydantic models
class SignupIn(BaseModel):
    name: str
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

class AnalyzeIn(BaseModel):
    code: str
    token: Optional[str] = None

class Issue(BaseModel):
    line: int
    severity: str
    desc: Optional[str] = None

class AnalyzeOut(BaseModel):
    summary: str
    issues: List[Issue]
#========================================================================
# Step 7. Dependency (fake DB connection)
def get_db():
    return {"db": "Simulated database connection"}

# Step 8. Auth helper functions
def _generate_token() -> str:
    return str(uuid.uuid4())

def authenticate_token(token: str) -> Optional[str]:
    """Return email if token is valid."""
    return TOKENS.get(token)

# Step 9. Save history in background
def _save_history(email: str, entry: dict):
    lst = HISTORY.setdefault(email, [])
    lst.append(entry)
    print(f"[history] Saved record for {email} (total {len(lst)})")

# Step 10. Signup
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

#  Step 11. Login
@app.post("/api/auth/login")
def login(payload: LoginIn, db=Depends(get_db)):
    user = USERS.get(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = _generate_token()
    TOKENS[token] = payload.email
    print(f"[auth] {payload.email} logged in, token: {token}")
    return {"message": "Login successful", "token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}

#  Step 12. Code vulnerability analysis API
@app.post("/api/analyze", response_model=AnalyzeOut)
def analyze(payload: AnalyzeIn, background_tasks: BackgroundTasks, db=Depends(get_db)):
    code = payload.code or ""
    issues = []
    for idx, line in enumerate(code.splitlines(), start=1):
        l = line.lower()
        if "eval(" in l or "exec(" in l:
            issues.append({"line": idx, "severity": "Medium", "desc": "Use of eval/exec is a security risk"})
        elif "select " in l or "sql" in l or "insert " in l:
            issues.append({"line": idx, "severity": "High", "desc": "SQL-related code found (possible SQL Injection)"})
        elif "system(" in l or "popen(" in l:
            issues.append({"line": idx, "severity": "High", "desc": "OS command execution detected"})
    summary = f"Found {len(issues)} potential vulnerabilities"
    result = {"summary": summary, "issues": issues}

    # If token provided and valid, save history
    if payload.token:
        email = authenticate_token(payload.token)
        if email:
            entry = {"summary": summary, "issues": issues, "timestamp": int(time.time())}
            background_tasks.add_task(_save_history, email, entry)

    return result

#  Step 13. Get analysis history API
@app.get("/api/history")
def get_history(token: str, db=Depends(get_db)):
    email = authenticate_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token.")
    return {"email": email, "history": HISTORY.get(email, [])}
