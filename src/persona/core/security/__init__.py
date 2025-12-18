"""
Security module for Persona.

Provides API key protection, rotation, rate limiting, and error handling.
"""

from persona.core.security.keys import (
    KeyMaskingFilter,
    SecureString,
    mask_api_key,
    redact_api_keys,
)
from persona.core.security.rate_limiter import (
    RateLimitConfig,
    RateLimiter,
    RateLimitExceeded,
)
from persona.core.security.retry import (
    CircuitBreaker,
    CircuitState,
    ErrorClassifier,
    PermanentError,
    RetryableError,
    RetryStrategy,
)
from persona.core.security.rotation import (
    KeyHealth,
    KeyManager,
    KeyStatus,
)
from persona.core.security.validation import (
    InputValidator,
    PathValidationError,
    ValidationError,
    ValueValidationError,
)

__all__ = [
    # Keys (F-051)
    "SecureString",
    "mask_api_key",
    "KeyMaskingFilter",
    "redact_api_keys",
    # Rotation (F-052)
    "KeyManager",
    "KeyStatus",
    "KeyHealth",
    # Validation (F-053)
    "InputValidator",
    "ValidationError",
    "PathValidationError",
    "ValueValidationError",
    # Rate Limiting (F-057)
    "RateLimiter",
    "RateLimitConfig",
    "RateLimitExceeded",
    # Retry (F-058)
    "RetryStrategy",
    "CircuitBreaker",
    "CircuitState",
    "ErrorClassifier",
    "RetryableError",
    "PermanentError",
]
