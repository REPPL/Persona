# ADR-0029: Error Handling Strategy

## Status

Planned

## Context

Persona needs a unified error handling strategy to provide:
- Consistent error categorisation across the application
- Appropriate recovery behaviour for different error types
- Clear user-facing error messages
- Proper logging for debugging
- Graceful degradation when possible

Currently, error handling is ad-hoc at individual call sites without a systematic approach to classification, recovery, or user communication.

## Decision

Implement a **layered error handling strategy** with typed exceptions, recovery policies, and graceful degradation.

### Error Hierarchy

```python
class PersonaError(Exception):
    """Base exception for all Persona errors."""
    code: str
    recoverable: bool
    user_message: str

class ValidationError(PersonaError):
    """Input validation failures."""
    code = "VALIDATION_ERROR"
    recoverable = False

class ProviderError(PersonaError):
    """LLM provider failures."""
    code = "PROVIDER_ERROR"
    recoverable = True

class RateLimitError(ProviderError):
    """Rate limiting from provider."""
    code = "RATE_LIMIT"
    recoverable = True

class ConfigurationError(PersonaError):
    """Configuration problems."""
    code = "CONFIG_ERROR"
    recoverable = False

class NetworkError(PersonaError):
    """Network connectivity issues."""
    code = "NETWORK_ERROR"
    recoverable = True
```

### Error Categories

| Category | Examples | Recovery | User Action |
|----------|----------|----------|-------------|
| **Input** | Invalid YAML, missing fields | Fail fast | Fix input |
| **Config** | Missing API key, invalid setting | Fail fast | Fix config |
| **Transient** | Timeout, rate limit, 503 | Retry | Wait |
| **Provider** | Invalid model, quota exceeded | Failover | Change provider |
| **System** | OOM, disk full | Log & exit | Check resources |

### Recovery Policies

```python
@dataclass
class RecoveryPolicy:
    max_retries: int = 3
    backoff_base: float = 2.0
    max_wait: float = 60.0
    failover_enabled: bool = True
    degradation_enabled: bool = True

class ErrorHandler:
    def __init__(self, policy: RecoveryPolicy):
        self.policy = policy

    async def handle(self, error: PersonaError, context: Context) -> Result:
        if not error.recoverable:
            raise error

        if isinstance(error, RateLimitError):
            return await self._handle_rate_limit(error, context)

        if isinstance(error, ProviderError):
            return await self._handle_provider_error(error, context)

        if isinstance(error, NetworkError):
            return await self._handle_network_error(error, context)

        raise error
```

### User-Facing Messages

```python
ERROR_MESSAGES = {
    "RATE_LIMIT": "Rate limit reached. Waiting {wait}s before retrying...",
    "PROVIDER_ERROR": "Provider {provider} unavailable. Trying {fallback}...",
    "NETWORK_ERROR": "Network issue detected. Retrying in {wait}s...",
    "VALIDATION_ERROR": "Invalid input: {detail}",
    "CONFIG_ERROR": "Configuration error: {detail}",
}

def format_error_message(error: PersonaError, **context) -> str:
    template = ERROR_MESSAGES.get(error.code, str(error))
    return template.format(**context)
```

### Logging Strategy

```python
class ErrorLogger:
    def log(self, error: PersonaError, context: dict) -> None:
        if error.recoverable:
            logger.warning(
                f"{error.code}: {error}",
                extra={"context": context, "recoverable": True}
            )
        else:
            logger.error(
                f"{error.code}: {error}",
                extra={"context": context, "recoverable": False},
                exc_info=True
            )
```

## Consequences

**Positive:**
- Consistent error handling across codebase
- Clear recovery paths for different error types
- Better user experience with informative messages
- Easier debugging with structured logging
- Graceful degradation maintains functionality

**Negative:**
- Requires refactoring existing error handling
- More code for exception hierarchy
- Policy configuration complexity

## Alternatives Considered

### Result Types (Rust-style)

**Description:** Use `Result[T, E]` types instead of exceptions.

**Pros:** Explicit error handling, no hidden control flow.

**Cons:** Verbose, not Pythonic, major refactor.

**Why Not Chosen:** Python ecosystem expects exceptions.

### Global Exception Handler

**Description:** Single handler catches all exceptions at top level.

**Pros:** Simple, centralised.

**Cons:** Loses context, can't recover mid-operation.

**Why Not Chosen:** Need granular recovery.

### Status Codes

**Description:** Return status codes instead of exceptions.

**Pros:** Simple, consistent.

**Cons:** Easy to ignore, loses stack trace.

**Why Not Chosen:** Exceptions provide richer context.

## Research Reference

See [R-026: Error Recovery & Graceful Degradation](../../research/R-026-error-recovery-degradation.md) for detailed analysis of error handling patterns.

---

## Related Documentation

- [R-026: Error Recovery & Graceful Degradation](../../research/R-026-error-recovery-degradation.md)
- [ADR-0030: Async Execution Model](ADR-0030-async-execution-model.md)

---

**Status**: Planned
