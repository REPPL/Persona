# REST API Reference

Persona provides a REST API for programmatic access to persona generation.

## Quick Start

```bash
# Start the API server
persona serve --port 8000

# Generate personas via API
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"data": "./interviews.csv", "count": 3}'
```

---

## Starting the Server

```bash
persona serve [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--host`, `-h` | STRING | 127.0.0.1 | Server host |
| `--port`, `-p` | INT | 8000 | Server port |
| `--workers`, `-w` | INT | 1 | Number of worker processes |
| `--reload` | FLAG | false | Enable auto-reload (development) |
| `--auth-token` | STRING | - | API authentication token |
| `--log-level` | STRING | info | Logging level |

**Examples:**

```bash
# Development mode with auto-reload
persona serve --reload --log-level debug

# Production with authentication
persona serve --host 0.0.0.0 --port 8080 --workers 4 --auth-token "secret123"

# Using environment variable for auth
export PERSONA_API_AUTH_TOKEN="secret123"
persona serve --host 0.0.0.0
```

---

## Authentication

When `--auth-token` is provided or `PERSONA_API_AUTH_TOKEN` is set, all write endpoints require authentication.

**Header format:**
```
Authorization: Bearer <token>
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer secret123" \
  -H "Content-Type: application/json" \
  -d '{"data": "./data.csv"}'
```

**Endpoints requiring authentication:**
- `POST /api/v1/generate`
- `POST /api/v1/webhooks`
- `DELETE /api/v1/webhooks/{id}`

---

## Base URL

```
http://localhost:8000
```

**Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Endpoints

### Root

#### GET /

Returns API information.

**Response:**
```json
{
  "name": "Persona API",
  "version": "1.9.6",
  "docs": "/docs",
  "health": "/api/v1/health"
}
```

---

### Health

#### GET /api/v1/health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.9.6",
  "timestamp": "2025-12-19T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Server is healthy
- `503 Service Unavailable` - Server is unhealthy

---

### Generation

#### POST /api/v1/generate

Start an asynchronous persona generation job.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | string | Yes | Path or URL to data source |
| `count` | integer | No | Number of personas (1-20, default: 3) |
| `provider` | string | No | LLM provider (anthropic, openai, gemini) |
| `model` | string | No | Model identifier |
| `config` | object | No | Generation configuration |
| `webhook_url` | string | No | URL for completion webhook |

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer secret123" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "./interviews.csv",
    "count": 5,
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "config": {
      "complexity": "moderate",
      "detail_level": "standard"
    },
    "webhook_url": "https://example.com/webhook"
  }'
```

**Response:**
```json
{
  "job_id": "job-abc123",
  "status": "pending",
  "message": "Generation job created successfully",
  "status_url": "/api/v1/generate/job-abc123"
}
```

**Status Codes:**
- `200 OK` - Job created
- `400 Bad Request` - Invalid request
- `401 Unauthorised` - Authentication required
- `422 Unprocessable Entity` - Validation error

---

#### GET /api/v1/generate/{job_id}

Get generation job status and results.

**Path Parameters:**
- `job_id` - Job identifier

**Example Request:**
```bash
curl http://localhost:8000/api/v1/generate/job-abc123
```

**Response (pending):**
```json
{
  "job_id": "job-abc123",
  "status": "pending",
  "progress": 0,
  "created_at": "2025-12-19T10:30:00Z",
  "started_at": null,
  "completed_at": null,
  "error": null,
  "result": null
}
```

**Response (running):**
```json
{
  "job_id": "job-abc123",
  "status": "running",
  "progress": 45,
  "created_at": "2025-12-19T10:30:00Z",
  "started_at": "2025-12-19T10:30:01Z",
  "completed_at": null,
  "error": null,
  "result": null
}
```

**Response (completed):**
```json
{
  "job_id": "job-abc123",
  "status": "completed",
  "progress": 100,
  "created_at": "2025-12-19T10:30:00Z",
  "started_at": "2025-12-19T10:30:01Z",
  "completed_at": "2025-12-19T10:35:00Z",
  "error": null,
  "result": {
    "personas": [
      {
        "id": "persona-001",
        "name": "Sarah Chen",
        "title": "The Mobile Professional",
        "demographics": {...},
        "goals": [...],
        "pain_points": [...],
        "behaviours": [...],
        "quotes": [...]
      }
    ],
    "experiment_id": "exp-def456",
    "output_path": "./output/20251219_103000/"
  }
}
```

**Response (failed):**
```json
{
  "job_id": "job-abc123",
  "status": "failed",
  "progress": 0,
  "created_at": "2025-12-19T10:30:00Z",
  "started_at": "2025-12-19T10:30:01Z",
  "completed_at": "2025-12-19T10:30:05Z",
  "error": "API rate limit exceeded",
  "result": null
}
```

**Job Statuses:**
- `pending` - Job created, waiting to start
- `running` - Job in progress
- `completed` - Job finished successfully
- `failed` - Job failed with error

**Status Codes:**
- `200 OK` - Job found
- `404 Not Found` - Job not found

---

#### GET /api/v1/generate

List all generation jobs.

**Example Request:**
```bash
curl http://localhost:8000/api/v1/generate
```

**Response:**
```json
[
  {
    "job_id": "job-abc123",
    "status": "completed",
    "progress": 100,
    "created_at": "2025-12-19T10:30:00Z",
    ...
  },
  {
    "job_id": "job-def456",
    "status": "running",
    "progress": 60,
    "created_at": "2025-12-19T10:35:00Z",
    ...
  }
]
```

---

### Webhooks

Webhooks notify your application when generation jobs complete or fail.

#### POST /api/v1/webhooks

Register a webhook.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Webhook URL |
| `events` | array | No | Events to subscribe to |
| `secret` | string | No | Secret for HMAC signature |

**Available Events:**
- `generation.completed` - Job completed successfully
- `generation.failed` - Job failed

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Authorization: Bearer secret123" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "events": ["generation.completed", "generation.failed"],
    "secret": "webhook-secret-123"
  }'
```

**Response:**
```json
{
  "webhook_id": "webhook-abc123",
  "url": "https://example.com/webhook",
  "events": ["generation.completed", "generation.failed"],
  "created_at": "2025-12-19T10:30:00Z"
}
```

---

#### GET /api/v1/webhooks/{webhook_id}

Get webhook details.

**Example Request:**
```bash
curl http://localhost:8000/api/v1/webhooks/webhook-abc123
```

**Response:**
```json
{
  "webhook_id": "webhook-abc123",
  "url": "https://example.com/webhook",
  "events": ["generation.completed", "generation.failed"],
  "created_at": "2025-12-19T10:30:00Z"
}
```

---

#### DELETE /api/v1/webhooks/{webhook_id}

Delete a webhook.

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/webhooks/webhook-abc123 \
  -H "Authorization: Bearer secret123"
```

**Response:**
```json
{
  "success": true,
  "message": "Webhook webhook-abc123 deleted successfully"
}
```

---

#### GET /api/v1/webhooks

List all registered webhooks.

**Example Request:**
```bash
curl http://localhost:8000/api/v1/webhooks
```

**Response:**
```json
[
  {
    "webhook_id": "webhook-abc123",
    "url": "https://example.com/webhook",
    "events": ["generation.completed"],
    "created_at": "2025-12-19T10:30:00Z"
  }
]
```

---

### Webhook Payloads

When an event occurs, Persona sends a POST request to your webhook URL.

**Headers:**
```
Content-Type: application/json
X-Persona-Event: generation.completed
X-Persona-Signature: sha256=<hmac-signature>  # If secret provided
```

**Payload (generation.completed):**
```json
{
  "event": "generation.completed",
  "timestamp": "2025-12-19T10:35:00Z",
  "data": {
    "job_id": "job-abc123",
    "personas_count": 5,
    "experiment_id": "exp-def456",
    "output_path": "./output/20251219_103000/"
  }
}
```

**Payload (generation.failed):**
```json
{
  "event": "generation.failed",
  "timestamp": "2025-12-19T10:30:05Z",
  "data": {
    "job_id": "job-abc123",
    "error": "API rate limit exceeded"
  }
}
```

**Signature Verification (Python):**
```python
import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "success": false,
  "error": "error_code",
  "message": "Human-readable message",
  "details": {}
}
```

**Common Error Codes:**

| Code | Status | Description |
|------|--------|-------------|
| `invalid_input` | 400 | Invalid request parameters |
| `unauthorised` | 401 | Missing or invalid auth token |
| `not_found` | 404 | Resource not found |
| `validation_error` | 422 | Request validation failed |
| `rate_limited` | 429 | Too many requests |
| `internal_error` | 500 | Server error |

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default:** 100 requests per minute per IP
- **Generation:** 10 concurrent jobs per API key

**Rate limit headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1734608400
```

**Rate limited response:**
```json
{
  "success": false,
  "error": "rate_limited",
  "message": "Rate limit exceeded. Retry after 60 seconds.",
  "details": {
    "retry_after": 60
  }
}
```

---

## Client Libraries

### Python

```python
import httpx

class PersonaClient:
    def __init__(self, base_url: str = "http://localhost:8000", token: str = None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def generate(self, data: str, count: int = 3, **kwargs) -> dict:
        response = httpx.post(
            f"{self.base_url}/api/v1/generate",
            headers=self.headers,
            json={"data": data, "count": count, **kwargs}
        )
        response.raise_for_status()
        return response.json()

    def get_job(self, job_id: str) -> dict:
        response = httpx.get(
            f"{self.base_url}/api/v1/generate/{job_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def wait_for_job(self, job_id: str, timeout: int = 300) -> dict:
        import time
        start = time.time()
        while time.time() - start < timeout:
            job = self.get_job(job_id)
            if job["status"] in ("completed", "failed"):
                return job
            time.sleep(2)
        raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

# Usage
client = PersonaClient(token="secret123")
result = client.generate("./interviews.csv", count=5)
job = client.wait_for_job(result["job_id"])
print(job["result"]["personas"])
```

### cURL

```bash
# Generate personas
JOB=$(curl -s -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer secret123" \
  -H "Content-Type: application/json" \
  -d '{"data": "./data.csv", "count": 3}' | jq -r '.job_id')

# Poll for completion
while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/generate/$JOB | jq -r '.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  sleep 2
done

# Get results
curl -s http://localhost:8000/api/v1/generate/$JOB | jq '.result.personas'
```

---

## Related Documentation

- [Deployment Guide](deployment.md) - Server deployment options
- [Advanced Features](advanced-features.md) - CLI advanced commands
- [SDK Patterns](sdk-patterns.md) - Python SDK usage
- [CI/CD Integration](ci-cd-integration.md) - Pipeline integration
