import time
from fastapi import Request

# ------- Request timing middleware
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(
        f"Request: {request.method} {request.url} - Processing time: {process_time:.4f}s"
    )
    return response

