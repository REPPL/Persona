"""
Security module for Persona.

Provides API key protection, rotation, rate limiting, and error handling.
"""

from persona.core.security.keys import (
    SecureString,
    mask_api_key,
    KeyMaskingFilter,
    redact_api_keys,
)
from persona.core.security.rotation import (
    KeyManager,
    KeyStatus,
    KeyHealth,
)
from persona.core.security.validation import (
    InputValidator,
    ValidationError,
    PathValidationError,
    ValueValidationError,
)
from persona.core.security.rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    RateLimitExceeded,
)
from persona.core.security.retry import (
    RetryStrategy,
    CircuitBreaker,
    CircuitState,
    ErrorClassifier,
    RetryableError,
    PermanentError,
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
