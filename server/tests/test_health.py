from fastapi.testclient import TestClient
from cvrgpt_api.api import app


def test_health():
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["status"] == "ok"
