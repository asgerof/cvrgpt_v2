"""
Error utilities and canonical payloads.
"""

from typing import Optional
from pydantic import BaseModel
from enum import Enum


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


# Suggested usages:
#   raise HTTPException(status_code=404, detail=ErrorPayload(code=ErrorCode.NOT_FOUND, message="Company not found").model_dump())
#   raise HTTPException(status_code=502, detail=ErrorPayload(code=ErrorCode.UPSTREAM_ERROR, message="CVR API unavailable").model_dump())
