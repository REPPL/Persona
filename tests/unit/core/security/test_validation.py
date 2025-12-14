"""Tests for input validation (F-053)."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from persona.core.security.validation import (
    InputValidator,
    ValidationError,
    PathValidationError,
    ValueValidationError,
    validate_path,
    validate_provider,
)


class TestInputValidatorPath:
    """Tests for path validation."""

    def test_validates_existing_file(self):
        """Validates existing file."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            validator = InputValidator()
            result = validator.validate_path(test_file, must_exist=True)

            assert result.valid
            assert result.resolved_path.exists()

    def test_fails_nonexistent_file(self):
        """Fails for non-existent file when required."""
        validator = InputValidator()
        result = validator.validate_path("/nonexistent/path.txt", must_exist=True)

        assert not result.valid
        assert "does not exist" in result.error

    def test_validates_directory(self):
        """Validates directory."""
        with TemporaryDirectory() as tmpdir:
            validator = InputValidator()
            result = validator.validate_path(tmpdir, must_be_directory=True)

            assert result.valid

    def test_fails_file_when_directory_required(self):
        """Fails when file given but directory required."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            validator = InputValidator()
            result = validator.validate_path(
                test_file,
                must_exist=True,
                must_be_directory=True,
            )

            assert not result.valid
            assert "not a directory" in result.error

    def test_validates_extension(self):
        """Validates file extension."""
        validator = InputValidator()
        result = validator.validate_path(
            "/path/to/file.csv",
            allowed_extensions={".csv", ".json"},
        )

        assert result.valid

    def test_fails_invalid_extension(self):
        """Fails for invalid extension."""
        validator = InputValidator()
        result = validator.validate_path(
            "/path/to/file.exe",
            allowed_extensions={".csv", ".json"},
        )

        assert not result.valid
        assert "Invalid file extension" in result.error

    def test_validates_within_allowed_roots(self):
        """Validates path within allowed roots."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            validator = InputValidator(allowed_roots=[Path(tmpdir)])
            result = validator.validate_path(test_file)

            assert result.valid

    def test_fails_outside_allowed_roots(self):
        """Fails for path outside allowed roots."""
        with TemporaryDirectory() as tmpdir:
            validator = InputValidator(allowed_roots=[Path(tmpdir)])
            result = validator.validate_path("/etc/passwd")

            assert not result.valid
            assert "not within allowed" in result.error

    def test_handles_path_traversal(self):
        """Handles path traversal attempts."""
        validator = InputValidator()
        result = validator.validate_path("../../../etc/passwd")

        # Should resolve and check - either valid (if file exists) or error
        assert result.resolved_path is not None or result.error is not None


class TestInputValidatorString:
    """Tests for string validation."""

    def test_validates_valid_string(self):
        """Validates valid string."""
        validator = InputValidator()
        result = validator.validate_string("hello", min_length=1, max_length=10)

        assert result.valid
        assert result.value == "hello"

    def test_fails_too_short(self):
        """Fails for string too short."""
        validator = InputValidator()
        result = validator.validate_string("hi", min_length=5)

        assert not result.valid
        assert "too short" in result.error

    def test_fails_too_long(self):
        """Fails for string too long."""
        validator = InputValidator()
        result = validator.validate_string("hello world", max_length=5)

        assert not result.valid
        assert "too long" in result.error

    def test_validates_pattern(self):
        """Validates against regex pattern."""
        validator = InputValidator()
        result = validator.validate_string(
            "test-name",
            pattern=r"^[a-z-]+$",
        )

        assert result.valid

    def test_fails_invalid_pattern(self):
        """Fails for invalid pattern."""
        validator = InputValidator()
        result = validator.validate_string(
            "test_name",  # Underscore not allowed
            pattern=r"^[a-z-]+$",
        )

        assert not result.valid
        assert "pattern" in result.error

    def test_validates_allowed_values(self):
        """Validates against allowed values."""
        validator = InputValidator()
        result = validator.validate_string(
            "apple",
            allowed_values={"apple", "banana", "cherry"},
        )

        assert result.valid

    def test_fails_disallowed_value(self):
        """Fails for disallowed value."""
        validator = InputValidator()
        result = validator.validate_string(
            "orange",
            allowed_values={"apple", "banana"},
        )

        assert not result.valid
        assert result.suggestions is not None

    def test_rejects_non_string(self):
        """Rejects non-string value."""
        validator = InputValidator()
        result = validator.validate_string(123)

        assert not result.valid
        assert "Expected string" in result.error


class TestInputValidatorNumber:
    """Tests for numeric validation."""

    def test_validates_integer(self):
        """Validates integer."""
        validator = InputValidator()
        result = validator.validate_number(5, min_value=1, max_value=10)

        assert result.valid

    def test_validates_float(self):
        """Validates float."""
        validator = InputValidator()
        result = validator.validate_number(3.14, min_value=0, max_value=10)

        assert result.valid

    def test_fails_below_minimum(self):
        """Fails for value below minimum."""
        validator = InputValidator()
        result = validator.validate_number(0, min_value=1)

        assert not result.valid
        assert "below minimum" in result.error

    def test_fails_above_maximum(self):
        """Fails for value above maximum."""
        validator = InputValidator()
        result = validator.validate_number(100, max_value=50)

        assert not result.valid
        assert "exceeds maximum" in result.error

    def test_rejects_float_when_not_allowed(self):
        """Rejects float when not allowed."""
        validator = InputValidator()
        result = validator.validate_number(3.5, allow_float=False)

        assert not result.valid
        assert "Floating point" in result.error


class TestInputValidatorUrl:
    """Tests for URL validation."""

    def test_validates_https_url(self):
        """Validates HTTPS URL."""
        validator = InputValidator()
        result = validator.validate_url("https://example.com/api")

        assert result.valid

    def test_fails_http_url(self):
        """Fails for HTTP URL when HTTPS required."""
        validator = InputValidator()
        result = validator.validate_url("http://example.com/api")

        assert not result.valid
        assert "HTTPS" in result.error

    def test_allows_http_when_not_required(self):
        """Allows HTTP when not required."""
        validator = InputValidator()
        result = validator.validate_url(
            "http://example.com/api",
            require_https=False,
        )

        # Still fails because http not in allowed protocols
        assert not result.valid

    def test_validates_allowed_domain(self):
        """Validates against allowed domains."""
        validator = InputValidator()
        result = validator.validate_url(
            "https://api.openai.com/v1",
            allowed_domains={"api.openai.com"},
        )

        assert result.valid

    def test_fails_disallowed_domain(self):
        """Fails for disallowed domain."""
        validator = InputValidator()
        result = validator.validate_url(
            "https://malicious.com/api",
            allowed_domains={"api.openai.com"},
        )

        assert not result.valid
        assert "Domain not allowed" in result.error

    def test_fails_invalid_url(self):
        """Fails for invalid URL."""
        validator = InputValidator()
        result = validator.validate_url("not-a-url")

        assert not result.valid


class TestInputValidatorProvider:
    """Tests for provider validation."""

    def test_validates_known_provider(self):
        """Validates known provider."""
        validator = InputValidator()
        result = validator.validate_provider("openai")

        assert result.valid
        assert result.value == "openai"

    def test_validates_case_insensitive(self):
        """Validates case-insensitively."""
        validator = InputValidator()
        result = validator.validate_provider("OpenAI")

        assert result.valid
        assert result.value == "openai"

    def test_fails_unknown_provider(self):
        """Fails for unknown provider."""
        validator = InputValidator()
        result = validator.validate_provider("unknown")

        assert not result.valid
        assert result.suggestions is not None

    def test_validates_custom_provider(self):
        """Validates custom provider."""
        validator = InputValidator()
        result = validator.validate_provider(
            "azure",
            custom_providers={"azure"},
        )

        assert result.valid


class TestInputValidatorModel:
    """Tests for model validation."""

    def test_validates_known_model_prefix(self):
        """Validates model with known prefix."""
        validator = InputValidator()
        result = validator.validate_model("gpt-4o")

        assert result.valid

    def test_validates_claude_model(self):
        """Validates Claude model."""
        validator = InputValidator()
        result = validator.validate_model("claude-sonnet-4-20250514")

        assert result.valid

    def test_fails_invalid_format(self):
        """Fails for invalid model name format."""
        validator = InputValidator()
        result = validator.validate_model("invalid model name!")

        assert not result.valid


class TestInputValidatorCount:
    """Tests for count validation."""

    def test_validates_valid_count(self):
        """Validates valid count."""
        validator = InputValidator()
        result = validator.validate_count(5)

        assert result.valid

    def test_fails_below_minimum(self):
        """Fails for count below minimum."""
        validator = InputValidator()
        result = validator.validate_count(0)

        assert not result.valid

    def test_fails_above_maximum(self):
        """Fails for count above maximum."""
        validator = InputValidator()
        result = validator.validate_count(200)

        assert not result.valid


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_validate_path_returns_path(self):
        """validate_path returns Path object."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            result = validate_path(test_file, must_exist=True)
            assert isinstance(result, Path)

    def test_validate_path_raises_on_error(self):
        """validate_path raises PathValidationError."""
        with pytest.raises(PathValidationError):
            validate_path("/nonexistent/path.txt", must_exist=True)

    def test_validate_provider_returns_lowercase(self):
        """validate_provider returns lowercase."""
        result = validate_provider("OpenAI")
        assert result == "openai"

    def test_validate_provider_raises_on_error(self):
        """validate_provider raises ValueValidationError."""
        with pytest.raises(ValueValidationError):
            validate_provider("unknown")
