from fastapi.testclient import TestClient
from cvrgpt_api.api import app

client = TestClient(app)

def test_run_events_search_tool():
    payload = {
        "name": "events_search",
        "args": {
            "event_type": "bankruptcy",
            "nace_prefixes": ["62"],
            "date_from": "2025-05-23T00:00:00+00:00",
            "date_to": "2025-08-23T00:00:00+00:00",
            "limit": 5
        }
    }
    r = client.post("/v1/tools/run", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "result" in body
    assert body["result"]["type"] == "table"
