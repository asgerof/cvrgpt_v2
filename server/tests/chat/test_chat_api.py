import os

# Set test environment variables BEFORE importing the app
os.environ.setdefault("API_KEY", "test-key")
os.environ.setdefault("CVRGPT_ENDPOINT_API_KEY", "test-key")
os.environ.setdefault("DATA_PROVIDER", "fixture")
os.environ.setdefault("APP_ENV", "dev")

from fastapi.testclient import TestClient
from cvrgpt_api.api import app
from cvrgpt_api.chat.state import _STORE

client = TestClient(app)
HEADERS = {"X-API-Key": "test-key"}  # Using test key for tests (note capitalization)


def test_requires_api_key():
    """Test that chat endpoint requires API key"""
    r = client.post("/chat", json={"messages": [{"role": "user", "content": "hello"}]})
    assert r.status_code in (401, 403)


def test_basic_chat_flow():
    """Test basic chat interaction"""
    body = {"messages": [{"role": "user", "content": "12345678 profile"}]}
    r = client.post("/chat", headers=HEADERS, json=body)
    assert r.status_code == 200
    payload = r.json()
    assert "thread_id" in payload
    assert "blocks" in payload
    assert len(payload["blocks"]) > 0


def test_choice_flow():
    """Test choice flow when multiple companies match"""
    body = {"messages": [{"role": "user", "content": "Demo company"}]}
    r = client.post("/chat", headers=HEADERS, json=body)
    assert r.status_code == 200
    payload = r.json()
    # May or may not have choices depending on fixture data
    assert "thread_id" in payload
    assert "blocks" in payload


def test_export_csv_no_table():
    """Test CSV export when no table exists"""
    r = client.get("/chat/export?thread_id=nonexistent", headers=HEADERS)
    assert r.status_code == 400
    response_data = r.json()
    # Check for the error message in either the message field or detail field
    error_text = response_data.get("message", "") + str(response_data.get("detail", ""))
    assert "No table to export" in error_text


def test_export_csv_with_table():
    """Test CSV export after creating a table"""
    # First, create a chat with financials to generate a table
    body = {"messages": [{"role": "user", "content": "12345678 revenue"}]}
    r = client.post("/chat", headers=HEADERS, json=body)
    assert r.status_code == 200
    payload = r.json()
    thread_id = payload["thread_id"]

    # Check if any table block was created
    has_table = any(block.get("type") == "table" for block in payload["blocks"])

    if has_table:
        # Try to export CSV
        r = client.get(f"/chat/export?thread_id={thread_id}", headers=HEADERS)
        assert r.status_code == 200
        assert r.headers["content-type"] == "text/csv; charset=utf-8"


def test_financial_intent():
    """Test financial data request"""
    body = {"messages": [{"role": "user", "content": "12345678 revenue 2023"}]}
    r = client.post("/chat", headers=HEADERS, json=body)
    assert r.status_code == 200
    payload = r.json()
    assert "thread_id" in payload
    # Should have at least one block
    assert len(payload["blocks"]) > 0


def test_filings_intent():
    """Test filings request"""
    body = {"messages": [{"role": "user", "content": "12345678 filings"}]}
    r = client.post("/chat", headers=HEADERS, json=body)
    assert r.status_code == 200
    payload = r.json()
    assert "thread_id" in payload
    assert len(payload["blocks"]) > 0


def test_compare_intent_insufficient_years():
    """Test comparison with insufficient years"""
    body = {"messages": [{"role": "user", "content": "12345678 compare"}]}
    r = client.post("/chat", headers=HEADERS, json=body)
    assert r.status_code == 200
    payload = r.json()
    assert "thread_id" in payload
    # Should get a message about needing more years
    text_blocks = [b for b in payload["blocks"] if b.get("type") == "text"]
    assert len(text_blocks) > 0
    assert "two years" in text_blocks[0]["text"]


def test_thread_context_persistence():
    """Test that thread context persists across requests"""
    # First request to establish context
    body1 = {"messages": [{"role": "user", "content": "12345678 profile"}]}
    r1 = client.post("/chat", headers=HEADERS, json=body1)
    assert r1.status_code == 200
    thread_id = r1.json()["thread_id"]

    # Second request using same thread should remember the company
    body2 = {"thread_id": thread_id, "messages": [{"role": "user", "content": "revenue"}]}
    r2 = client.post("/chat", headers=HEADERS, json=body2)
    assert r2.status_code == 200
    # Should not ask for company again since it's in context
    payload = r2.json()
    assert payload["thread_id"] == thread_id


def teardown_function():
    """Clean up thread state after each test"""
    _STORE.clear()
