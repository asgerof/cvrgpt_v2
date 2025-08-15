import pytest
from fastapi import HTTPException
from cvrgpt_server.security import require_api_key


def test_require_api_key_with_valid_key():
    # Use the default key from settings
    from cvrgpt_server.config import settings

    default_key = settings.endpoint_api_key

    # Should not raise exception with the default key
    try:
        require_api_key(default_key)
    except HTTPException:
        pytest.fail(f"require_api_key raised HTTPException with valid key: {default_key}")


def test_require_api_key_with_invalid_key():
    with pytest.raises(HTTPException) as exc_info:
        require_api_key("wrong-key")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail["code"] == "UNAUTHORIZED"


def test_require_api_key_with_no_key():
    with pytest.raises(HTTPException) as exc_info:
        require_api_key(None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail["code"] == "UNAUTHORIZED"


def test_require_api_key_with_empty_key():
    with pytest.raises(HTTPException) as exc_info:
        require_api_key("")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail["code"] == "UNAUTHORIZED"
