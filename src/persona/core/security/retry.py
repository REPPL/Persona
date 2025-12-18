"""
Error handling and retry logic (F-058).

Provides error classification, intelligent retry strategies,
and circuit breaker pattern implementation.
"""

import asyncio
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeVar

T = TypeVar("T")


class ErrorType(Enum):
    """Classification of error types."""

    NETWORK_TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    AUTH_FAILURE = "auth_failure"
    BAD_REQUEST = "bad_request"
    CONTEXT_TOO_LONG = "context_too_long"
    CONNECTION_ERROR = "connection_error"
    UNKNOWN = "unknown"


class RetryableError(Exception):
    """Exception for errors that can be retried."""

    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.UNKNOWN,
        retry_after: float | None = None,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.error_type = error_type
        self.retry_after = retry_after
        self.original_error = original_error


class PermanentError(Exception):
    """Exception for errors that should not be retried."""

    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.UNKNOWN,
        suggestion: str | None = None,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.error_type = error_type
        self.suggestion = suggestion
        self.original_error = original_error


class ErrorClassifier:
    """
    Classifies errors by type and recoverability.

    Examines exceptions and HTTP status codes to determine
    the appropriate error type and whether retry is appropriate.

    Example:
        >>> classifier = ErrorClassifier()
        >>> error_type = classifier.classify_status_code(429)
        ErrorType.RATE_LIMIT
        >>> classifier.is_retryable(ErrorType.RATE_LIMIT)
        True
    """

    # HTTP status codes and their error types
    STATUS_CODES: dict[int, ErrorType] = {
        400: ErrorType.BAD_REQUEST,
        401: ErrorType.AUTH_FAILURE,
        403: ErrorType.AUTH_FAILURE,
        404: ErrorType.BAD_REQUEST,
        408: ErrorType.NETWORK_TIMEOUT,
        429: ErrorType.RATE_LIMIT,
        500: ErrorType.SERVER_ERROR,
        502: ErrorType.SERVER_ERROR,
        503: ErrorType.SERVER_ERROR,
        504: ErrorType.NETWORK_TIMEOUT,
    }

    # Error types that can be retried
    RETRYABLE_TYPES: set[ErrorType] = {
        ErrorType.NETWORK_TIMEOUT,
        ErrorType.RATE_LIMIT,
        ErrorType.SERVER_ERROR,
        ErrorType.CONNECTION_ERROR,
    }

    # Error types that may be recovered with key rotation
    KEY_ROTATION_TYPES: set[ErrorType] = {
        ErrorType.AUTH_FAILURE,
    }

    def classify_status_code(self, status_code: int) -> ErrorType:
        """
        Classify an HTTP status code.

        Args:
            status_code: HTTP status code.

        Returns:
            Classified error type.
        """
        return self.STATUS_CODES.get(status_code, ErrorType.UNKNOWN)

    def classify_exception(self, error: Exception) -> ErrorType:
        """
        Classify an exception.

        Args:
            error: The exception to classify.

        Returns:
            Classified error type.
        """
        error_str = str(error).lower()

        # Check for common patterns
        if "timeout" in error_str or "timed out" in error_str:
            return ErrorType.NETWORK_TIMEOUT

        if "rate limit" in error_str or "too many requests" in error_str:
            return ErrorType.RATE_LIMIT

        if "connection" in error_str or "network" in error_str:
            return ErrorType.CONNECTION_ERROR

        if "context" in error_str and ("long" in error_str or "length" in error_str):
            return ErrorType.CONTEXT_TOO_LONG

        if (
            "auth" in error_str
            or "unauthorized" in error_str
            or "forbidden" in error_str
        ):
            return ErrorType.AUTH_FAILURE

        if "invalid" in error_str or "bad request" in error_str:
            return ErrorType.BAD_REQUEST

        return ErrorType.UNKNOWN

    def is_retryable(self, error_type: ErrorType) -> bool:
        """
        Check if an error type is retryable.

        Args:
            error_type: The error type.

        Returns:
            True if the error can be retried.
        """
        return error_type in self.RETRYABLE_TYPES

    def should_rotate_key(self, error_type: ErrorType) -> bool:
        """
        Check if an error type suggests key rotation.

        Args:
            error_type: The error type.

        Returns:
            True if key rotation should be attempted.
        """
        return error_type in self.KEY_ROTATION_TYPES

    def get_user_message(self, error_type: ErrorType) -> str:
        """
        Get a user-friendly message for an error type.

        Args:
            error_type: The error type.

        Returns:
            User-friendly error message.
        """
        messages = {
            ErrorType.NETWORK_TIMEOUT: "The request timed out. Please check your network connection.",
            ErrorType.RATE_LIMIT: "Rate limit exceeded. Please wait before retrying.",
            ErrorType.SERVER_ERROR: "The server encountered an error. This may be temporary.",
            ErrorType.AUTH_FAILURE: "Authentication failed. Please check your API key.",
            ErrorType.BAD_REQUEST: "The request was invalid. Please check your input.",
            ErrorType.CONTEXT_TOO_LONG: "The input is too long for the model's context window.",
            ErrorType.CONNECTION_ERROR: "Failed to connect to the server. Please check your network.",
            ErrorType.UNKNOWN: "An unexpected error occurred.",
        }
        return messages.get(error_type, "An error occurred.")

    def get_suggestion(self, error_type: ErrorType) -> str | None:
        """
        Get a suggestion for resolving an error.

        Args:
            error_type: The error type.

        Returns:
            Suggestion string, or None.
        """
        suggestions = {
            ErrorType.NETWORK_TIMEOUT: "Try increasing the timeout or check your connection.",
            ErrorType.RATE_LIMIT: "Wait a few seconds, or configure a backup API key.",
            ErrorType.AUTH_FAILURE: "Verify your API key with 'persona check'.",
            ErrorType.CONTEXT_TOO_LONG: "Try reducing the input size or using a model with a larger context window.",
        }
        return suggestions.get(error_type)


@dataclass
class RetryStrategy:
    """
    Configuration for retry behaviour.

    Defines how many times to retry, delay between retries,
    and which errors to retry.
    """

    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_range: float = 0.1  # 10% jitter

    retryable_errors: set[ErrorType] = field(
        default_factory=lambda: {
            ErrorType.NETWORK_TIMEOUT,
            ErrorType.RATE_LIMIT,
            ErrorType.SERVER_ERROR,
            ErrorType.CONNECTION_ERROR,
        }
    )

    def calculate_delay(self, attempt: int, retry_after: float | None = None) -> float:
        """
        Calculate delay before next retry.

        Args:
            attempt: Current attempt number (0-based).
            retry_after: Retry-After header value.

        Returns:
            Delay in seconds.
        """
        if retry_after is not None:
            return retry_after

        # Exponential backoff
        delay = self.initial_delay * (self.exponential_base**attempt)
        delay = min(delay, self.max_delay)

        # Add jitter
        if self.jitter:
            jitter_amount = delay * self.jitter_range
            delay += random.uniform(-jitter_amount, jitter_amount)

        return max(0, delay)

    def should_retry(self, error_type: ErrorType, attempt: int) -> bool:
        """
        Determine if a retry should be attempted.

        Args:
            error_type: The error type.
            attempt: Current attempt number.

        Returns:
            True if should retry.
        """
        if attempt >= self.max_retries:
            return False
        return error_type in self.retryable_errors


class CircuitState(Enum):
    """State of a circuit breaker."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Failures to open circuit
    success_threshold: int = 2  # Successes in half-open to close
    timeout: float = 60.0  # Seconds before half-open


@dataclass
class CircuitBreakerState:
    """State tracking for circuit breaker."""

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float | None = None
    last_state_change: float = field(default_factory=time.monotonic)


class CircuitBreaker:
    """
    Circuit breaker to prevent cascade failures.

    Monitors failures and opens the circuit when a threshold is reached,
    preventing further requests until recovery is likely.

    Example:
        >>> breaker = CircuitBreaker("anthropic")
        >>> if breaker.allow_request():
        ...     try:
        ...         result = make_request()
        ...         breaker.record_success()
        ...     except Exception as e:
        ...         breaker.record_failure()
        ...         raise
    """

    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
    ):
        """
        Initialise the circuit breaker.

        Args:
            name: Identifier for this circuit breaker.
            config: Circuit breaker configuration.
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitBreakerState()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, updating if necessary."""
        self._check_state_transition()
        return self._state.state

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (rejecting requests)."""
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    def allow_request(self) -> bool:
        """
        Check if a request should be allowed.

        Returns:
            True if request should proceed.
        """
        state = self.state

        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.HALF_OPEN:
            return True  # Allow test requests
        else:  # OPEN
            return False

    def record_success(self) -> None:
        """Record a successful request."""
        # Check for state transitions first (e.g., OPEN -> HALF_OPEN after timeout)
        self._check_state_transition()

        self._state.success_count += 1

        if self._state.state == CircuitState.HALF_OPEN:
            if self._state.success_count >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def record_failure(self) -> None:
        """Record a failed request."""
        # Check for state transitions first (e.g., OPEN -> HALF_OPEN after timeout)
        self._check_state_transition()

        self._state.failure_count += 1
        self._state.last_failure_time = time.monotonic()

        if self._state.state == CircuitState.CLOSED:
            if self._state.failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
        elif self._state.state == CircuitState.HALF_OPEN:
            # Any failure in half-open returns to open
            self._transition_to(CircuitState.OPEN)

    def reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        self._state = CircuitBreakerState()

    def get_status(self) -> dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._state.failure_count,
            "success_count": self._state.success_count,
            "last_failure": self._state.last_failure_time,
            "time_in_state": time.monotonic() - self._state.last_state_change,
        }

    def _check_state_transition(self) -> None:
        """Check and perform any necessary state transitions."""
        if self._state.state == CircuitState.OPEN:
            # Check if timeout has elapsed
            time_since_failure = time.monotonic() - (
                self._state.last_failure_time or self._state.last_state_change
            )
            if time_since_failure >= self.config.timeout:
                self._transition_to(CircuitState.HALF_OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        self._state.state = new_state
        self._state.last_state_change = time.monotonic()

        if new_state == CircuitState.CLOSED:
            self._state.failure_count = 0
            self._state.success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._state.success_count = 0


class RetryExecutor:
    """
    Executes operations with automatic retry.

    Example:
        >>> executor = RetryExecutor()
        >>> result = await executor.execute_async(make_api_call)
    """

    def __init__(
        self,
        strategy: RetryStrategy | None = None,
        classifier: ErrorClassifier | None = None,
    ):
        """Initialise the executor."""
        self.strategy = strategy or RetryStrategy()
        self.classifier = classifier or ErrorClassifier()

    async def execute_async(
        self,
        operation: Callable[[], T],
        on_retry: Callable[[int, Exception, float], None] | None = None,
    ) -> T:
        """
        Execute an async operation with retry.

        Args:
            operation: Async callable to execute.
            on_retry: Callback(attempt, error, delay) on retry.

        Returns:
            Result of the operation.

        Raises:
            Exception: If all retries exhausted.
        """
        last_error: Exception | None = None

        for attempt in range(self.strategy.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation()
                else:
                    return operation()
            except Exception as e:
                last_error = e
                error_type = self.classifier.classify_exception(e)

                if not self.strategy.should_retry(error_type, attempt):
                    raise PermanentError(
                        str(e),
                        error_type=error_type,
                        suggestion=self.classifier.get_suggestion(error_type),
                        original_error=e,
                    )

                # Calculate delay
                retry_after = getattr(e, "retry_after", None)
                delay = self.strategy.calculate_delay(attempt, retry_after)

                if on_retry:
                    on_retry(attempt, e, delay)

                await asyncio.sleep(delay)

        # Should not reach here, but just in case
        raise last_error or Exception("Retry failed")

    def execute_sync(
        self,
        operation: Callable[[], T],
        on_retry: Callable[[int, Exception, float], None] | None = None,
    ) -> T:
        """
        Execute a sync operation with retry.

        Args:
            operation: Callable to execute.
            on_retry: Callback(attempt, error, delay) on retry.

        Returns:
            Result of the operation.

        Raises:
            Exception: If all retries exhausted.
        """
        last_error: Exception | None = None

        for attempt in range(self.strategy.max_retries + 1):
            try:
                return operation()
            except Exception as e:
                last_error = e
                error_type = self.classifier.classify_exception(e)

                if not self.strategy.should_retry(error_type, attempt):
                    raise PermanentError(
                        str(e),
                        error_type=error_type,
                        suggestion=self.classifier.get_suggestion(error_type),
                        original_error=e,
                    )

                retry_after = getattr(e, "retry_after", None)
                delay = self.strategy.calculate_delay(attempt, retry_after)

                if on_retry:
                    on_retry(attempt, e, delay)

                time.sleep(delay)

        raise last_error or Exception("Retry failed")
