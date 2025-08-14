from fastapi.testclient import TestClient
from cvrgpt_api.api import app

client = TestClient(app)

def test_search_companies():
    res = client.get("/companies/search", params={"q":"De"})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert "cvr" in data[0]

def test_get_company():
    res = client.get("/companies/12345678")
    assert res.status_code == 200
    assert res.json()["cvr"] == "12345678"

def test_latest_accounts():
    res = client.get("/companies/12345678/accounts/latest")
    assert res.status_code == 200
    data = res.json()
    assert "year" in data
    assert "revenue" in data

def test_compare_accounts():
    res = client.get("/companies/12345678/accounts/compare")
    assert res.status_code == 200
    data = res.json()
    assert "a" in data
    assert "b" in data
    assert "deltas" in data
