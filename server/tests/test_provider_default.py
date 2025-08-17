import os
import pytest
from unittest.mock import patch
from cvrgpt_api.api import get_provider
from cvrgpt_api.providers.erst import ERSTProvider
from cvrgpt_api.providers.fixtures import FixtureProvider

def teardown_function():
    """Reset provider singleton after each test"""
    import cvrgpt_api.api
    import cvrgpt_core.providers.factory
    cvrgpt_api.api._provider_instance = None
    cvrgpt_core.providers.factory._provider_singleton = None

def test_default_provider_is_erst_in_dev():
    """Test that ERST is the default provider even in dev"""
    with patch.dict(os.environ, {"DATA_PROVIDER": "erst", "APP_ENV": "dev"}, clear=False):
        # Clear provider singleton
        import cvrgpt_api.api
        import cvrgpt_core.providers.factory
        cvrgpt_api.api._provider_instance = None
        cvrgpt_core.providers.factory._provider_singleton = None
        
        provider = get_provider()
        assert isinstance(provider, ERSTProvider)

def test_fixture_provider_when_explicitly_set():
    """Test that fixture provider is used when explicitly set"""
    with patch.dict(os.environ, {"DATA_PROVIDER": "fixture", "APP_ENV": "dev"}, clear=False):
        # Clear provider singleton
        import cvrgpt_api.api
        import cvrgpt_core.providers.factory
        cvrgpt_api.api._provider_instance = None
        cvrgpt_core.providers.factory._provider_singleton = None
        
        provider = get_provider()
        # Should be wrapped in CompositeProvider, so check the core
        assert hasattr(provider, 'core')
        assert isinstance(provider.core, FixtureProvider)

def test_erst_fails_in_prod_without_credentials():
    """Test that ERST provider fails in production without credentials"""
    with patch.dict(os.environ, {
        "DATA_PROVIDER": "erst", 
        "APP_ENV": "prod",
        "ERST_CLIENT_ID": "",
        "ERST_CLIENT_SECRET": "",
        "ERST_AUTH_URL": "",
        "ERST_TOKEN_AUDIENCE": "",
        "ERST_API_BASE_URL": ""
            }, clear=False):
        # Clear provider singleton
        import cvrgpt_api.api
        import cvrgpt_core.providers.factory
        cvrgpt_api.api._provider_instance = None
        cvrgpt_core.providers.factory._provider_singleton = None
        
        with pytest.raises(RuntimeError, match="ERST provider selected but required env vars are missing"):
            get_provider()

def test_erst_works_in_dev_without_credentials():
    """Test that ERST provider works in dev even without credentials"""
    with patch.dict(os.environ, {
        "DATA_PROVIDER": "erst", 
        "APP_ENV": "dev",
        "ERST_CLIENT_ID": "",
        "ERST_CLIENT_SECRET": "",
        "ERST_AUTH_URL": "",
        "ERST_TOKEN_AUDIENCE": "",
        "ERST_API_BASE_URL": ""
    }, clear=False):
        # Clear provider singleton
        import cvrgpt_api.api
        import cvrgpt_core.providers.factory
        cvrgpt_api.api._provider_instance = None
        cvrgpt_core.providers.factory._provider_singleton = None
        
        provider = get_provider()
        assert isinstance(provider, ERSTProvider)

def test_erst_ping_with_credentials():
    """Test ERST provider ping with credentials"""
    provider = ERSTProvider(
        client_id="test_id",
        client_secret="test_secret", 
        auth_url="https://test.auth.url",
        token_audience="test_audience",
        api_base="https://test.api.url"
    )
    
    # Should return True when credentials are provided
    assert provider.ping() is True

def test_erst_ping_without_credentials():
    """Test ERST provider ping without credentials"""
    provider = ERSTProvider(
        client_id="",
        client_secret="",
        auth_url="",
        token_audience="",
        api_base=""
    )
    
    # Should return False when credentials are missing
    assert provider.ping() is False

@pytest.mark.asyncio
async def test_erst_provider_methods():
    """Test that ERST provider methods return expected structure"""
    provider = ERSTProvider(
        client_id="test_id",
        client_secret="test_secret",
        auth_url="https://test.auth.url", 
        token_audience="test_audience",
        api_base="https://test.api.url"
    )
    
    # Test search_companies
    result = await provider.search_companies("test")
    assert "items" in result
    assert "total" in result
    assert "citations" in result
    
    # Test get_company
    result = await provider.get_company("12345678")
    assert "company" in result
    assert "citations" in result
    
    # Test list_filings
    result = await provider.list_filings("12345678")
    assert "filings" in result
    assert "citations" in result
    
    # Test get_latest_accounts
    result = await provider.get_latest_accounts("12345678")
    assert "accounts" in result
    assert "citations" in result
