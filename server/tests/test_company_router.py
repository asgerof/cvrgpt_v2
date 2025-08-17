from fastapi.testclient import TestClient
from cvrgpt_api.api import app

API_KEY = "dev-local-key"
HEADERS = {"X-API-Key": API_KEY}

client = TestClient(app)


def test_company_validation(monkeypatch):
    monkeypatch.setenv("API_KEY", API_KEY)
    r = client.get("/v1/company/12", headers=HEADERS)  # Invalid short CVR
    assert r.status_code == 404
    data = r.json()
    assert data["code"] == "NOT_FOUND"


def test_search_ok(monkeypatch):
    monkeypatch.setenv("API_KEY", API_KEY)
    r = client.get("/v1/search?q=de", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
