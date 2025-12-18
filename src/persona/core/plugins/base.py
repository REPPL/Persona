"""
Base classes for the plugin system.

This module provides the foundational classes for plugin registration
and discovery across all extension points.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar


class PluginType(Enum):
    """Types of plugins supported by the system."""

    FORMATTER = "formatter"
    LOADER = "loader"
    PROVIDER = "provider"
    VALIDATOR = "validator"
    WORKFLOW = "workflow"


@dataclass
class PluginInfo:
    """
    Metadata about a registered plugin.

    This class stores information about a plugin including its name,
    description, type, and the actual class or callable that implements it.
    """

    name: str
    description: str
    plugin_type: PluginType
    plugin_class: type
    version: str = "1.0.0"
    author: str = ""
    enabled: bool = True
    builtin: bool = False
    entry_point: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert plugin info to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.plugin_type.value,
            "version": self.version,
            "author": self.author,
            "enabled": self.enabled,
            "builtin": self.builtin,
            "entry_point": self.entry_point,
            "metadata": self.metadata,
        }


T = TypeVar("T")


class PluginRegistry(ABC, Generic[T]):
    """
    Abstract base class for plugin registries.

    Provides a common interface for registering, discovering, and
    instantiating plugins of a specific type.

    Type Parameters:
        T: The base type that plugins must implement.

    Example:
        class FormatterRegistry(PluginRegistry[BaseFormatterV2]):
            plugin_type = PluginType.FORMATTER
            entry_point_group = "persona.formatters"
    """

    # Subclasses must define these
    plugin_type: PluginType
    entry_point_group: str

    def __init__(self) -> None:
        """Initialise the plugin registry."""
        self._plugins: dict[str, PluginInfo] = {}
        self._instances: dict[str, T] = {}
        self._discovery_done = False

    def register(
        self,
        name: str,
        plugin_class: type[T],
        description: str = "",
        version: str = "1.0.0",
        author: str = "",
        builtin: bool = False,
        **metadata: Any,
    ) -> None:
        """
        Register a plugin.

        Args:
            name: Unique name for the plugin.
            plugin_class: The plugin class.
            description: Human-readable description.
            version: Plugin version string.
            author: Plugin author.
            builtin: Whether this is a built-in plugin.
            **metadata: Additional metadata.

        Raises:
            ValueError: If name is already registered.
        """
        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' is already registered")

        self._plugins[name] = PluginInfo(
            name=name,
            description=description or f"{plugin_class.__name__}",
            plugin_type=self.plugin_type,
            plugin_class=plugin_class,
            version=version,
            author=author,
            enabled=True,
            builtin=builtin,
            metadata=metadata,
        )

    def register_entry_point(
        self,
        name: str,
        plugin_class: type[T],
        entry_point: str,
        description: str = "",
        version: str = "1.0.0",
        author: str = "",
        **metadata: Any,
    ) -> None:
        """
        Register a plugin discovered via entry point.

        Args:
            name: Unique name for the plugin.
            plugin_class: The plugin class.
            entry_point: The entry point string.
            description: Human-readable description.
            version: Plugin version string.
            author: Plugin author.
            **metadata: Additional metadata.
        """
        if name in self._plugins:
            # Skip if already registered (builtin takes precedence)
            return

        self._plugins[name] = PluginInfo(
            name=name,
            description=description or f"{plugin_class.__name__}",
            plugin_type=self.plugin_type,
            plugin_class=plugin_class,
            version=version,
            author=author,
            enabled=True,
            builtin=False,
            entry_point=entry_point,
            metadata=metadata,
        )

    def unregister(self, name: str) -> None:
        """
        Unregister a plugin.

        Args:
            name: Name of the plugin to remove.

        Raises:
            KeyError: If plugin not found.
        """
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found")

        del self._plugins[name]
        # Also remove cached instance if present
        if name in self._instances:
            del self._instances[name]

    def get(self, name: str, **kwargs: Any) -> T:
        """
        Get an instance of a plugin.

        Args:
            name: Name of the plugin.
            **kwargs: Arguments passed to plugin constructor.

        Returns:
            Plugin instance.

        Raises:
            KeyError: If plugin not found.
        """
        if name not in self._plugins:
            available = ", ".join(self.list_names())
            raise KeyError(f"Plugin '{name}' not found. Available: {available}")

        info = self._plugins[name]
        if not info.enabled:
            raise KeyError(f"Plugin '{name}' is disabled")

        return info.plugin_class(**kwargs)

    def get_cached(self, name: str, **kwargs: Any) -> T:
        """
        Get a cached instance of a plugin.

        Returns the same instance for repeated calls with the same name.

        Args:
            name: Name of the plugin.
            **kwargs: Arguments passed to plugin constructor (only used on first call).

        Returns:
            Plugin instance.
        """
        if name not in self._instances:
            self._instances[name] = self.get(name, **kwargs)
        return self._instances[name]

    def get_info(self, name: str) -> PluginInfo:
        """
        Get metadata about a plugin.

        Args:
            name: Name of the plugin.

        Returns:
            PluginInfo with plugin metadata.

        Raises:
            KeyError: If plugin not found.
        """
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found")
        return self._plugins[name]

    def list_names(self) -> list[str]:
        """
        List all registered plugin names.

        Returns:
            Sorted list of plugin names.
        """
        return sorted(self._plugins.keys())

    def list_enabled(self) -> list[str]:
        """
        List only enabled plugin names.

        Returns:
            Sorted list of enabled plugin names.
        """
        return sorted(name for name, info in self._plugins.items() if info.enabled)

    def list_builtin(self) -> list[str]:
        """
        List only built-in plugin names.

        Returns:
            Sorted list of built-in plugin names.
        """
        return sorted(name for name, info in self._plugins.items() if info.builtin)

    def list_external(self) -> list[str]:
        """
        List only external (non-builtin) plugin names.

        Returns:
            Sorted list of external plugin names.
        """
        return sorted(name for name, info in self._plugins.items() if not info.builtin)

    def list_all(self) -> list[PluginInfo]:
        """
        List all registered plugins with metadata.

        Returns:
            List of PluginInfo objects.
        """
        return [self._plugins[name] for name in self.list_names()]

    def has(self, name: str) -> bool:
        """
        Check if a plugin is registered.

        Args:
            name: Name to check.

        Returns:
            True if registered.
        """
        return name in self._plugins

    def enable(self, name: str) -> None:
        """
        Enable a plugin.

        Args:
            name: Name of the plugin to enable.

        Raises:
            KeyError: If plugin not found.
        """
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found")
        self._plugins[name].enabled = True

    def disable(self, name: str) -> None:
        """
        Disable a plugin.

        Args:
            name: Name of the plugin to disable.

        Raises:
            KeyError: If plugin not found.
        """
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found")
        self._plugins[name].enabled = False
        # Remove cached instance
        if name in self._instances:
            del self._instances[name]

    def clear_cache(self) -> None:
        """Clear all cached plugin instances."""
        self._instances.clear()

    @abstractmethod
    def _register_builtins(self) -> None:
        """
        Register built-in plugins.

        Subclasses must implement this to register their default plugins.
        """
        ...

    def discover_entry_points(self) -> int:
        """
        Discover and register plugins from entry points.

        Returns:
            Number of plugins discovered.
        """
        if self._discovery_done:
            return 0

        from persona.core.plugins.discovery import discover_plugins

        count = discover_plugins(self.entry_point_group, self)
        self._discovery_done = True
        return count

    def reload(self) -> None:
        """Reload all plugins, re-registering builtins and re-discovering entry points."""
        self._plugins.clear()
        self._instances.clear()
        self._discovery_done = False
        self._register_builtins()
        self.discover_entry_points()
