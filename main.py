# main.py
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import time
import uuid

# ✅ Step 1. FastAPI 인스턴스 생성
app = FastAPI(title="VulnLocator API")

# ✅ Step 2. CORS 설정 (React와 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Step 3. 요청 처리 시간 로깅 (Middleware)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"요청: {request.method} {request.url} - 처리 시간: {process_time:.4f}초")
    return response

# ✅ Step 4. 에러 처리 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": "에러가 발생했습니다"}
    )

# ✅ Step 5. 임시 "데이터베이스" (메모리에 저장)
USERS: Dict[str, Dict] = {}         # email → 사용자 정보
TOKENS: Dict[str, str] = {}         # token → email
HISTORY: Dict[str, List[Dict]] = {} # email → 분석기록

# ✅ Step 6. Pydantic 모델 정의
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

# ✅ Step 7. 의존성 (가짜 DB 연결)
def get_db():
    return {"db": "가짜 데이터베이스 연결"}

# ✅ Step 8. 인증 관련 보조 함수
def _generate_token() -> str:
    return str(uuid.uuid4())

def authenticate_token(token: str) -> Optional[str]:
    """토큰이 유효하면 이메일을 반환"""
    return TOKENS.get(token)

# ✅ Step 9. 백그라운드로 분석기록 저장
def _save_history(email: str, entry: dict):
    lst = HISTORY.setdefault(email, [])
    lst.append(entry)
    print(f"[history] {email} 기록 저장 완료 (총 {len(lst)}개)")

# ✅ Step 10. 회원가입
@app.post("/api/auth/signup")
def signup(payload: SignupIn, db=Depends(get_db)):
    if payload.email in USERS:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    user_id = f"user-{len(USERS)+1}"
    USERS[payload.email] = {
        "id": user_id,
        "name": payload.name,
        "email": payload.email,
        "password": payload.password
    }
    print(f"[auth] 신규 회원: {payload.email}")
    return {"message": "회원가입 성공", "user": {"id": user_id, "name": payload.name, "email": payload.email}}

# ✅ Step 11. 로그인
@app.post("/api/auth/login")
def login(payload: LoginIn, db=Depends(get_db)):
    user = USERS.get(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")
    token = _generate_token()
    TOKENS[token] = payload.email
    print(f"[auth] {payload.email} 로그인 성공, 토큰: {token}")
    return {"message": "로그인 성공", "token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}

# ✅ Step 12. 코드 취약점 분석 API
@app.post("/api/analyze", response_model=AnalyzeOut)
def analyze(payload: AnalyzeIn, background_tasks: BackgroundTasks, db=Depends(get_db)):
    code = payload.code or ""
    issues = []
    for idx, line in enumerate(code.splitlines(), start=1):
        l = line.lower()
        if "eval(" in l or "exec(" in l:
            issues.append({"line": idx, "severity": "Medium", "desc": "eval/exec 사용은 보안상 위험"})
        elif "select " in l or "sql" in l or "insert " in l:
            issues.append({"line": idx, "severity": "High", "desc": "SQL 관련 코드 발견 (SQL Injection 가능성)"})
        elif "system(" in l or "popen(" in l:
            issues.append({"line": idx, "severity": "High", "desc": "OS 명령 실행 감지"})
    summary = f"{len(issues)}개의 잠재적 취약점 발견"
    result = {"summary": summary, "issues": issues}

    # 로그인된 사용자면 기록 저장
    if payload.token:
        email = authenticate_token(payload.token)
        if email:
            entry = {"summary": summary, "issues": issues, "timestamp": int(time.time())}
            background_tasks.add_task(_save_history, email, entry)

    return result

# ✅ Step 13. 분석 기록 조회 API
@app.get("/api/history")
def get_history(token: str, db=Depends(get_db)):
    email = authenticate_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    return {"email": email, "history": HISTORY.get(email, [])}
