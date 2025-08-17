import secrets
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED
from .config import settings

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def require_api_key(key: str = Security(api_key_header)):
    if not key or not secrets.compare_digest(key, settings.endpoint_api_key):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid or missing API key."},
        )
