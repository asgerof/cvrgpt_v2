import os

# Configure environment before importing the app
os.environ["API_KEY"] = "test-secret"
os.environ["DATA_PROVIDER"] = "fixture"
os.environ["APP_ENV"] = "dev"

from fastapi.testclient import TestClient
from cvrgpt_api.api import app

client = TestClient(app)


def test_healthz_no_auth():
    r = client.get("/healthz")
    assert r.status_code == 200


def test_v1_requires_api_key_missing():
    r = client.get("/v1/search?q=test")
    assert r.status_code == 401


def test_v1_allows_with_correct_key():
    r = client.get("/v1/search?q=test", headers={"X-API-Key": "test-secret"})
    assert r.status_code in (200, 204, 404)  # any valid outcome past auth
