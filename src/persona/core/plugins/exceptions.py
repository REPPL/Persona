"""
Exceptions for the plugin system.

This module defines custom exceptions for plugin-related errors.
"""


class PluginError(Exception):
    """Base exception for plugin-related errors."""

    pass


class PluginNotFoundError(PluginError):
    """Raised when a requested plugin cannot be found."""

    def __init__(self, plugin_name: str, plugin_type: str | None = None) -> None:
        """
        Initialise the exception.

        Args:
            plugin_name: Name of the plugin that was not found.
            plugin_type: Optional type of plugin (formatter, loader, etc.).
        """
        self.plugin_name = plugin_name
        self.plugin_type = plugin_type

        if plugin_type:
            message = f"Plugin '{plugin_name}' of type '{plugin_type}' not found"
        else:
            message = f"Plugin '{plugin_name}' not found"

        super().__init__(message)


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""

    def __init__(
        self,
        plugin_name: str,
        reason: str,
        original_error: Exception | None = None,
    ) -> None:
        """
        Initialise the exception.

        Args:
            plugin_name: Name of the plugin that failed to load.
            reason: Description of why the plugin failed to load.
            original_error: The original exception that caused the failure.
        """
        self.plugin_name = plugin_name
        self.reason = reason
        self.original_error = original_error

        message = f"Failed to load plugin '{plugin_name}': {reason}"
        if original_error:
            message += f" (caused by: {original_error})"

        super().__init__(message)


class PluginValidationError(PluginError):
    """Raised when a plugin fails validation."""

    def __init__(
        self,
        plugin_name: str,
        validation_errors: list[str],
    ) -> None:
        """
        Initialise the exception.

        Args:
            plugin_name: Name of the plugin that failed validation.
            validation_errors: List of validation error messages.
        """
        self.plugin_name = plugin_name
        self.validation_errors = validation_errors

        errors_str = "; ".join(validation_errors)
        message = f"Plugin '{plugin_name}' failed validation: {errors_str}"

        super().__init__(message)
