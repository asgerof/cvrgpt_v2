from fastapi import APIRouter, Request
from time import perf_counter
from typing import Dict

router = APIRouter()
_counters: Dict[str, int] = {
    "requests_total": 0,
    "errors_total": 0,
    "cache_hits": 0,
}


def count(name: str, inc: int = 1) -> None:
    _counters[name] = _counters.get(name, 0) + inc


@router.get("/metrics")
async def metrics():
    return _counters


async def timing_middleware(request: Request, call_next):
    start = perf_counter()
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = int((perf_counter() - start) * 1000)
        # You can wire structlog here; for now, basic print:
        print({"event": "request_completed", "route": request.url.path, "duration_ms": duration_ms})
        count("requests_total", 1)
