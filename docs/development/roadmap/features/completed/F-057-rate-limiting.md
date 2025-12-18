# F-057: Rate Limiting

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003, UC-007 |
| **Milestone** | v0.6.0 |
| **Priority** | P1 |
| **Category** | LLM |

## Problem Statement

LLM providers enforce rate limits. Exceeding limits causes request failures and potential account issues. Persona should proactively manage request rates.

## Design Approach

- Track request rates per provider
- Implement token bucket algorithm
- Respect provider-specific limits
- Queue requests when near limit
- Backoff on 429 responses

### Rate Limit Configuration

```yaml
# vendors.yaml
anthropic:
  rate_limits:
    requests_per_minute: 60
    tokens_per_minute: 100000
    concurrent_requests: 5
  backoff:
    initial_delay: 1.0
    max_delay: 60.0
    multiplier: 2.0
```

### Token Bucket Algorithm

```python
class RateLimiter:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate          # Tokens per second
        self.capacity = capacity  # Bucket size
        self.tokens = capacity
        self.last_update = time.monotonic()

    async def acquire(self, tokens: int = 1) -> float:
        """Wait until tokens available, return wait time."""
        ...
```

## Implementation Tasks

- [ ] Create RateLimiter class
- [ ] Implement token bucket algorithm
- [ ] Add per-provider rate tracking
- [ ] Implement request queueing
- [ ] Add 429 response handling
- [ ] Implement exponential backoff
- [ ] Add rate limit status display
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Rate limits never exceeded
- [ ] Graceful handling of 429 responses
- [ ] Clear feedback on rate limit status
- [ ] Configurable per-provider limits
- [ ] Test coverage ≥ 80%

## Dependencies

- F-002: LLM provider abstraction
- F-088: Async support

---

## Related Documentation

- [Milestone v0.6.0](../../milestones/v0.6.0.md)
- [Provider APIs Reference](../../../../reference/provider-apis.md)
