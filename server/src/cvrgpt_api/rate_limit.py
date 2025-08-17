from fastapi_limiter import FastAPILimiter
from .redis_client import redis_client
import logging

logger = logging.getLogger(__name__)


async def init_rate_limiter():
    try:
        await FastAPILimiter.init(redis_client)
        logger.info("FastAPILimiter initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize FastAPILimiter: {e}. Rate limiting will be disabled.")
