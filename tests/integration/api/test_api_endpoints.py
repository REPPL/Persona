"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from persona.api.app import create_app
from persona.api.config import APIConfig


@pytest.fixture
def app():
    """Create test FastAPI application."""
    config = APIConfig(
        auth_enabled=False,
        rate_limit_enabled=False,
    )
    return create_app(config)


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.get("/api/v1/health", headers={"Origin": "https://example.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_rate_limit_disabled(app):
    """Test that rate limiting can be disabled."""
    config = app.state.config
    assert config.rate_limit_enabled is False


def test_create_generation_job(client):
    """Test creating a generation job."""
    request_data = {
        "data": "./test-data.csv",
        "count": 3,
        "provider": "anthropic",
    }

    response = client.post("/api/v1/generate", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    assert "status_url" in data


def test_get_job_status(client):
    """Test getting job status."""
    # First create a job
    request_data = {
        "data": "./test-data.csv",
        "count": 3,
    }
    create_response = client.post("/api/v1/generate", json=request_data)
    job_id = create_response.json()["job_id"]

    # Get job status
    response = client.get(f"/api/v1/generate/{job_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data
    assert "progress" in data
    assert "created_at" in data


def test_get_nonexistent_job(client):
    """Test getting status of nonexistent job."""
    response = client.get("/api/v1/generate/nonexistent")
    assert response.status_code == 404


def test_list_jobs(client):
    """Test listing all jobs."""
    # Create a couple of jobs
    for i in range(2):
        client.post(
            "/api/v1/generate",
            json={"data": f"./test-{i}.csv", "count": 3},
        )

    # List all jobs
    response = client.get("/api/v1/generate")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_register_webhook(client):
    """Test registering a webhook."""
    request_data = {
        "url": "https://example.com/webhook",
        "events": ["generation.completed", "generation.failed"],
        "secret": "test-secret",
    }

    response = client.post("/api/v1/webhooks", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert "webhook_id" in data
    assert data["url"] == request_data["url"]
    assert data["events"] == request_data["events"]
    assert "created_at" in data


def test_get_webhook(client):
    """Test getting webhook details."""
    # First register a webhook
    request_data = {
        "url": "https://example.com/webhook",
        "events": ["generation.completed"],
    }
    create_response = client.post("/api/v1/webhooks", json=request_data)
    webhook_id = create_response.json()["webhook_id"]

    # Get webhook details
    response = client.get(f"/api/v1/webhooks/{webhook_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["webhook_id"] == webhook_id
    assert data["url"] == request_data["url"]


def test_delete_webhook(client):
    """Test deleting a webhook."""
    # First register a webhook
    request_data = {
        "url": "https://example.com/webhook",
        "events": ["generation.completed"],
    }
    create_response = client.post("/api/v1/webhooks", json=request_data)
    webhook_id = create_response.json()["webhook_id"]

    # Delete webhook
    response = client.delete(f"/api/v1/webhooks/{webhook_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True

    # Webhook should no longer exist
    get_response = client.get(f"/api/v1/webhooks/{webhook_id}")
    assert get_response.status_code == 404


def test_list_webhooks(client):
    """Test listing all webhooks."""
    # Register a couple of webhooks
    for i in range(2):
        client.post(
            "/api/v1/webhooks",
            json={
                "url": f"https://example.com/webhook-{i}",
                "events": ["generation.completed"],
            },
        )

    # List all webhooks
    response = client.get("/api/v1/webhooks")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_openapi_docs(client):
    """Test OpenAPI documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json(client):
    """Test OpenAPI JSON schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
