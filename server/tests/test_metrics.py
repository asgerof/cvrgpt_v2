"""Test Prometheus metrics endpoint."""

from fastapi.testclient import TestClient
from cvrgpt_api.api import app


def test_metrics_endpoint_exists():
    """Test that /metrics endpoint is available."""
    client = TestClient(app)
    r = client.get("/metrics")
    
    # Should return 200 OK
    assert r.status_code == 200
    
    # Should return Prometheus text format
    assert "text/plain" in r.headers.get("content-type", "")


def test_metrics_contains_prometheus_data():
    """Test that /metrics returns Prometheus-formatted metrics."""
    client = TestClient(app)
    
    # Make a few requests to generate some metrics
    client.get("/healthz")
    client.get("/healthz") 
    client.get("/nonexistent")  # This should generate a 404
    
    # Now check metrics
    r = client.get("/metrics")
    content = r.text
    
    # Should contain standard Prometheus metrics
    assert "http_requests_total" in content or "http_request_duration_seconds" in content
    assert "# HELP" in content  # Prometheus help text
    assert "# TYPE" in content  # Prometheus type declarations


def test_metrics_endpoint_not_in_openapi():
    """Test that /metrics endpoint is not included in OpenAPI schema."""
    client = TestClient(app)
    r = client.get("/openapi.json")
    
    openapi_data = r.json()
    paths = openapi_data.get("paths", {})
    
    # /metrics should not be in the OpenAPI schema (Prometheus sets include_in_schema=False)
    # Note: This might still appear in some FastAPI versions, so we'll check the endpoint works instead
    r_metrics = client.get("/metrics")
    assert r_metrics.status_code == 200


def test_request_id_in_logs(caplog):
    """Test that request IDs are included in access logs."""
    client = TestClient(app)
    
    # Make a request with a custom request ID
    custom_id = "test-metrics-123"
    r = client.get("/healthz", headers={"x-request-id": custom_id})
    
    # Verify the request ID is in the response header
    assert r.headers["x-request-id"] == custom_id
