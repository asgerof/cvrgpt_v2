import pytest
from unittest.mock import AsyncMock, patch
from fastapi_limiter import FastAPILimiter
from cvrgpt_server.rate_limit import init_rate_limiter


@pytest.mark.asyncio
async def test_init_rate_limiter():
    """Test that rate limiter initialization works"""
    with patch.object(FastAPILimiter, "init", new_callable=AsyncMock) as mock_init:
        await init_rate_limiter()
        mock_init.assert_called_once()


def test_rate_limit_module_imports():
    """Test that rate limiting components can be imported"""
    from fastapi_limiter.depends import RateLimiter
    from cvrgpt_server.rate_limit import init_rate_limiter

    assert RateLimiter is not None
    assert init_rate_limiter is not None


def test_rate_limiter_dependency_creation():
    """Test that RateLimiter dependency can be created with different parameters"""
    from fastapi_limiter.depends import RateLimiter

    # Test creating different rate limiters
    search_limiter = RateLimiter(times=30, seconds=60)
    company_limiter = RateLimiter(times=60, seconds=60)

    assert search_limiter is not None
    assert company_limiter is not None
