from starlette.middleware.base import BaseHTTPMiddleware
import uuid
from starlette.requests import Request


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        cid = request.headers.get("x-correlation-id", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["x-correlation-id"] = cid
        return response
