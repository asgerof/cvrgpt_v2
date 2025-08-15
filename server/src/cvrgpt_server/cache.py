import hashlib
import orjson
from starlette.responses import Response
from fastapi import Request
from .redis_client import redis_client


def _key(prefix: str, *parts: str) -> str:
    return prefix + ":" + ":".join(parts)


async def cache_get(key: str):
    val = await redis_client.get(key)
    return orjson.loads(val) if val else None


async def cache_set(key: str, data: dict, ttl: int):
    await redis_client.set(key, orjson.dumps(data), ex=ttl)


def with_etag(request: Request, payload: dict, ttl: int) -> Response:
    body = orjson.dumps(payload)
    etag = hashlib.md5(body, usedforsecurity=False).hexdigest()  # nosec B324
    inm = request.headers.get("if-none-match")
    if inm and inm == etag:
        return Response(status_code=304)
    resp = Response(content=body, media_type="application/json")
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = f"public, max-age={ttl}"
    return resp
