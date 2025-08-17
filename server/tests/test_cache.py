import pytest
from unittest.mock import AsyncMock, patch, Mock
from fastapi import Request
from cvrgpt_api.cache import cache_get, cache_set, with_etag, _key, cache


@pytest.mark.asyncio
async def test_cache_get_returns_none_when_empty():
    """Test that cache_get returns None when key doesn't exist"""
    with patch.object(cache, 'get', return_value=None) as mock_get:
        result = await cache_get("test_key")
        assert result is None
        mock_get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_cache_get_returns_parsed_data():
    """Test that cache_get returns parsed JSON data"""
    test_data = {"name": "Test Company", "cvr": "12345678"}
    with patch.object(cache, 'get', return_value=test_data) as mock_get:
        result = await cache_get("test_key")
        assert result == test_data
        mock_get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_cache_set_stores_data():
    """Test that cache_set stores data with TTL"""
    test_data = {"name": "Test Company", "cvr": "12345678"}
    with patch.object(cache, 'set') as mock_set:
        await cache_set("test_key", test_data, 3600)
        mock_set.assert_called_once_with("test_key", test_data, 3600)


def test_key_function():
    """Test the _key helper function"""
    result = _key("prefix", "part1", "part2")
    assert result == "prefix:part1:part2"


def test_with_etag_returns_304_when_etag_matches():
    """Test that with_etag returns 304 when If-None-Match header matches ETag"""
    # Create a mock request with If-None-Match header
    mock_request = Mock(spec=Request)
    test_data = {"test": "data"}

    # Calculate what the ETag should be
    import hashlib
    import json

    expected_etag = hashlib.md5(json.dumps(test_data, default=str).encode(), usedforsecurity=False).hexdigest()  # nosec B324

    mock_request.headers = {"if-none-match": expected_etag}

    response = with_etag(mock_request, test_data, 3600)
    assert response.status_code == 304


def test_with_etag_returns_data_with_headers():
    """Test that with_etag returns data with ETag and Cache-Control headers"""
    mock_request = Mock(spec=Request)
    mock_request.headers = {}  # No If-None-Match header

    test_data = {"test": "data"}
    response = with_etag(mock_request, test_data, 3600)

    assert response.status_code == 200
    assert "ETag" in response.headers
    assert response.headers["Cache-Control"] == "public, max-age=3600"
    assert response.media_type == "application/json"
