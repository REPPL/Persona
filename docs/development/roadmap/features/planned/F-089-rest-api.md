# F-089: REST API

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-008 |
| **Milestone** | v0.9.0 |
| **Priority** | P2 |
| **Category** | API |

## Problem Statement

Some users need HTTP-based access for web integrations, microservices architectures, or language-agnostic access. A REST API complements the Python SDK.

## Design Approach

- FastAPI-based HTTP server
- OpenAPI documentation auto-generated
- Same functionality as SDK
- Token-based authentication
- Optional installation (`pip install persona[api]`)

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/experiments` | List experiments |
| POST | `/experiments` | Create experiment |
| GET | `/experiments/{id}` | Get experiment |
| DELETE | `/experiments/{id}` | Delete experiment |
| POST | `/experiments/{id}/generate` | Start generation |
| GET | `/experiments/{id}/runs` | List runs |
| GET | `/experiments/{id}/runs/{run_id}` | Get run details |
| GET | `/personas/{id}` | Get persona |

### Request/Response Examples

**Create Experiment:**
```bash
POST /experiments
Content-Type: application/json

{
  "name": "my-experiment",
  "data_sources": ["./interviews.csv"],
  "config": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-5-20250929",
    "persona_count": 3
  }
}
```

**Response:**
```json
{
  "id": "exp-abc123",
  "name": "my-experiment",
  "status": "created",
  "created_at": "2025-12-14T10:30:00Z"
}
```

### Server Launch

```bash
# Start API server
persona serve --port 8000

# With authentication
persona serve --port 8000 --auth-token secret123

# Production (with uvicorn)
uvicorn persona.api:app --host 0.0.0.0 --port 8000
```

## Implementation Tasks

- [ ] Create FastAPI application
- [ ] Implement experiment endpoints
- [ ] Implement generation endpoints
- [ ] Implement persona endpoints
- [ ] Add token authentication
- [ ] Generate OpenAPI spec
- [ ] Create `persona serve` command
- [ ] Add to optional dependencies
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All endpoints functional
- [ ] OpenAPI docs generated
- [ ] Authentication works
- [ ] Optional dependency works
- [ ] Test coverage ≥ 80%

## Dependencies

- F-105: Python SDK
- F-088: Async support

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [ADR-0021: Programmatic API](../../../decisions/adrs/ADR-0021-programmatic-api.md)
- [F-105: Python SDK](F-105-python-sdk.md)

