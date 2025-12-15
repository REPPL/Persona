"""Tests for persona.core.errors module."""

import pytest

from persona.core.errors import (
    PersonaError,
    ConfigurationError,
    MissingAPIKeyError,
    InvalidConfigError,
    ProviderNotFoundError,
    ModelNotConfiguredError,
    DataError,
    DataLoadError,
    DataFormatError,
    EmptyDataError,
    EncodingError,
    ProviderError,
    APIError,
    RateLimitError,
    AuthenticationError,
    ModelNotFoundError,
    ContextLengthError,
    TimeoutError,
    ValidationError,
    InvalidPersonaError,
    SchemaValidationError,
    MissingFieldError,
    BudgetError,
    CostLimitExceededError,
    TokenLimitExceededError,
    InternalError,
    ConfigCorruptedError,
)


class TestPersonaError:
    """Tests for base PersonaError."""

    def test_default_message(self):
        """Test error with default message."""
        error = PersonaError()
        assert "An error occurred" in str(error)
        assert error.code == "PERSONA-900-001"

    def test_custom_message(self):
        """Test error with custom message."""
        error = PersonaError("Custom error message")
        assert str(error) == "Custom error message"

    def test_with_details(self):
        """Test error with details."""
        error = PersonaError("Test", key="value")
        assert error.details == {"key": "value"}


class TestConfigurationErrors:
    """Tests for configuration error types."""

    def test_missing_api_key_error(self):
        """Test MissingAPIKeyError."""
        error = MissingAPIKeyError("anthropic")
        assert error.provider == "anthropic"
        assert error.env_var == "ANTHROPIC_API_KEY"
        assert "anthropic" in str(error)
        assert "ANTHROPIC_API_KEY" in str(error)
        assert error.code == "PERSONA-100-001"

    def test_missing_api_key_custom_env_var(self):
        """Test MissingAPIKeyError with custom env var."""
        error = MissingAPIKeyError("custom", "CUSTOM_KEY")
        assert error.env_var == "CUSTOM_KEY"
        assert "CUSTOM_KEY" in str(error)

    def test_invalid_config_error(self):
        """Test InvalidConfigError."""
        error = InvalidConfigError("syntax error", "/path/config.yaml")
        assert "syntax error" in str(error)
        assert error.path == "/path/config.yaml"
        assert error.code == "PERSONA-100-002"

    def test_provider_not_found_error(self):
        """Test ProviderNotFoundError."""
        error = ProviderNotFoundError("unknown", ["anthropic", "openai"])
        assert error.provider == "unknown"
        assert error.available == ["anthropic", "openai"]
        assert "unknown" in str(error)
        assert "anthropic" in str(error)
        assert error.code == "PERSONA-100-003"

    def test_model_not_configured_error(self):
        """Test ModelNotConfiguredError."""
        error = ModelNotConfiguredError("gpt-5", "openai")
        assert error.model == "gpt-5"
        assert error.provider == "openai"
        assert "gpt-5" in str(error)
        assert error.code == "PERSONA-100-004"


class TestDataErrors:
    """Tests for data error types."""

    def test_data_load_error(self):
        """Test DataLoadError."""
        error = DataLoadError("/path/data.csv", "file not found")
        assert error.path == "/path/data.csv"
        assert error.reason == "file not found"
        assert "file not found" in str(error)
        assert error.code == "PERSONA-200-001"

    def test_data_format_error(self):
        """Test DataFormatError."""
        error = DataFormatError("xlsx", "/path/file.xlsx")
        assert error.format_name == "xlsx"
        assert error.path == "/path/file.xlsx"
        assert "xlsx" in str(error)
        assert error.code == "PERSONA-200-002"

    def test_empty_data_error(self):
        """Test EmptyDataError."""
        error = EmptyDataError("/path/empty/")
        assert error.path == "/path/empty/"
        assert "empty" in str(error)
        assert error.code == "PERSONA-200-003"

    def test_encoding_error(self):
        """Test EncodingError."""
        error = EncodingError("/path/file.txt", "latin-1")
        assert error.path == "/path/file.txt"
        assert error.encoding == "latin-1"
        assert "latin-1" in str(error)
        assert error.code == "PERSONA-200-004"


class TestProviderErrors:
    """Tests for provider error types."""

    def test_api_error(self):
        """Test APIError."""
        error = APIError("server error", 500)
        assert error.status_code == 500
        assert "500" in str(error)
        assert "server error" in str(error)
        assert error.code == "PERSONA-300-001"

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError(30)
        assert error.retry_after == 30
        assert "30s" in str(error)
        assert error.code == "PERSONA-300-002"

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("openai", "invalid key")
        assert error.provider == "openai"
        assert error.reason == "invalid key"
        assert "openai" in str(error)
        assert error.code == "PERSONA-300-003"

    def test_model_not_found_error(self):
        """Test ModelNotFoundError."""
        error = ModelNotFoundError("gpt-5", "openai")
        assert error.model == "gpt-5"
        assert error.provider == "openai"
        assert "gpt-5" in str(error)
        assert error.code == "PERSONA-300-004"

    def test_context_length_error(self):
        """Test ContextLengthError."""
        error = ContextLengthError(200000, 128000, "gpt-4")
        assert error.tokens == 200000
        assert error.max_tokens == 128000
        assert error.model == "gpt-4"
        assert "200000" in str(error)
        assert "128000" in str(error)
        assert error.code == "PERSONA-300-005"

    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError(60)
        assert error.timeout == 60
        assert "60s" in str(error)
        assert error.code == "PERSONA-300-006"


class TestValidationErrors:
    """Tests for validation error types."""

    def test_invalid_persona_error(self):
        """Test InvalidPersonaError."""
        error = InvalidPersonaError("missing goals", "Test User")
        assert "missing goals" in str(error)
        assert "Test User" in str(error)
        assert error.persona_name == "Test User"
        assert error.code == "PERSONA-400-001"

    def test_schema_validation_error(self):
        """Test SchemaValidationError."""
        error = SchemaValidationError("age", "int", "str")
        assert error.field == "age"
        assert error.expected == "int"
        assert error.got == "str"
        assert "age" in str(error)
        assert error.code == "PERSONA-400-002"

    def test_missing_field_error(self):
        """Test MissingFieldError."""
        error = MissingFieldError("goals", "Test User")
        assert error.field == "goals"
        assert error.persona_name == "Test User"
        assert "goals" in str(error)
        assert error.code == "PERSONA-400-003"


class TestBudgetErrors:
    """Tests for budget error types."""

    def test_cost_limit_exceeded_error(self):
        """Test CostLimitExceededError."""
        error = CostLimitExceededError(15.50, 10.00)
        assert error.estimated_cost == 15.50
        assert error.limit == 10.00
        assert "15.5" in str(error)
        assert "10.0" in str(error)
        assert error.code == "PERSONA-500-001"

    def test_token_limit_exceeded_error(self):
        """Test TokenLimitExceededError."""
        error = TokenLimitExceededError(150000, 100000, "input")
        assert error.count == 150000
        assert error.limit == 100000
        assert error.token_type == "input"
        assert "150000" in str(error)
        assert error.code == "PERSONA-500-002"


class TestInternalErrors:
    """Tests for internal error types."""

    def test_internal_error(self):
        """Test InternalError."""
        error = InternalError("unexpected state")
        assert "unexpected state" in str(error)
        assert error.code == "PERSONA-900-001"

    def test_config_corrupted_error(self):
        """Test ConfigCorruptedError."""
        error = ConfigCorruptedError("/path/config.yaml", "invalid YAML")
        assert error.path == "/path/config.yaml"
        assert error.reason == "invalid YAML"
        assert "corrupted" in str(error).lower()
        assert error.code == "PERSONA-900-002"


class TestErrorHierarchy:
    """Tests for error inheritance hierarchy."""

    def test_configuration_error_is_persona_error(self):
        """ConfigurationError inherits from PersonaError."""
        error = ConfigurationError()
        assert isinstance(error, PersonaError)

    def test_data_error_is_persona_error(self):
        """DataError inherits from PersonaError."""
        error = DataError()
        assert isinstance(error, PersonaError)

    def test_provider_error_is_persona_error(self):
        """ProviderError inherits from PersonaError."""
        error = ProviderError()
        assert isinstance(error, PersonaError)

    def test_validation_error_is_persona_error(self):
        """ValidationError inherits from PersonaError."""
        error = ValidationError()
        assert isinstance(error, PersonaError)

    def test_budget_error_is_persona_error(self):
        """BudgetError inherits from PersonaError."""
        error = BudgetError()
        assert isinstance(error, PersonaError)

    def test_missing_api_key_is_configuration_error(self):
        """MissingAPIKeyError inherits from ConfigurationError."""
        error = MissingAPIKeyError("test")
        assert isinstance(error, ConfigurationError)

    def test_rate_limit_is_provider_error(self):
        """RateLimitError inherits from ProviderError."""
        error = RateLimitError()
        assert isinstance(error, ProviderError)

    def test_catch_by_category(self):
        """Test catching errors by category."""
        errors = [
            MissingAPIKeyError("test"),
            DataLoadError("/path"),
            RateLimitError(30),
            InvalidPersonaError("test"),
            CostLimitExceededError(10, 5),
        ]

        config_errors = [e for e in errors if isinstance(e, ConfigurationError)]
        data_errors = [e for e in errors if isinstance(e, DataError)]
        provider_errors = [e for e in errors if isinstance(e, ProviderError)]
        validation_errors = [e for e in errors if isinstance(e, ValidationError)]
        budget_errors = [e for e in errors if isinstance(e, BudgetError)]

        assert len(config_errors) == 1
        assert len(data_errors) == 1
        assert len(provider_errors) == 1
        assert len(validation_errors) == 1
        assert len(budget_errors) == 1
