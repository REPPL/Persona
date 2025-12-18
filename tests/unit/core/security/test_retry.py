"""Tests for error handling and retry logic (F-058)."""

import time

import pytest
from persona.core.security.retry import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    ErrorClassifier,
    ErrorType,
    PermanentError,
    RetryableError,
    RetryExecutor,
    RetryStrategy,
)


class TestErrorType:
    """Tests for ErrorType enum."""

    def test_all_types_defined(self):
        """All expected error types are defined."""
        assert ErrorType.NETWORK_TIMEOUT
        assert ErrorType.RATE_LIMIT
        assert ErrorType.SERVER_ERROR
        assert ErrorType.AUTH_FAILURE
        assert ErrorType.BAD_REQUEST
        assert ErrorType.CONTEXT_TOO_LONG
        assert ErrorType.CONNECTION_ERROR
        assert ErrorType.UNKNOWN


class TestErrorClassifier:
    """Tests for ErrorClassifier."""

    def test_classify_status_429(self):
        """Classifies 429 as rate limit."""
        classifier = ErrorClassifier()
        result = classifier.classify_status_code(429)
        assert result == ErrorType.RATE_LIMIT

    def test_classify_status_401(self):
        """Classifies 401 as auth failure."""
        classifier = ErrorClassifier()
        result = classifier.classify_status_code(401)
        assert result == ErrorType.AUTH_FAILURE

    def test_classify_status_500(self):
        """Classifies 500 as server error."""
        classifier = ErrorClassifier()
        result = classifier.classify_status_code(500)
        assert result == ErrorType.SERVER_ERROR

    def test_classify_status_408(self):
        """Classifies 408 as timeout."""
        classifier = ErrorClassifier()
        result = classifier.classify_status_code(408)
        assert result == ErrorType.NETWORK_TIMEOUT

    def test_classify_status_unknown(self):
        """Classifies unknown status as unknown."""
        classifier = ErrorClassifier()
        result = classifier.classify_status_code(999)
        assert result == ErrorType.UNKNOWN

    def test_classify_timeout_exception(self):
        """Classifies timeout exception."""
        classifier = ErrorClassifier()
        result = classifier.classify_exception(TimeoutError("Connection timed out"))
        assert result == ErrorType.NETWORK_TIMEOUT

    def test_classify_rate_limit_exception(self):
        """Classifies rate limit exception."""
        classifier = ErrorClassifier()
        result = classifier.classify_exception(Exception("Rate limit exceeded"))
        assert result == ErrorType.RATE_LIMIT

    def test_classify_connection_exception(self):
        """Classifies connection exception."""
        classifier = ErrorClassifier()
        result = classifier.classify_exception(ConnectionError("Connection refused"))
        assert result == ErrorType.CONNECTION_ERROR

    def test_classify_context_exception(self):
        """Classifies context length exception."""
        classifier = ErrorClassifier()
        result = classifier.classify_exception(
            Exception("Context length exceeded maximum")
        )
        assert result == ErrorType.CONTEXT_TOO_LONG

    def test_is_retryable_timeout(self):
        """Timeout is retryable."""
        classifier = ErrorClassifier()
        assert classifier.is_retryable(ErrorType.NETWORK_TIMEOUT)

    def test_is_retryable_rate_limit(self):
        """Rate limit is retryable."""
        classifier = ErrorClassifier()
        assert classifier.is_retryable(ErrorType.RATE_LIMIT)

    def test_is_not_retryable_auth(self):
        """Auth failure is not retryable."""
        classifier = ErrorClassifier()
        assert not classifier.is_retryable(ErrorType.AUTH_FAILURE)

    def test_is_not_retryable_bad_request(self):
        """Bad request is not retryable."""
        classifier = ErrorClassifier()
        assert not classifier.is_retryable(ErrorType.BAD_REQUEST)

    def test_should_rotate_key_auth(self):
        """Auth failure should rotate key."""
        classifier = ErrorClassifier()
        assert classifier.should_rotate_key(ErrorType.AUTH_FAILURE)

    def test_should_not_rotate_key_timeout(self):
        """Timeout should not rotate key."""
        classifier = ErrorClassifier()
        assert not classifier.should_rotate_key(ErrorType.NETWORK_TIMEOUT)

    def test_user_message(self):
        """Returns user-friendly message."""
        classifier = ErrorClassifier()
        msg = classifier.get_user_message(ErrorType.RATE_LIMIT)
        assert "Rate limit" in msg

    def test_suggestion(self):
        """Returns suggestion for error."""
        classifier = ErrorClassifier()
        suggestion = classifier.get_suggestion(ErrorType.AUTH_FAILURE)
        assert suggestion is not None
        assert "API key" in suggestion


class TestRetryStrategy:
    """Tests for RetryStrategy."""

    def test_default_values(self):
        """Default strategy values."""
        strategy = RetryStrategy()
        assert strategy.max_retries == 3
        assert strategy.initial_delay == 1.0
        assert strategy.exponential_base == 2.0

    def test_calculate_delay_first_attempt(self):
        """Calculates delay for first attempt."""
        strategy = RetryStrategy(initial_delay=1.0, jitter=False)
        delay = strategy.calculate_delay(0)
        assert delay == 1.0

    def test_calculate_delay_exponential(self):
        """Calculates exponential delay."""
        strategy = RetryStrategy(initial_delay=1.0, exponential_base=2.0, jitter=False)
        delay = strategy.calculate_delay(2)  # 1.0 * 2^2 = 4.0
        assert delay == 4.0

    def test_calculate_delay_max(self):
        """Respects maximum delay."""
        strategy = RetryStrategy(
            initial_delay=1.0,
            max_delay=5.0,
            exponential_base=10.0,
            jitter=False,
        )
        delay = strategy.calculate_delay(5)
        assert delay == 5.0

    def test_calculate_delay_retry_after(self):
        """Uses retry-after when provided."""
        strategy = RetryStrategy()
        delay = strategy.calculate_delay(0, retry_after=30.0)
        assert delay == 30.0

    def test_calculate_delay_with_jitter(self):
        """Adds jitter to delay."""
        strategy = RetryStrategy(initial_delay=10.0, jitter=True, jitter_range=0.5)
        delays = [strategy.calculate_delay(0) for _ in range(10)]

        # With jitter, delays should vary
        assert len(set(delays)) > 1

    def test_should_retry_within_limit(self):
        """Should retry within limit."""
        strategy = RetryStrategy(max_retries=3)
        assert strategy.should_retry(ErrorType.NETWORK_TIMEOUT, 0)
        assert strategy.should_retry(ErrorType.NETWORK_TIMEOUT, 2)

    def test_should_not_retry_at_limit(self):
        """Should not retry at limit."""
        strategy = RetryStrategy(max_retries=3)
        assert not strategy.should_retry(ErrorType.NETWORK_TIMEOUT, 3)

    def test_should_not_retry_permanent_error(self):
        """Should not retry permanent error."""
        strategy = RetryStrategy()
        assert not strategy.should_retry(ErrorType.BAD_REQUEST, 0)


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""

    def test_initial_state_closed(self):
        """Initial state is closed."""
        breaker = CircuitBreaker("test")
        assert breaker.state == CircuitState.CLOSED
        assert breaker.is_closed
        assert not breaker.is_open

    def test_allow_request_closed(self):
        """Allows requests when closed."""
        breaker = CircuitBreaker("test")
        assert breaker.allow_request()

    def test_record_success(self):
        """Records successful request."""
        breaker = CircuitBreaker("test")
        breaker.record_success()

        status = breaker.get_status()
        assert status["success_count"] == 1

    def test_opens_after_threshold(self):
        """Opens after failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker("test", config)

        for _ in range(3):
            breaker.record_failure()

        assert breaker.is_open
        assert not breaker.allow_request()

    def test_half_open_after_timeout(self):
        """Transitions to half-open after timeout."""
        config = CircuitBreakerConfig(failure_threshold=1, timeout=0.01)
        breaker = CircuitBreaker("test", config)

        breaker.record_failure()
        assert breaker.is_open

        # Wait for timeout
        time.sleep(0.02)
        assert breaker.state == CircuitState.HALF_OPEN
        assert breaker.allow_request()

    def test_closes_after_success_in_half_open(self):
        """Closes after success in half-open state."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=2,
            timeout=0.01,
        )
        breaker = CircuitBreaker("test", config)

        breaker.record_failure()
        time.sleep(0.02)

        # In half-open, record successes
        breaker.record_success()
        breaker.record_success()

        assert breaker.is_closed

    def test_reopens_on_failure_in_half_open(self):
        """Re-opens on failure in half-open state."""
        config = CircuitBreakerConfig(failure_threshold=1, timeout=0.01)
        breaker = CircuitBreaker("test", config)

        breaker.record_failure()
        time.sleep(0.02)

        assert breaker.state == CircuitState.HALF_OPEN
        breaker.record_failure()

        assert breaker.is_open

    def test_reset(self):
        """Resets to initial state."""
        breaker = CircuitBreaker("test")
        breaker.record_failure()
        breaker.record_failure()

        breaker.reset()

        assert breaker.is_closed
        status = breaker.get_status()
        assert status["failure_count"] == 0

    def test_get_status(self):
        """Returns status information."""
        breaker = CircuitBreaker("test")
        status = breaker.get_status()

        assert status["name"] == "test"
        assert "state" in status
        assert "failure_count" in status
        assert "success_count" in status


class TestRetryExecutor:
    """Tests for RetryExecutor."""

    @pytest.mark.asyncio
    async def test_execute_async_success(self):
        """Executes async operation successfully."""
        executor = RetryExecutor()

        async def operation():
            return "success"

        result = await executor.execute_async(operation)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_execute_async_retry(self):
        """Retries async operation on failure."""
        executor = RetryExecutor(
            strategy=RetryStrategy(max_retries=3, initial_delay=0.01, jitter=False)
        )

        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError("Timeout")
            return "success"

        result = await executor.execute_async(operation)
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_execute_async_permanent_error(self):
        """Raises permanent error without retry."""
        executor = RetryExecutor()

        async def operation():
            raise Exception("Invalid request - bad input")

        with pytest.raises(PermanentError):
            await executor.execute_async(operation)

    @pytest.mark.asyncio
    async def test_execute_async_on_retry_callback(self):
        """Calls on_retry callback."""
        executor = RetryExecutor(
            strategy=RetryStrategy(max_retries=2, initial_delay=0.01, jitter=False)
        )

        retries = []

        def on_retry(attempt, error, delay):
            retries.append((attempt, str(error), delay))

        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("Timeout")
            return "success"

        await executor.execute_async(operation, on_retry=on_retry)
        assert len(retries) == 1

    def test_execute_sync_success(self):
        """Executes sync operation successfully."""
        executor = RetryExecutor()

        def operation():
            return "success"

        result = executor.execute_sync(operation)
        assert result == "success"

    def test_execute_sync_retry(self):
        """Retries sync operation on failure."""
        executor = RetryExecutor(
            strategy=RetryStrategy(max_retries=3, initial_delay=0.01, jitter=False)
        )

        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError("Timeout")
            return "success"

        result = executor.execute_sync(operation)
        assert result == "success"
        assert call_count == 3


class TestRetryableError:
    """Tests for RetryableError exception."""

    def test_attributes(self):
        """Has required attributes."""
        err = RetryableError(
            "Network error",
            error_type=ErrorType.NETWORK_TIMEOUT,
            retry_after=30.0,
        )

        assert err.error_type == ErrorType.NETWORK_TIMEOUT
        assert err.retry_after == 30.0


class TestPermanentError:
    """Tests for PermanentError exception."""

    def test_attributes(self):
        """Has required attributes."""
        original = ValueError("Bad input")
        err = PermanentError(
            "Invalid request",
            error_type=ErrorType.BAD_REQUEST,
            suggestion="Check your input",
            original_error=original,
        )

        assert err.error_type == ErrorType.BAD_REQUEST
        assert err.suggestion == "Check your input"
        assert err.original_error == original
