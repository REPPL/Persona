"""
Exception hierarchy for the Persona SDK.

All SDK exceptions inherit from PersonaError, allowing callers to catch
all SDK-related errors with a single except clause.

Example:
    from persona.sdk import PersonaGenerator, PersonaError

    try:
        generator = PersonaGenerator(provider="anthropic")
        result = generator.generate(...)
    except PersonaError as e:
        print(f"Persona generation failed: {e}")
"""

from typing import Any


class PersonaError(Exception):
    """
    Base exception for all Persona SDK errors.

    All SDK exceptions inherit from this class.

    Attributes:
        message: Human-readable error message.
        details: Optional dictionary with additional error context.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Initialise PersonaError.

        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional error context.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation."""
        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({detail_str})"
        return self.message


class ConfigurationError(PersonaError):
    """
    Configuration-related errors.

    Raised when:
    - Invalid configuration values
    - Missing required configuration
    - Configuration file parsing errors
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
    ) -> None:
        """
        Initialise ConfigurationError.

        Args:
            message: Error message.
            field: The configuration field that caused the error.
            value: The invalid value (if applicable).
        """
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, details)
        self.field = field
        self.value = value


class ValidationError(PersonaError):
    """
    Schema validation errors.

    Raised when:
    - Pydantic validation fails
    - Invalid data types
    - Schema constraints violated
    """

    def __init__(
        self,
        message: str,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        """
        Initialise ValidationError.

        Args:
            message: Error message.
            errors: List of validation error dictionaries.
        """
        details = {"error_count": len(errors) if errors else 0}
        super().__init__(message, details)
        self.errors = errors or []


class DataError(PersonaError):
    """
    Data loading and processing errors.

    Raised when:
    - Input file not found
    - Unsupported file format
    - Empty or invalid data
    - Data parsing failures
    """

    def __init__(
        self,
        message: str,
        path: str | None = None,
        format: str | None = None,
    ) -> None:
        """
        Initialise DataError.

        Args:
            message: Error message.
            path: Path to the problematic file.
            format: Expected or detected file format.
        """
        details = {}
        if path:
            details["path"] = path
        if format:
            details["format"] = format
        super().__init__(message, details)
        self.path = path
        self.format = format


class ProviderError(PersonaError):
    """
    LLM provider-related errors.

    Raised when:
    - Provider not configured
    - API authentication fails
    - Provider unavailable
    - API key missing or invalid
    """

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        status_code: int | None = None,
    ) -> None:
        """
        Initialise ProviderError.

        Args:
            message: Error message.
            provider: The provider that caused the error.
            status_code: HTTP status code (if applicable).
        """
        details = {}
        if provider:
            details["provider"] = provider
        if status_code:
            details["status_code"] = status_code
        super().__init__(message, details)
        self.provider = provider
        self.status_code = status_code


class RateLimitError(ProviderError):
    """
    Rate limit exceeded errors.

    Raised when the LLM provider returns a rate limit error.
    Contains retry information when available.
    """

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        """
        Initialise RateLimitError.

        Args:
            message: Error message.
            provider: The provider that rate limited.
            retry_after: Seconds to wait before retrying.
        """
        super().__init__(message, provider, status_code=429)
        self.retry_after = retry_after
        if retry_after:
            self.details["retry_after"] = retry_after


class BudgetExceededError(PersonaError):
    """
    Budget/cost limit exceeded errors.

    Raised when:
    - Generation would exceed cost budget
    - Token limit exceeded
    """

    def __init__(
        self,
        message: str,
        budget: float | None = None,
        estimated_cost: float | None = None,
    ) -> None:
        """
        Initialise BudgetExceededError.

        Args:
            message: Error message.
            budget: The configured budget limit.
            estimated_cost: The estimated cost that exceeded budget.
        """
        details = {}
        if budget is not None:
            details["budget"] = f"${budget:.2f}"
        if estimated_cost is not None:
            details["estimated_cost"] = f"${estimated_cost:.2f}"
        super().__init__(message, details)
        self.budget = budget
        self.estimated_cost = estimated_cost


class GenerationError(PersonaError):
    """
    Persona generation errors.

    Raised when:
    - LLM returns invalid response
    - Parsing fails
    - Generation produces no personas
    """

    def __init__(
        self,
        message: str,
        stage: str | None = None,
        raw_response: str | None = None,
    ) -> None:
        """
        Initialise GenerationError.

        Args:
            message: Error message.
            stage: The pipeline stage where the error occurred.
            raw_response: The raw LLM response (for debugging).
        """
        details = {}
        if stage:
            details["stage"] = stage
        super().__init__(message, details)
        self.stage = stage
        self.raw_response = raw_response
