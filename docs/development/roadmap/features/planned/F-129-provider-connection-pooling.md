# F-129: Provider HTTP Connection Pooling

**Milestone:** v1.11.0 - Code Quality & Architecture

**Category:** Performance

**Priority:** High

---

## Problem Statement

Each API call creates a new `httpx.Client()`, which:
- Creates new TCP connection per request
- Performs SSL/TLS handshake each time
- Loses connection pooling benefits
- Slows down batch operations significantly

Affected files:
- `src/persona/core/providers/anthropic.py`
- `src/persona/core/providers/openai.py`
- `src/persona/core/providers/gemini.py`

---

## Solution

Create base HTTP provider with connection pooling:

```python
class HTTPProvider(LLMProvider):
    """Base provider with connection pooling."""

    _client: httpx.AsyncClient | None = None

    @property
    async def client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(120.0),
                limits=httpx.Limits(max_connections=10),
            )
        return self._client

    async def cleanup(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
```

---

## Implementation Tasks

- [ ] Create `src/persona/core/providers/http_base.py`
- [ ] Add connection pool configuration options
- [ ] Refactor AnthropicProvider to inherit HTTPProvider
- [ ] Refactor OpenAIProvider to inherit HTTPProvider
- [ ] Refactor GeminiProvider to inherit HTTPProvider
- [ ] Add cleanup lifecycle to ProviderFactory
- [ ] Add connection pooling tests
- [ ] Benchmark before/after performance

---

## Success Criteria

- [ ] All HTTP providers use shared connection pool
- [ ] API call latency reduced by ≥20% in batch operations
- [ ] Memory usage stable during batch operations
- [ ] Proper cleanup on application shutdown

---

## Dependencies

None

---

## Related Documentation

- [v1.11.0 Milestone](../../milestones/v1.11.0.md)

---

**Status**: Planned
