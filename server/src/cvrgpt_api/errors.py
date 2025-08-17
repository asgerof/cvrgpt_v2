"""
Error utilities and canonical payloads.
"""

import uuid
from typing import Optional
from pydantic import BaseModel
from enum import Enum
from fastapi import Request, status
from fastapi.responses import JSONResponse


class ErrorCode(str, Enum):
    NOT_FOUND = "NOT_FOUND"
    UPSTREAM_ERROR = "UPSTREAM_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    PROVIDER_DOWN = "PROVIDER_DOWN"
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ErrorPayload(BaseModel):
    code: ErrorCode
    message: str
    detail: Optional[str] = None
    retry_after: Optional[int] = None  # seconds


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str


def with_request_id() -> str:
    """Generate a unique request ID."""
    return uuid.uuid4().hex


def make_error(code: str, message: str, status_code: int, request_id: str) -> JSONResponse:
    """Create a standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(code=code, message=message, request_id=request_id).model_dump(),
    )


async def not_found_handler(request: Request, exc) -> JSONResponse:
    """Handle 404 Not Found errors."""
    rid = request.headers.get("x-request-id", with_request_id())
    return make_error("NOT_FOUND", "Resource not found", status.HTTP_404_NOT_FOUND, rid)


async def upstream_handler(request: Request, exc) -> JSONResponse:
    """Handle upstream service errors."""
    rid = request.headers.get("x-request-id", with_request_id())
    return make_error("UPSTREAM_ERROR", "Upstream service error", status.HTTP_502_BAD_GATEWAY, rid)


async def validation_error_handler(request: Request, exc) -> JSONResponse:
    """Handle validation errors."""
    rid = request.headers.get("x-request-id", with_request_id())
    return make_error("VALIDATION_ERROR", "Invalid request data", status.HTTP_422_UNPROCESSABLE_ENTITY, rid)


async def internal_error_handler(request: Request, exc) -> JSONResponse:
    """Handle internal server errors."""
    rid = request.headers.get("x-request-id", with_request_id())
    return make_error("INTERNAL_ERROR", "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, rid)


# Suggested usages:
#   raise HTTPException(status_code=404, detail=ErrorPayload(code=ErrorCode.NOT_FOUND, message="Company not found").model_dump())
#   raise HTTPException(status_code=502, detail=ErrorPayload(code=ErrorCode.UPSTREAM_ERROR, message="CVR API unavailable").model_dump())
