import pytest
import json
from unittest.mock import Mock, patch
from cvrgpt_server.logging import access_log_mw, setup_logging


@pytest.mark.asyncio
async def test_access_log_mw_logs_request_details():
    """Test that access logging middleware logs request details in JSON format"""
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.url.path = "/v1/search"
    mock_request.state.request_id = "test-request-id-123"

    mock_response = Mock()
    mock_response.status_code = 200

    async def mock_call_next(request):
        return mock_response

    with patch("cvrgpt_server.logging.logger.info") as mock_logger:
        result = await access_log_mw(mock_request, mock_call_next)

        # Check that logger.info was called
        mock_logger.assert_called_once()

        # Parse the logged JSON
        logged_data = json.loads(mock_logger.call_args[0][0])

        # Verify the log structure
        assert logged_data["event"] == "http_access"
        assert logged_data["method"] == "GET"
        assert logged_data["path"] == "/v1/search"
        assert logged_data["status"] == 200
        assert logged_data["request_id"] == "test-request-id-123"
        assert "took_ms" in logged_data
        assert isinstance(logged_data["took_ms"], int)

        # Check that the response was returned
        assert result == mock_response


@pytest.mark.asyncio
async def test_access_log_mw_handles_missing_request_id():
    """Test that access logging works when request_id is not set"""
    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.url.path = "/v1/company/123"
    # No request_id set on state
    mock_request.state = Mock()
    del mock_request.state.request_id  # Simulate missing attribute

    mock_response = Mock()
    mock_response.status_code = 404

    async def mock_call_next(request):
        return mock_response

    with patch("cvrgpt_server.logging.logger.info") as mock_logger:
        with patch("cvrgpt_server.logging.getattr", return_value=None):
            await access_log_mw(mock_request, mock_call_next)

        # Check that logger.info was called
        mock_logger.assert_called_once()

        # Parse the logged JSON
        logged_data = json.loads(mock_logger.call_args[0][0])

        # Verify the log structure
        assert logged_data["event"] == "http_access"
        assert logged_data["method"] == "POST"
        assert logged_data["path"] == "/v1/company/123"
        assert logged_data["status"] == 404
        assert logged_data["request_id"] is None
        assert "took_ms" in logged_data


def test_setup_logging_returns_logger():
    """Test that setup_logging returns a structlog logger"""
    logger = setup_logging()
    assert logger is not None
    # Should be a structlog BoundLogger
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")


def test_logging_module_imports():
    """Test that logging components can be imported"""
    from cvrgpt_server.logging import access_log_mw, setup_logging, logger

    assert access_log_mw is not None
    assert setup_logging is not None
    assert logger is not None
