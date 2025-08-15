from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models.common import ErrorEnvelope, ErrorDetail
from app.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.middleware import CorrelationIdMiddleware
from app.metrics import req_counter, latency_hist
from app.routers import company
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
import time
import os

app = FastAPI(title="cvrgpt_v2 API", version="1.0.0")

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CorrelationIdMiddleware)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        resp = await call_next(request)
        dur = time.perf_counter() - start
        req_counter.labels(request.url.path, request.method, str(resp.status_code)).inc()
        latency_hist.labels(request.url.path, request.method).observe(dur)
        return resp


app.add_middleware(MetricsMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
def ratelimit_handler(request, exc):
    from fastapi.responses import JSONResponse
    from app.models.common import ErrorEnvelope, ErrorDetail

    env = ErrorEnvelope(
        error=ErrorDetail(code="RATE_LIMIT", message="Too many requests", details=None, sources=[])
    )
    return JSONResponse(status_code=429, content=env.model_dump())


@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    env = ErrorEnvelope(
        error=ErrorDetail(
            code="UPSTREAM_ERROR"
            if exc.status_code >= 500
            else "NOT_FOUND"
            if exc.status_code == 404
            else "VALIDATION_ERROR",
            message=str(exc.detail),
            sources=[],
        )
    )
    return JSONResponse(status_code=exc.status_code, content=env.model_dump())


app.include_router(company.router)


@app.get("/health", tags=["meta"])
async def health():
    return {"ok": True, "time": datetime.now(timezone.utc).isoformat()}


@app.get("/metrics")
async def metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    data = generate_latest()  # bytes
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
