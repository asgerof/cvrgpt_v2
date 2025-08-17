from fastapi.testclient import TestClient
from cvrgpt_api.api import app

client = TestClient(app)
HDR = {"X-API-Key": "secret"}

def test_pagination(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    a = client.get("/v1/search?q=a&limit=5&offset=0", headers=HDR).json()
    assert a["limit"] == 5 and a["offset"] == 0
    if a["next_offset"] is not None:
        b = client.get(f"/v1/search?q=a&limit=5&offset={a['next_offset']}", headers=HDR).json()
        assert b["offset"] == a["next_offset"]

def test_limit_cap(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    r = client.get("/v1/search?q=a&limit=999", headers=HDR)
    assert r.status_code == 422
