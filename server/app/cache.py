import os
import json
import hashlib
from redis import asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "900"))

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


def key_for(prefix: str, **kwargs) -> str:
    payload = json.dumps(kwargs, sort_keys=True)
    h = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return f"cvrgpt:{prefix}:{h}"


async def cache_get(prefix: str, **kwargs):
    r = await get_redis()
    return await r.get(key_for(prefix, **kwargs))


async def cache_set(prefix: str, value: str, **kwargs):
    r = await get_redis()
    await r.setex(key_for(prefix, **kwargs), TTL_SECONDS, value)
