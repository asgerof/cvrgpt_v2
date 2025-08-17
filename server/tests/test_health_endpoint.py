import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from cvrgpt_api.api import app

client = TestClient(app)

def test_health_provider_endpoint_with_fixture():
    """Test health endpoint returns fixture provider status"""
    with patch.dict(os.environ, {"DATA_PROVIDER": "fixture", "APP_ENV": "dev"}, clear=False):
        # Clear provider singleton
        import cvrgpt_api.api
        cvrgpt_api.api._provider_instance = None
        
        response = client.get("/health/provider")
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "ok" in data
        assert data["provider"] == "fixture"
        assert data["ok"] is True

def test_health_provider_endpoint_with_erst():
    """Test health endpoint returns ERST provider status"""
    with patch.dict(os.environ, {
        "DATA_PROVIDER": "erst", 
        "APP_ENV": "dev",
        "ERST_CLIENT_ID": "test_id",
        "ERST_CLIENT_SECRET": "test_secret",
        "ERST_AUTH_URL": "https://test.auth.url",
        "ERST_TOKEN_AUDIENCE": "test_audience",
        "ERST_API_BASE_URL": "https://test.api.url"
    }, clear=False):
        # Clear provider singleton
        import cvrgpt_api.api
        cvrgpt_api.api._provider_instance = None
        
        response = client.get("/health/provider")
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "ok" in data
        assert data["provider"] == "erst"
        assert data["ok"] is True

def test_health_provider_endpoint_with_erst_no_credentials():
    """Test health endpoint returns ERST provider failure when no credentials"""
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
        cvrgpt_api.api._provider_instance = None
        
        response = client.get("/health/provider")
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "ok" in data
        assert data["provider"] == "erst"
        assert data["ok"] is False
