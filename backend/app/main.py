# Entry point for FastAPI application
# ------------------------------------------------------------
# Step 1. Initialize FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import log_requests
from app.core.exceptions import http_exception_handler
from app.api.v1.endpoints import auth, analyze, history, user, visualization

app = FastAPI(title="VulnLocator AI API")

# ------------------------------------------------------------
# Step 2. Configure CORS (for React frontend connection)...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# Step 3. Request timing middleware
app.middleware("http")(log_requests)

# ------------------------------------------------------------
# Step 4. Global error handler
app.exception_handler(Exception)(http_exception_handler)

# ------------------------------------------------------------
# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(
    visualization.router, prefix="/api/visualization", tags=["Visualization"]
)
