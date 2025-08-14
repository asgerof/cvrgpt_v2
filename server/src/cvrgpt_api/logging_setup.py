import structlog
import sys
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

structlog.configure(processors=[structlog.processors.JSONRenderer()])

log = structlog.get_logger()

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["x-request-id"] = rid
        log.info("request", method=request.method, path=request.url.path, status=response.status_code, rid=rid)
        return response
