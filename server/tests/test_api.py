from fastapi.testclient import TestClient
from cvrgpt_api.api import app

client = TestClient(app)


def test_search_companies():
    res = client.get("/v1/search", params={"q": "De"})
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    if data["items"]:
        assert "cvr" in data["items"][0]


def test_get_company():
    res = client.get("/v1/company/12345678")
    assert res.status_code == 200
    data = res.json()
    assert "company" in data
    assert data["company"]["cvr"] == "12345678"


def test_latest_accounts():
    res = client.get("/v1/accounts/latest/12345678")
    assert res.status_code == 200
    data = res.json()
    assert "accounts" in data


def test_compare_accounts():
    res = client.get("/v1/compare/12345678")
    assert res.status_code == 200
    data = res.json()
    assert "narrative" in data
