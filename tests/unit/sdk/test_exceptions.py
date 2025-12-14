"""Tests for SDK exceptions."""

import pytest

from persona.sdk.exceptions import (
    PersonaError,
    ConfigurationError,
    ProviderError,
    ValidationError,
    DataError,
    BudgetExceededError,
    RateLimitError,
    GenerationError,
)


class TestPersonaError:
    """Tests for PersonaError base class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = PersonaError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.details == {}

    def test_error_with_details(self):
        """Test error with details."""
        error = PersonaError("Error", details={"key": "value"})
        assert "key=value" in str(error)
        assert error.details == {"key": "value"}

    def test_error_inheritance(self):
        """Test that PersonaError inherits from Exception."""
        error = PersonaError("Test")
        assert isinstance(error, Exception)


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_basic_configuration_error(self):
        """Test basic configuration error."""
        error = ConfigurationError("Invalid config")
        assert "Invalid config" in str(error)
        assert error.field is None
        assert error.value is None

    def test_configuration_error_with_field(self):
        """Test configuration error with field."""
        error = ConfigurationError("Invalid value", field="provider", value="invalid")
        assert error.field == "provider"
        assert error.value == "invalid"
        assert "field=provider" in str(error)
        assert "value=invalid" in str(error)

    def test_inherits_from_persona_error(self):
        """Test inheritance from PersonaError."""
        error = ConfigurationError("Test")
        assert isinstance(error, PersonaError)


class TestValidationError:
    """Tests for ValidationError."""

    def test_basic_validation_error(self):
        """Test basic validation error."""
        error = ValidationError("Validation failed")
        assert "Validation failed" in str(error)
        assert error.errors == []

    def test_validation_error_with_errors(self):
        """Test validation error with error list."""
        errors = [
            {"loc": ["field1"], "msg": "required"},
            {"loc": ["field2"], "msg": "invalid type"},
        ]
        error = ValidationError("Validation failed", errors=errors)
        assert error.errors == errors
        assert "error_count=2" in str(error)


class TestDataError:
    """Tests for DataError."""

    def test_basic_data_error(self):
        """Test basic data error."""
        error = DataError("File not found")
        assert "File not found" in str(error)
        assert error.path is None
        assert error.format is None

    def test_data_error_with_path(self):
        """Test data error with path."""
        error = DataError("Cannot read", path="/path/to/file.csv")
        assert error.path == "/path/to/file.csv"
        assert "path=/path/to/file.csv" in str(error)

    def test_data_error_with_format(self):
        """Test data error with format."""
        error = DataError("Unsupported", path="/file.xyz", format="xyz")
        assert error.format == "xyz"
        assert "format=xyz" in str(error)


class TestProviderError:
    """Tests for ProviderError."""

    def test_basic_provider_error(self):
        """Test basic provider error."""
        error = ProviderError("API call failed")
        assert "API call failed" in str(error)
        assert error.provider is None
        assert error.status_code is None

    def test_provider_error_with_provider(self):
        """Test provider error with provider name."""
        error = ProviderError("Failed", provider="anthropic")
        assert error.provider == "anthropic"
        assert "provider=anthropic" in str(error)

    def test_provider_error_with_status_code(self):
        """Test provider error with status code."""
        error = ProviderError("Failed", provider="openai", status_code=500)
        assert error.status_code == 500
        assert "status_code=500" in str(error)


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_basic_rate_limit_error(self):
        """Test basic rate limit error."""
        error = RateLimitError("Rate limited")
        assert "Rate limited" in str(error)
        assert error.status_code == 429

    def test_rate_limit_error_with_retry(self):
        """Test rate limit error with retry_after."""
        error = RateLimitError("Slow down", provider="anthropic", retry_after=30.0)
        assert error.retry_after == 30.0
        assert error.provider == "anthropic"
        assert "retry_after=30.0" in str(error)

    def test_inherits_from_provider_error(self):
        """Test inheritance from ProviderError."""
        error = RateLimitError("Test")
        assert isinstance(error, ProviderError)
        assert isinstance(error, PersonaError)


class TestBudgetExceededError:
    """Tests for BudgetExceededError."""

    def test_basic_budget_error(self):
        """Test basic budget exceeded error."""
        error = BudgetExceededError("Budget exceeded")
        assert "Budget exceeded" in str(error)
        assert error.budget is None
        assert error.estimated_cost is None

    def test_budget_error_with_amounts(self):
        """Test budget error with amounts."""
        error = BudgetExceededError(
            "Would exceed budget",
            budget=10.0,
            estimated_cost=15.0,
        )
        assert error.budget == 10.0
        assert error.estimated_cost == 15.0
        assert "$10.00" in str(error)
        assert "$15.00" in str(error)


class TestGenerationError:
    """Tests for GenerationError."""

    def test_basic_generation_error(self):
        """Test basic generation error."""
        error = GenerationError("Generation failed")
        assert "Generation failed" in str(error)
        assert error.stage is None
        assert error.raw_response is None

    def test_generation_error_with_stage(self):
        """Test generation error with stage."""
        error = GenerationError("Failed at parsing", stage="parsing")
        assert error.stage == "parsing"
        assert "stage=parsing" in str(error)

    def test_generation_error_with_response(self):
        """Test generation error with raw response."""
        error = GenerationError(
            "Invalid response",
            stage="parsing",
            raw_response="<invalid>",
        )
        assert error.raw_response == "<invalid>"


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_errors_inherit_from_persona_error(self):
        """Test that all SDK errors inherit from PersonaError."""
        errors = [
            ConfigurationError("test"),
            ValidationError("test"),
            DataError("test"),
            ProviderError("test"),
            RateLimitError("test"),
            BudgetExceededError("test"),
            GenerationError("test"),
        ]

        for error in errors:
            assert isinstance(error, PersonaError)

    def test_catch_all_with_persona_error(self):
        """Test catching all errors with PersonaError."""
        def raise_config_error():
            raise ConfigurationError("test")

        def raise_data_error():
            raise DataError("test")

        def raise_generation_error():
            raise GenerationError("test")

        for func in [raise_config_error, raise_data_error, raise_generation_error]:
            with pytest.raises(PersonaError):
                func()

    def test_specific_catch(self):
        """Test catching specific error types."""
        def raise_rate_limit():
            raise RateLimitError("rate limited")

        # Can catch as RateLimitError
        with pytest.raises(RateLimitError):
            raise_rate_limit()

        # Can catch as ProviderError
        with pytest.raises(ProviderError):
            raise_rate_limit()

        # Can catch as PersonaError
        with pytest.raises(PersonaError):
            raise_rate_limit()
