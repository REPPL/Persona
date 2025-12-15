# F-052: API Key Rotation on Failure

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003 |
| **Milestone** | v0.6.0 |
| **Priority** | P1 |
| **Category** | Security |

## Problem Statement

When API keys expire or are revoked, users experience generation failures. The system should gracefully handle key failures and support automatic rotation to backup keys.

## Design Approach

- Detect authentication failures (401, 403)
- Support multiple keys per provider
- Automatic fallback to backup keys
- Clear notifications about key status
- Key health monitoring

### Key Configuration

```yaml
# vendors.yaml
anthropic:
  api_keys:
    - ${ANTHROPIC_API_KEY}          # Primary
    - ${ANTHROPIC_API_KEY_BACKUP}   # Backup
  rotation:
    on_failure: true
    max_retries: 2
```

### Rotation Flow

```
Request Failed (401)
    ↓
Log Key Failure
    ↓
Check Backup Keys
    ↓
[Has Backup] → Rotate to Backup → Retry Request
    ↓
[No Backup] → Notify User → Fail Gracefully
```

## Implementation Tasks

- [ ] Create KeyManager class
- [ ] Implement key rotation logic
- [ ] Add 401/403 detection
- [ ] Support multiple keys per provider
- [ ] Add key health monitoring
- [ ] Create rotation notifications
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Automatic rotation on auth failure
- [ ] Clear failure notifications
- [ ] Key health visible in status
- [ ] Graceful degradation when no keys available
- [ ] Test coverage ≥ 80%

## Dependencies

- F-002: LLM provider abstraction
- F-051: API key protection

---

## Related Documentation

- [Milestone v0.6.0](../../milestones/v0.6.0.md)
- [ADR-0014: Security API Keys](../../../decisions/adrs/ADR-0014-security-api-keys.md)

