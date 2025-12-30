# R-026: Error Recovery & Graceful Degradation

## Executive Summary

This research analyses strategies for robust error handling in LLM-powered applications, focusing on partial failure handling, graceful degradation, and recovery mechanisms. The current Persona implementation has basic error handling but lacks systematic strategies for maintaining functionality when components fail. Recommended approach: implement a circuit breaker pattern with provider fallback chains and graceful degradation to cached/local alternatives.

---

## Research Context

| Attribute | Value |
|-----------|-------|
| **ID** | R-026 |
| **Category** | Reliability |
| **Status** | Complete |
| **Priority** | P2 |
| **Informs** | ADR-0029 (Error Handling Strategy), v1.13.0+ features |

---

## Problem Statement

LLM-powered applications face unique reliability challenges:
- API services have variable availability and rate limits
- Network issues can interrupt long-running generation
- Provider-specific errors require different handling
- Partial results should be preserved when possible
- User experience should degrade gracefully, not fail completely

Currently, Persona handles errors at individual call sites without a unified strategy for:
- Cross-provider failover
- Partial result preservation
- Circuit breaking for unhealthy providers
- Graceful degradation paths

---

## State of the Art Analysis

### Error Categories

| Category | Examples | Recovery Strategy |
|----------|----------|-------------------|
| **Transient** | Timeout, rate limit, 502/503 | Retry with backoff |
| **Provider** | Invalid API key, quota exceeded | Failover to alternative |
| **Input** | Invalid data, schema mismatch | Validate early, reject |
| **System** | OOM, disk full | Log, alert, graceful shutdown |
| **Logic** | Bug in code | Log, preserve state, report |

### Pattern 1: Circuit Breaker

Prevent cascading failures by stopping calls to unhealthy services.

```python
from enum import Enum
from dataclasses import dataclass
from time import monotonic

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0
    half_open_calls: int = 0

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if monotonic() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False

        # HALF_OPEN
        return self.half_open_calls < self.half_open_max_calls

    def record_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                self.state = CircuitState.CLOSED
        self.failure_count = 0

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = monotonic()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

**Evaluation:**
- ✅ Prevents cascade failures
- ✅ Allows automatic recovery
- ⚠️ Requires per-provider tracking
- ⚠️ Configuration tuning needed

### Pattern 2: Provider Fallback Chain

Define ordered fallback providers when primary fails.

```python
@dataclass
class FallbackChain:
    providers: list[Provider]

    async def execute(self, request: Request) -> Response:
        last_error = None

        for provider in self.providers:
            if not provider.circuit_breaker.can_execute():
                continue

            try:
                result = await provider.generate(request)
                provider.circuit_breaker.record_success()
                return result
            except RetryableError as e:
                provider.circuit_breaker.record_failure()
                last_error = e
                continue
            except NonRetryableError as e:
                raise  # Don't try alternatives

        raise AllProvidersFailedError(last_error)
```

**Configuration:**
```yaml
providers:
  fallback_chain:
    - provider: anthropic
      priority: 1
    - provider: openai
      priority: 2
    - provider: ollama
      priority: 3
      degraded: true  # Lower quality, but always available
```

### Pattern 3: Graceful Degradation

Provide reduced functionality rather than complete failure.

```python
class DegradationLevel(Enum):
    FULL = "full"           # All features available
    REDUCED = "reduced"     # Some features disabled
    MINIMAL = "minimal"     # Core functionality only
    CACHED = "cached"       # Return cached results only
    OFFLINE = "offline"     # Fully offline mode

class GracefulDegradation:
    def __init__(self):
        self.level = DegradationLevel.FULL
        self.cache = ResponseCache()

    async def generate(self, request: Request) -> Response:
        if self.level == DegradationLevel.FULL:
            return await self._full_generation(request)

        if self.level == DegradationLevel.REDUCED:
            return await self._reduced_generation(request)

        if self.level == DegradationLevel.CACHED:
            cached = self.cache.get(request)
            if cached:
                return cached.with_warning("Cached result")
            raise NoCachedResultError()

        if self.level == DegradationLevel.OFFLINE:
            return await self._offline_generation(request)

    async def _reduced_generation(self, request: Request) -> Response:
        """Generate with reduced features."""
        # Disable quality scoring
        # Use faster model
        # Skip validation
        return await self.provider.generate(
            request,
            skip_quality=True,
            model="fast"
        )

    async def _offline_generation(self, request: Request) -> Response:
        """Generate using local model only."""
        return await self.ollama_provider.generate(request)
```

### Pattern 4: Partial Result Preservation

Save intermediate results to prevent total loss.

```python
class PartialResultHandler:
    def __init__(self, storage: Storage):
        self.storage = storage

    async def process_batch_with_preservation(
        self,
        items: list[Item]
    ) -> BatchResult:
        successful = []
        failed = []

        for item in items:
            try:
                result = await self.process(item)
                successful.append(result)
                # Immediately persist
                await self.storage.save_result(result)
            except Exception as e:
                failed.append(FailedItem(item=item, error=e))
                # Log but continue
                logger.warning(f"Item {item.id} failed: {e}")

        return BatchResult(
            successful=successful,
            failed=failed,
            partial=len(failed) > 0
        )
```

### Pattern 5: Retry with Exponential Backoff

Handle transient failures with intelligent retry.

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class RetryableError(Exception):
    pass

class RateLimitError(RetryableError):
    pass

class TimeoutError(RetryableError):
    pass

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type(RetryableError)
)
async def generate_with_retry(request: Request) -> Response:
    return await provider.generate(request)
```

---

## Error Handling Matrix

| Error Type | Action | Fallback | User Message |
|------------|--------|----------|--------------|
| Rate limit | Retry + backoff | Next provider | "Waiting for rate limit..." |
| Timeout | Retry 2x | Next provider | "Request timed out, retrying..." |
| Auth error | Fail fast | None | "Invalid API key for {provider}" |
| Invalid input | Fail fast | None | "Input validation failed: {detail}" |
| Server error | Retry 1x | Next provider | "Provider error, trying alternative..." |
| Network error | Retry 3x | Offline mode | "Network issue, using local model..." |
| Quota exceeded | Fail fast | Next provider | "Quota exceeded, switching providers..." |

---

## Evaluation Matrix

| Pattern | Resilience | Complexity | UX | Performance |
|---------|------------|------------|-----|-------------|
| Circuit breaker | ✅ | ⚠️ | ✅ | ✅ |
| Fallback chain | ✅ | ⚠️ | ✅ | ⚠️ |
| Graceful degradation | ✅ | ⚠️ | ✅ | ✅ |
| Partial preservation | ✅ | ⚠️ | ✅ | ⚠️ |
| Retry with backoff | ⚠️ | ✅ | ⚠️ | ⚠️ |

---

## Recommendation

### Primary: Layered Error Handling

Implement multiple layers of error handling:

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Handling Layers                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Input Validation                                   │
│  └─ Fail fast for invalid input                             │
│                                                              │
│  Layer 2: Retry with Backoff                                │
│  └─ Handle transient failures                               │
│                                                              │
│  Layer 3: Circuit Breaker                                   │
│  └─ Prevent cascade failures                                │
│                                                              │
│  Layer 4: Provider Fallback                                 │
│  └─ Switch to alternative providers                         │
│                                                              │
│  Layer 5: Graceful Degradation                              │
│  └─ Reduce functionality if needed                          │
│                                                              │
│  Layer 6: Partial Preservation                              │
│  └─ Save what we have                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Configuration

```yaml
error_handling:
  retry:
    max_attempts: 3
    backoff_base: 2.0
    max_wait: 60
    retryable:
      - rate_limit
      - timeout
      - server_error

  circuit_breaker:
    enabled: true
    failure_threshold: 5
    recovery_timeout: 60
    per_provider: true

  fallback:
    enabled: true
    chain:
      - anthropic
      - openai
      - ollama
    allow_degradation: true

  degradation:
    levels:
      reduced:
        skip_quality: true
        use_fast_model: true
      minimal:
        skip_validation: true
        simple_output: true
      offline:
        provider: ollama

  preservation:
    enabled: true
    save_partial: true
    checkpoint_interval: 10
```

### Implementation Priority

1. **Retry with backoff** - Foundation layer
2. **Circuit breaker** - Prevent cascade failures
3. **Provider fallback** - Multi-provider resilience
4. **Partial preservation** - Protect user work
5. **Graceful degradation** - Maintain functionality

---

## Implementation Sketch

```python
class ResilientGenerator:
    def __init__(
        self,
        providers: list[Provider],
        config: ErrorHandlingConfig
    ):
        self.fallback_chain = FallbackChain([
            ProviderWithCircuit(p, CircuitBreaker())
            for p in providers
        ])
        self.degradation = GracefulDegradation(config.degradation)
        self.partial_handler = PartialResultHandler(storage)

    async def generate(self, request: Request) -> Response:
        # Layer 1: Validate
        validate_request(request)

        try:
            # Layer 2-4: Try with fallback
            return await self._generate_with_fallback(request)
        except AllProvidersFailedError:
            # Layer 5: Degrade
            self.degradation.level = DegradationLevel.OFFLINE
            return await self.degradation.generate(request)

    async def generate_batch(
        self,
        items: list[Item]
    ) -> BatchResult:
        # Layer 6: Preserve partial results
        return await self.partial_handler.process_batch_with_preservation(
            items,
            processor=self.generate
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, max=60),
        retry=retry_if_exception_type(RetryableError)
    )
    async def _generate_with_fallback(
        self,
        request: Request
    ) -> Response:
        return await self.fallback_chain.execute(request)
```

---

## References

1. [Circuit Breaker Pattern - Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
2. [Release It! - Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
3. [Tenacity Documentation](https://tenacity.readthedocs.io/)
4. [Netflix Hystrix (archived)](https://github.com/Netflix/Hystrix)
5. [Resilience4j](https://resilience4j.readme.io/)

---

## Related Documentation

- [ADR-0029: Error Handling Strategy](../decisions/adrs/ADR-0029-error-handling-strategy.md)
- [R-025: Batch Processing Optimisation](R-025-batch-processing-optimisation.md)
- [F-088: Async Generation](../roadmap/features/completed/F-088-async-generation.md)

---

**Status**: Complete
