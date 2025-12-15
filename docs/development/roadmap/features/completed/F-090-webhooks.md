# F-090: Webhooks

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-008 |
| **Milestone** | v0.9.0 |
| **Priority** | P3 |
| **Category** | API |

## Problem Statement

Long-running generation operations need a way to notify external systems when complete. Webhooks enable event-driven integrations without polling.

## Design Approach

- Register webhook URLs per experiment
- POST events to registered URLs
- Support event filtering
- Include signature for verification
- Retry on failure with backoff

### Webhook Events

| Event | Trigger |
|-------|---------|
| `generation.started` | Generation begins |
| `generation.progress` | Progress update (optional) |
| `generation.completed` | Generation succeeds |
| `generation.failed` | Generation fails |
| `persona.created` | Individual persona ready |

### Webhook Configuration

```yaml
# experiment.yaml
webhooks:
  - url: "https://example.com/webhook"
    events: ["generation.completed", "generation.failed"]
    secret: "${WEBHOOK_SECRET}"
    timeout: 30

  - url: "https://slack.com/api/webhook"
    events: ["generation.completed"]
    template: slack  # Use Slack-formatted payload
```

### Webhook Payload

```json
{
  "event": "generation.completed",
  "timestamp": "2025-12-14T10:32:15Z",
  "experiment_id": "exp-abc123",
  "run_id": "run-def456",
  "data": {
    "persona_count": 3,
    "duration_seconds": 135,
    "cost_usd": 0.42,
    "output_path": "outputs/2025-12-14_103000/"
  }
}
```

### Signature Verification

```python
# Verify webhook signature
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

## Implementation Tasks

- [x] Create WebhookManager class
- [x] Implement webhook registration
- [x] Add event filtering
- [x] Implement payload signing
- [x] Add retry with backoff
- [ ] Support custom templates (deferred)
- [ ] Add webhook test command (deferred)
- [x] Write unit tests
- [x] Write integration tests

## Success Criteria

- [x] Webhooks delivered reliably
- [x] Signature verification works
- [x] Retry logic handles failures
- [ ] Custom templates work (deferred)
- [x] Test coverage ≥ 80%

## Dependencies

- F-089: REST API
- F-073: Experiment logger

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [F-089: REST API](F-089-rest-api.md)

