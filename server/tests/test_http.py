import pytest
from unittest.mock import AsyncMock, patch, Mock
import httpx
from cvrgpt_api.http import get_json, UpstreamError, UpstreamNotFound, client


@pytest.mark.asyncio
async def test_get_json_success():
    """Test that get_json returns JSON data on success"""
    test_data = {"test": "data"}

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = test_data

    with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await get_json("https://example.com/api")
        assert result == test_data
        mock_get.assert_called_once_with("https://example.com/api", params=None, headers=None)


@pytest.mark.asyncio
async def test_get_json_with_params_and_headers():
    """Test that get_json passes params and headers correctly"""
    test_data = {"test": "data"}
    test_params = {"q": "test"}
    test_headers = {"Authorization": "Bearer token"}

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = test_data

    with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await get_json("https://example.com/api", params=test_params, headers=test_headers)
        assert result == test_data
        mock_get.assert_called_once_with(
            "https://example.com/api", params=test_params, headers=test_headers
        )


@pytest.mark.asyncio
async def test_get_json_404_raises_upstream_not_found():
    """Test that 404 status raises UpstreamNotFound"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not found"

    with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        with pytest.raises(UpstreamNotFound) as exc_info:
            await get_json("https://example.com/api")
        assert "Not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_json_client_error_raises_upstream_error():
    """Test that client HTTP errors (4xx except 404) raise UpstreamError"""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad request", request=Mock(), response=mock_response
    )

    with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        with pytest.raises(UpstreamError):
            await get_json("https://example.com/api")


@pytest.mark.asyncio
async def test_get_json_retries_on_server_error():
    """Test that get_json retries on server errors (5xx)"""
    test_data = {"test": "data"}

    # First call fails with 500, second succeeds
    mock_response_fail = Mock()
    mock_response_fail.status_code = 500
    mock_response_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server error", request=Mock(), response=mock_response_fail
    )

    mock_response_success = Mock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = test_data

    with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
        # Configure side_effect to fail first, then succeed
        mock_get.side_effect = [mock_response_fail, mock_response_success]

        result = await get_json("https://example.com/api")
        assert result == test_data
        # Should have been called twice due to retry
        assert mock_get.call_count == 2


@pytest.mark.asyncio
async def test_get_json_no_retry_on_client_error():
    """Test that get_json does not retry on client errors (4xx except 404)"""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad request", request=Mock(), response=mock_response
    )

    with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        with pytest.raises(UpstreamError):
            await get_json("https://example.com/api")
        # Should only be called once (no retry)
        assert mock_get.call_count == 1


@pytest.mark.asyncio
async def test_get_json_server_error_exhausts_retries():
    """Test that server errors eventually raise RetryError after exhausting retries"""
    from tenacity import RetryError

    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server error", request=Mock(), response=mock_response
    )

    with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        with pytest.raises(RetryError):
            await get_json("https://example.com/api")
        # Should be called multiple times due to retries (default is 2 + 1 = 3)
        assert mock_get.call_count == 3


def test_http_client_configuration():
    """Test that HTTP client is configured with correct timeout"""
    from cvrgpt_api.config import settings

    assert client.timeout.read == settings.request_timeout_s
    assert client.timeout.connect == settings.request_timeout_s


def test_upstream_exceptions_inheritance():
    """Test that exception classes have correct inheritance"""
    assert issubclass(UpstreamNotFound, UpstreamError)
    assert issubclass(UpstreamError, Exception)
