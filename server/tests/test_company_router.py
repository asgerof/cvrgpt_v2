from fastapi.testclient import TestClient
from cvrgpt_server.api import app

API_KEY = "dev-local-key"


def test_company_validation():
    client = TestClient(app)
    r = client.get("/v1/company/12")  # Invalid short CVR
    assert r.status_code == 404
    data = r.json()
    assert data["code"] == "NOT_FOUND"


def test_search_ok():
    client = TestClient(app)
    r = client.get("/v1/search?q=de", headers={"x-api-key": API_KEY})
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
