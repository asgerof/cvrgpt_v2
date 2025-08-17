import redis.asyncio as redis  # type: ignore
from .config import settings

redis_client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
