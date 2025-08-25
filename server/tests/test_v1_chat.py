import os
from fastapi.testclient import TestClient


# Configure environment before importing the app
os.environ["API_KEY"] = "test-secret"
os.environ.setdefault("DATA_PROVIDER", "fixture")
os.environ.setdefault("APP_ENV", "dev")
os.environ.setdefault("CHAT_NLU", "llm")  # enforce LLM

from cvrgpt_api.api import app  # noqa: E402


client = TestClient(app)
HDR = {"X-API-Key": "test-secret"}


def test_v1_chat_requires_api_key():
    r = client.post(
        "/v1/chat", json={"thread_id": "t1", "messages": [{"role": "user", "content": "hello"}]}
    )
    assert r.status_code in (401, 403)


def test_v1_chat_bankruptcies_requires_llm():
    body = {
        "thread_id": "t1",
        "messages": [
            {"role": "user", "content": "recent bankruptcies in the IT sector (last 3 months)"}
        ],
    }
    r = client.post("/v1/chat", headers=HDR, json=body)
    # If OpenAI API key is available, expect success; otherwise expect 503
    if os.getenv("OPENAI_API_KEY"):
        assert r.status_code == 200
        j = r.json()
        assert "blocks" in j
    else:
        assert r.status_code == 503
        j = r.json()
        assert "LLM NLU unavailable" in (j.get("detail") or "")


def test_v1_chat_annual_result_requires_llm():
    body = {
        "thread_id": "t2",
        "messages": [
            {"role": "user", "content": "What was the annual result of Demo IT ApS in 2022?"}
        ],
    }
    r = client.post("/v1/chat", headers=HDR, json=body)
    # If OpenAI API key is available, expect success; otherwise expect 503
    if os.getenv("OPENAI_API_KEY"):
        assert r.status_code == 200
        j = r.json()
        assert "blocks" in j
    else:
        assert r.status_code == 503
        j = r.json()
        assert "LLM NLU unavailable" in (j.get("detail") or "")
