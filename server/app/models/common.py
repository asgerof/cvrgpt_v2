from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class Source(BaseModel):
    url: HttpUrl
    label: str
    accessed_at: datetime


class ErrorDetail(BaseModel):
    code: str = Field(
        pattern=r"^(NOT_FOUND|UPSTREAM_ERROR|RATE_LIMIT|PROVIDER_DOWN|INSUFFICIENT_DATA|VALIDATION_ERROR)$"
    )
    message: str
    details: dict | None = None
    sources: list[Source] = []


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
