import os
from fastapi import Header, HTTPException, status

API_KEY_ENV = "API_KEY"


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    expected = os.getenv(API_KEY_ENV)
    # if expected is set, enforce; if not set (local dev), allow all
    if expected:
        if not x_api_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")
        if x_api_key != expected:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
