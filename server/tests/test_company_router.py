from fastapi.testclient import TestClient
from app.main import app

API_KEY = "dev-local-key"


def test_company_validation():
    client = TestClient(app)
    r = client.get("/v1/company/12", headers={"x-api-key": API_KEY})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR" or r.json().get("detail")


def test_search_ok():
    client = TestClient(app)
    r = client.get("/v1/search?q=de", headers={"x-api-key": API_KEY})
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
