from fastapi.testclient import TestClient
from cvrgpt_api.api import app

def test_cache_basic(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    c = TestClient(app)
    r1 = c.get("/v1/search?q=test&limit=2&offset=0", headers={"X-API-Key":"secret"}).json()
    r2 = c.get("/v1/search?q=test&limit=2&offset=0", headers={"X-API-Key":"secret"}).json()
    assert r1 == r2
