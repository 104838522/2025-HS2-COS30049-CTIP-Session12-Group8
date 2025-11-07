from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# ------------------------------------------------------------
# Step 4. Global error handler
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
