"""Tests for plugin exceptions."""

import pytest

from persona.core.plugins.exceptions import (
    PluginError,
    PluginNotFoundError,
    PluginLoadError,
    PluginValidationError,
)


class TestPluginError:
    """Tests for PluginError base exception."""

    def test_plugin_error_is_exception(self) -> None:
        """Should be an Exception subclass."""
        error = PluginError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"


class TestPluginNotFoundError:
    """Tests for PluginNotFoundError."""

    def test_creates_with_name_only(self) -> None:
        """Should create error with plugin name."""
        error = PluginNotFoundError("my-plugin")

        assert error.plugin_name == "my-plugin"
        assert error.plugin_type is None
        assert "my-plugin" in str(error)
        assert "not found" in str(error)

    def test_creates_with_name_and_type(self) -> None:
        """Should create error with name and type."""
        error = PluginNotFoundError("my-plugin", "formatter")

        assert error.plugin_name == "my-plugin"
        assert error.plugin_type == "formatter"
        assert "my-plugin" in str(error)
        assert "formatter" in str(error)

    def test_is_plugin_error(self) -> None:
        """Should be a PluginError subclass."""
        error = PluginNotFoundError("test")
        assert isinstance(error, PluginError)


class TestPluginLoadError:
    """Tests for PluginLoadError."""

    def test_creates_with_name_and_reason(self) -> None:
        """Should create error with name and reason."""
        error = PluginLoadError("my-plugin", "import failed")

        assert error.plugin_name == "my-plugin"
        assert error.reason == "import failed"
        assert error.original_error is None
        assert "my-plugin" in str(error)
        assert "import failed" in str(error)

    def test_creates_with_original_error(self) -> None:
        """Should include original error."""
        original = ImportError("No module named 'foo'")
        error = PluginLoadError("my-plugin", "import failed", original)

        assert error.original_error is original
        assert "caused by" in str(error)
        assert "No module named" in str(error)

    def test_is_plugin_error(self) -> None:
        """Should be a PluginError subclass."""
        error = PluginLoadError("test", "reason")
        assert isinstance(error, PluginError)


class TestPluginValidationError:
    """Tests for PluginValidationError."""

    def test_creates_with_single_error(self) -> None:
        """Should create error with single validation error."""
        error = PluginValidationError("my-plugin", ["Missing required method"])

        assert error.plugin_name == "my-plugin"
        assert len(error.validation_errors) == 1
        assert "Missing required method" in str(error)

    def test_creates_with_multiple_errors(self) -> None:
        """Should create error with multiple validation errors."""
        errors = ["Error 1", "Error 2", "Error 3"]
        error = PluginValidationError("my-plugin", errors)

        assert len(error.validation_errors) == 3
        error_str = str(error)
        assert "Error 1" in error_str
        assert "Error 2" in error_str
        assert "Error 3" in error_str

    def test_is_plugin_error(self) -> None:
        """Should be a PluginError subclass."""
        error = PluginValidationError("test", ["error"])
        assert isinstance(error, PluginError)
