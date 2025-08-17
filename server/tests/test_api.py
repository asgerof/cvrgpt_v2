from fastapi.testclient import TestClient
from cvrgpt_api.api import app

client = TestClient(app)

# Set up API key for tests
API_KEY = "test-secret"
HEADERS = {"X-API-Key": API_KEY}


def test_search_companies(monkeypatch):
    monkeypatch.setenv("API_KEY", API_KEY)
    res = client.get("/v1/search", params={"q": "De"}, headers=HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    if data["items"]:
        assert "cvr" in data["items"][0]


def test_get_company(monkeypatch):
    monkeypatch.setenv("API_KEY", API_KEY)
    res = client.get("/v1/company/12345678", headers=HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert "company" in data
    assert data["company"]["cvr"] == "12345678"


def test_latest_accounts(monkeypatch):
    monkeypatch.setenv("API_KEY", API_KEY)
    res = client.get("/v1/accounts/latest/12345678", headers=HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert "current" in data or "accounts" in data  # Handle both response formats


def test_compare_accounts(monkeypatch):
    monkeypatch.setenv("API_KEY", API_KEY)
    res = client.get("/v1/compare/12345678", headers=HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert "narrative" in data
