from fastapi.testclient import TestClient
from cvrgpt_api.api import app

client = TestClient(app)

def test_list_events_last_90_days():
    r = client.get("/v1/events?event_type=bankruptcy&nace=62&last_days=90&limit=10")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body and isinstance(body["items"], list)
    assert body["count"] <= 10

def test_events_bad_params():
    r = client.get("/v1/events?last_days=90&from_date=2025-01-01")
    assert r.status_code == 400
