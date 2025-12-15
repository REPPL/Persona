"""
Persona error hierarchy.

This module defines all exception types used throughout Persona,
organised in a structured hierarchy for easy handling.
"""

from __future__ import annotations


class PersonaError(Exception):
    """Base exception for all Persona errors."""

    code: str = "PERSONA-900-001"
    message: str = "An error occurred"

    def __init__(self, message: str | None = None, **kwargs):
        self.message = message or self.message
        self.details = kwargs
        super().__init__(self.message)


# Configuration Errors (100-199)


class ConfigurationError(PersonaError):
    """Base class for configuration-related errors."""

    code = "PERSONA-100-000"
    message = "Configuration error"


class MissingAPIKeyError(ConfigurationError):
    """API key not found for provider."""

    code = "PERSONA-100-001"
    message = "API key not found"

    def __init__(self, provider: str, env_var: str | None = None):
        self.provider = provider
        self.env_var = env_var or f"{provider.upper()}_API_KEY"
        super().__init__(
            f"API key not found for provider: {provider}. "
            f"Set the {self.env_var} environment variable.",
            provider=provider,
            env_var=self.env_var,
        )


class InvalidConfigError(ConfigurationError):
    """Configuration file has invalid syntax or values."""

    code = "PERSONA-100-002"
    message = "Invalid configuration"

    def __init__(self, details: str, path: str | None = None):
        self.path = path
        super().__init__(
            f"Invalid configuration: {details}",
            details=details,
            path=path,
        )


class ProviderNotFoundError(ConfigurationError):
    """Specified provider is not supported."""

    code = "PERSONA-100-003"
    message = "Provider not found"

    def __init__(self, provider: str, available: list[str] | None = None):
        self.provider = provider
        self.available = available or []
        msg = f"Provider not found: {provider}"
        if self.available:
            msg += f". Available: {', '.join(self.available)}"
        super().__init__(msg, provider=provider, available=self.available)


class ModelNotConfiguredError(ConfigurationError):
    """Specified model is not available for the provider."""

    code = "PERSONA-100-004"
    message = "Model not configured"

    def __init__(self, model: str, provider: str | None = None):
        self.model = model
        self.provider = provider
        msg = f"Model not configured: {model}"
        if provider:
            msg += f" for provider {provider}"
        super().__init__(msg, model=model, provider=provider)


# Data Errors (200-299)


class DataError(PersonaError):
    """Base class for data-related errors."""

    code = "PERSONA-200-000"
    message = "Data error"


class DataLoadError(DataError):
    """Failed to load data from path."""

    code = "PERSONA-200-001"
    message = "Failed to load data"

    def __init__(self, path: str, reason: str | None = None):
        self.path = path
        self.reason = reason
        msg = f"Failed to load data from: {path}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg, path=path, reason=reason)


class DataFormatError(DataError):
    """Data file format is not recognised or malformed."""

    code = "PERSONA-200-002"
    message = "Unsupported data format"

    def __init__(self, format_name: str, path: str | None = None):
        self.format_name = format_name
        self.path = path
        msg = f"Unsupported or invalid data format: {format_name}"
        if path:
            msg += f" in {path}"
        super().__init__(msg, format_name=format_name, path=path)


class EmptyDataError(DataError):
    """Data source contains no usable content."""

    code = "PERSONA-200-003"
    message = "No data found"

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"No data found in: {path}", path=path)


class EncodingError(DataError):
    """File uses unsupported text encoding."""

    code = "PERSONA-200-004"
    message = "Failed to decode file"

    def __init__(self, path: str, encoding: str | None = None):
        self.path = path
        self.encoding = encoding
        msg = f"Failed to decode file: {path}"
        if encoding:
            msg += f" (detected: {encoding})"
        super().__init__(msg, path=path, encoding=encoding)


# Provider Errors (300-399)


class ProviderError(PersonaError):
    """Base class for LLM provider errors."""

    code = "PERSONA-300-000"
    message = "Provider error"


class APIError(ProviderError):
    """LLM provider API returned an error."""

    code = "PERSONA-300-001"
    message = "API request failed"

    def __init__(self, details: str, status_code: int | None = None):
        self.status_code = status_code
        msg = f"API request failed: {details}"
        if status_code:
            msg = f"API request failed (HTTP {status_code}): {details}"
        super().__init__(msg, details=details, status_code=status_code)


class RateLimitError(ProviderError):
    """Too many requests to the provider API."""

    code = "PERSONA-300-002"
    message = "Rate limit exceeded"

    def __init__(self, retry_after: int | None = None):
        self.retry_after = retry_after
        msg = "Rate limit exceeded"
        if retry_after:
            msg += f". Retry after: {retry_after}s"
        super().__init__(msg, retry_after=retry_after)


class AuthenticationError(ProviderError):
    """API key is invalid, expired, or has insufficient permissions."""

    code = "PERSONA-300-003"
    message = "Authentication failed"

    def __init__(self, provider: str, reason: str | None = None):
        self.provider = provider
        self.reason = reason
        msg = f"Authentication failed for provider: {provider}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg, provider=provider, reason=reason)


class ModelNotFoundError(ProviderError):
    """Specified model doesn't exist or isn't available."""

    code = "PERSONA-300-004"
    message = "Model not found"

    def __init__(self, model: str, provider: str | None = None):
        self.model = model
        self.provider = provider
        msg = f"Model not found: {model}"
        if provider:
            msg += f" (provider: {provider})"
        super().__init__(msg, model=model, provider=provider)


class ContextLengthError(ProviderError):
    """Input exceeds model context length."""

    code = "PERSONA-300-005"
    message = "Context length exceeded"

    def __init__(self, tokens: int, max_tokens: int, model: str | None = None):
        self.tokens = tokens
        self.max_tokens = max_tokens
        self.model = model
        msg = f"Input exceeds model context length: {tokens} > {max_tokens}"
        if model:
            msg += f" (model: {model})"
        super().__init__(msg, tokens=tokens, max_tokens=max_tokens, model=model)


class TimeoutError(ProviderError):
    """Provider took too long to respond."""

    code = "PERSONA-300-006"
    message = "Request timed out"

    def __init__(self, timeout: int):
        self.timeout = timeout
        super().__init__(f"Request timed out after {timeout}s", timeout=timeout)


# Validation Errors (400-499)


class ValidationError(PersonaError):
    """Base class for validation errors."""

    code = "PERSONA-400-000"
    message = "Validation error"


class InvalidPersonaError(ValidationError):
    """Generated persona doesn't match expected schema."""

    code = "PERSONA-400-001"
    message = "Invalid persona"

    def __init__(self, details: str, persona_name: str | None = None):
        self.persona_name = persona_name
        msg = f"Generated persona is invalid: {details}"
        if persona_name:
            msg = f"Generated persona '{persona_name}' is invalid: {details}"
        super().__init__(msg, details=details, persona_name=persona_name)


class SchemaValidationError(ValidationError):
    """Persona data doesn't match required schema."""

    code = "PERSONA-400-002"
    message = "Schema validation failed"

    def __init__(self, field: str, expected: str | None = None, got: str | None = None):
        self.field = field
        self.expected = expected
        self.got = got
        msg = f"Schema validation failed: {field}"
        if expected:
            msg += f" (expected {expected}"
            if got:
                msg += f", got {got}"
            msg += ")"
        super().__init__(msg, field=field, expected=expected, got=got)


class MissingFieldError(ValidationError):
    """Generated persona is missing a required field."""

    code = "PERSONA-400-003"
    message = "Required field missing"

    def __init__(self, field: str, persona_name: str | None = None):
        self.field = field
        self.persona_name = persona_name
        msg = f"Required field missing: {field}"
        if persona_name:
            msg += f" in persona '{persona_name}'"
        super().__init__(msg, field=field, persona_name=persona_name)


# Budget Errors (500-599)


class BudgetError(PersonaError):
    """Base class for budget-related errors."""

    code = "PERSONA-500-000"
    message = "Budget error"


class CostLimitExceededError(BudgetError):
    """Generation would exceed configured cost limit."""

    code = "PERSONA-500-001"
    message = "Cost limit exceeded"

    def __init__(self, estimated_cost: float, limit: float):
        self.estimated_cost = estimated_cost
        self.limit = limit
        super().__init__(
            f"Estimated cost ${estimated_cost:.4f} exceeds limit ${limit:.4f}",
            estimated_cost=estimated_cost,
            limit=limit,
        )


class TokenLimitExceededError(BudgetError):
    """Token count exceeds configured limits."""

    code = "PERSONA-500-002"
    message = "Token limit exceeded"

    def __init__(self, count: int, limit: int, token_type: str = "total"):
        self.count = count
        self.limit = limit
        self.token_type = token_type
        super().__init__(
            f"{token_type.title()} token count {count} exceeds limit {limit}",
            count=count,
            limit=limit,
            token_type=token_type,
        )


# Internal Errors (900-999)


class InternalError(PersonaError):
    """Unexpected error in Persona internals."""

    code = "PERSONA-900-001"
    message = "Internal error"

    def __init__(self, details: str):
        super().__init__(f"Internal error: {details}", details=details)


class ConfigCorruptedError(PersonaError):
    """Configuration file is unreadable or corrupted."""

    code = "PERSONA-900-002"
    message = "Configuration file corrupted"

    def __init__(self, path: str, reason: str | None = None):
        self.path = path
        self.reason = reason
        msg = f"Configuration file corrupted: {path}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg, path=path, reason=reason)
