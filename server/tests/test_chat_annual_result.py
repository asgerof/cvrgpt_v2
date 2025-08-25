import os

# Configure environment before importing the app
os.environ.setdefault("API_KEY", "test-key")
os.environ.setdefault("DATA_PROVIDER", "fixture")
os.environ.setdefault("APP_ENV", "dev")

from fastapi.testclient import TestClient
from cvrgpt_api.api import app

def test_chat_annual_result_fixture():
    c = TestClient(app)
    r = c.post("/v1/chat", headers={"X-API-Key": "test-key"}, json={
        "thread_id":"t2",
        "messages":[{"role":"user","content":"What was the annual result of Demo IT ApS in 2022?"}]
    })
    assert r.status_code == 200
    data = r.json()
    assert any(b.get("type")=="table" for b in data["blocks"])
