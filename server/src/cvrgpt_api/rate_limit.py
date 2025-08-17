try:
    from fastapi_limiter import FastAPILimiter
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    FastAPILimiter = None
    RATE_LIMITING_AVAILABLE = False

from .redis_client import redis_client
import logging

logger = logging.getLogger(__name__)


async def init_rate_limiter():
    if not RATE_LIMITING_AVAILABLE:
        logger.warning("fastapi-limiter not available. Rate limiting will be disabled.")
        return
    
    try:
        await FastAPILimiter.init(redis_client)
        logger.info("FastAPILimiter initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize FastAPILimiter: {e}. Rate limiting will be disabled.")
