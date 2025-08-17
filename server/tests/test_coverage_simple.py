"""Simple tests to improve coverage without hitting rate limiter dependencies."""

from cvrgpt_api.cache import Cache, _key
from cvrgpt_api.security import require_api_key
from cvrgpt_api.config import settings
from cvrgpt_api.errors import ErrorCode, ErrorPayload
import pytest
from fastapi import HTTPException


def test_cache_key_generation():
    """Test cache key generation."""
    key = _key("test", "a", "b", "c")
    assert key == "test:a:b:c"


def test_cache_memory_fallback():
    """Test in-memory cache when Redis is not available."""
    cache = Cache()
    # Ensure we're using memory cache
    cache._r = None
    
    # Test set and get
    cache.set("test_key", {"data": "value"}, 60)
    result = cache.get("test_key")
    assert result == {"data": "value"}
    
    # Test non-existent key
    result = cache.get("nonexistent")
    assert result is None


def test_security_no_env_var(monkeypatch):
    """Test security allows all when no API_KEY env var is set."""
    monkeypatch.delenv("API_KEY", raising=False)
    # Should not raise exception
    require_api_key(None)


def test_security_with_env_var_missing_key(monkeypatch):
    """Test security rejects when API_KEY is set but header is missing."""
    monkeypatch.setenv("API_KEY", "secret")
    with pytest.raises(HTTPException) as exc_info:
        require_api_key(None)
    assert exc_info.value.status_code == 401


def test_security_with_env_var_wrong_key(monkeypatch):
    """Test security rejects wrong API key."""
    monkeypatch.setenv("API_KEY", "secret")
    with pytest.raises(HTTPException) as exc_info:
        require_api_key("wrong")
    assert exc_info.value.status_code == 401


def test_security_with_env_var_correct_key(monkeypatch):
    """Test security accepts correct API key."""
    monkeypatch.setenv("API_KEY", "secret")
    # Should not raise exception
    require_api_key("secret")


def test_error_payload():
    """Test error payload model."""
    error = ErrorPayload(code=ErrorCode.NOT_FOUND, message="Test error")
    assert error.code == ErrorCode.NOT_FOUND
    assert error.message == "Test error"


def test_settings_loaded():
    """Test that settings are loaded correctly."""
    # Just verify settings object exists and has expected attributes
    assert hasattr(settings, 'provider')
    assert hasattr(settings, 'mcp_mount_path')
