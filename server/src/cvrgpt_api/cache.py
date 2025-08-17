import json, os, time
from typing import Any, Callable
import hashlib
from starlette.responses import Response
from fastapi import Request

try:
    import redis  # type: ignore
except Exception:
    redis = None

REDIS_URL = os.getenv("REDIS_URL")

class Cache:
    def __init__(self):
        self._mem: dict[str, tuple[float, str]] = {}
        self._r = redis.Redis.from_url(REDIS_URL) if (redis and REDIS_URL) else None

    def get(self, key: str) -> Any | None:
        if self._r:
            v = self._r.get(key)
            return json.loads(v) if v else None
        v = self._mem.get(key)
        if not v: return None
        expires_at, data = v
        if time.time() > expires_at:
            self._mem.pop(key, None); return None
        return json.loads(data)

    def set(self, key: str, value: Any, ttl_seconds: int):
        s = json.dumps(value, default=str)
        if self._r:
            self._r.setex(key, ttl_seconds, s)
        else:
            self._mem[key] = (time.time() + ttl_seconds, s)

cache = Cache()

def cached(ttl: int, key_fn: Callable[..., str]):
    def deco(fn):
        async def wrap(*args, **kwargs):
            key = key_fn(*args, **kwargs)
            hit = cache.get(key)
            if hit is not None: return hit
            val = await fn(*args, **kwargs)
            cache.set(key, val, ttl)
            return val
        return wrap
    return deco


def _key(prefix: str, *parts: str) -> str:
    return prefix + ":" + ":".join(parts)


async def cache_get(key: str):
    return cache.get(key)


async def cache_set(key: str, data: dict, ttl: int):
    cache.set(key, data, ttl)


def with_etag(request: Request, payload: dict, ttl: int) -> Response:
    body = json.dumps(payload, default=str).encode()
    etag = hashlib.md5(body, usedforsecurity=False).hexdigest()  # nosec B324
    inm = request.headers.get("if-none-match")
    if inm and inm == etag:
        return Response(status_code=304)
    resp = Response(content=body, media_type="application/json")
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = f"public, max-age={ttl}"
    return resp
