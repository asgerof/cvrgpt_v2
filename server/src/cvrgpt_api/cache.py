import os
import json
from typing import Callable, Any, Dict, Tuple

# Simple in-memory cache fallback when Redis is not available
_memory_cache: Dict[str, Tuple[Any, float]] = {}


def cache_json(key: str, ttl: int, producer: Callable[[], Any]):
    """Cache JSON data with TTL. Falls back to memory cache if Redis unavailable."""
    try:
        import redis

        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=0,
        )
        val = r.get(key)
        if val and isinstance(val, (str, bytes)):
            return json.loads(val)
        data = producer()
        r.setex(
            key, ttl, json.dumps(data, default=lambda o: o.dict() if hasattr(o, "dict") else str(o))
        )
        return data
    except Exception:
        # Fallback to simple memory cache
        import time

        now = time.time()
        if key in _memory_cache:
            cached_data, expires_at = _memory_cache[key]
            if now < expires_at:
                return cached_data

        data = producer()
        _memory_cache[key] = (data, now + ttl)
        return data
