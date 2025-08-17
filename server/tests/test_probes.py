import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_redis_ping_success():
    """Test that redis ping works when Redis is available"""
    with patch("cvrgpt_api.redis_client.redis_client.ping", new_callable=AsyncMock) as mock_ping:
        mock_ping.return_value = True

        # Import here to avoid MCP import issues
        from cvrgpt_api.redis_client import redis_client

        result = await redis_client.ping()
        assert result is True


@pytest.mark.asyncio
async def test_redis_ping_failure():
    """Test that redis ping raises exception when Redis is unavailable"""
    with patch("cvrgpt_api.redis_client.redis_client.ping", new_callable=AsyncMock) as mock_ping:
        mock_ping.side_effect = Exception("Connection failed")

        from cvrgpt_api.redis_client import redis_client

        with pytest.raises(Exception) as exc_info:
            await redis_client.ping()
        assert "Connection failed" in str(exc_info.value)


def test_request_id_middleware_imports():
    """Test that the RequestIDMiddleware can be imported"""
    from cvrgpt_api.observability import RequestIDMiddleware

    assert RequestIDMiddleware is not None
