import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter
import pybreaker
import os
from contextlib import asynccontextmanager

TIMEOUT = httpx.Timeout(10.0, connect=5.0)
breakers: dict[str, pybreaker.CircuitBreaker] = {}
CONTACT = os.getenv("APP_CONTACT_EMAIL", "unknown@example.com")


def get_breaker(name: str) -> pybreaker.CircuitBreaker:
    if name not in breakers:
        breakers[name] = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)
    return breakers[name]


@asynccontextmanager
async def client():
    async with httpx.AsyncClient(
        timeout=TIMEOUT, headers={"User-Agent": f"cvrgpt_v2/1.0 (+{CONTACT})"}
    ) as c:
        yield c


def retryer():
    return retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=0.2, max=2.0))
