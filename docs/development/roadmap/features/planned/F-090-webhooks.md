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

- [ ] Create WebhookManager class
- [ ] Implement webhook registration
- [ ] Add event filtering
- [ ] Implement payload signing
- [ ] Add retry with backoff
- [ ] Support custom templates
- [ ] Add webhook test command
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Webhooks delivered reliably
- [ ] Signature verification works
- [ ] Retry logic handles failures
- [ ] Custom templates work
- [ ] Test coverage ≥ 80%

## Dependencies

- F-089: REST API
- F-073: Experiment logger

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [F-089: REST API](F-089-rest-api.md)

