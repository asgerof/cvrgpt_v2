from fastapi_limiter import FastAPILimiter
from .redis_client import redis_client


async def init_rate_limiter():
    await FastAPILimiter.init(redis_client)
