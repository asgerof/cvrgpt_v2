"""
Error utilities and canonical payloads.
"""
from typing import Optional
from pydantic import BaseModel

class ErrorPayload(BaseModel):
    code: str
    detail: Optional[str] = None

# Suggested usages in endpoints:
#   raise HTTPException(status_code=404, detail=ErrorPayload(code="NOT_FOUND", detail="...").model_dump())
#   raise HTTPException(status_code=502, detail=ErrorPayload(code="UPSTREAM_ERROR", detail="...").model_dump())
