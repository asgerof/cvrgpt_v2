import os

# Configure environment before importing the app
os.environ.setdefault("API_KEY", "test-key")
os.environ.setdefault("DATA_PROVIDER", "fixture")
os.environ.setdefault("APP_ENV", "dev")

from fastapi.testclient import TestClient
from cvrgpt_api.api import app

def test_chat_bankruptcy_intent():
    c = TestClient(app)
    payload = {
        "thread_id": "t1",
        "messages": [{"role":"user","content":"Give me recent bankruptcies in the IT sector (last 3 months)."}]
    }
    r = c.post("/v1/chat", headers={"X-API-Key": "test-key"}, json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["blocks"][1]["type"] == "table"
