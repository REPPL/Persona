"""
Plugin manager for coordinating all plugin registries.

This module provides a central manager that coordinates plugin discovery
and access across all extension points.
"""

from typing import Any

from persona.core.plugins.base import PluginInfo, PluginRegistry, PluginType
from persona.core.plugins.exceptions import PluginNotFoundError


class PluginManager:
    """
    Central manager for all plugin registries.

    Provides a unified interface for discovering, listing, and accessing
    plugins across all extension points.

    Example:
        manager = PluginManager()
        manager.discover_all()

        # List all formatters
        for info in manager.list_plugins(PluginType.FORMATTER):
            print(f"{info.name}: {info.description}")

        # Get a specific plugin
        formatter = manager.get_plugin(PluginType.FORMATTER, "json")
    """

    def __init__(self) -> None:
        """Initialise the plugin manager."""
        self._registries: dict[PluginType, PluginRegistry] = {}
        self._discovery_done = False

    def register_registry(
        self,
        plugin_type: PluginType,
        registry: PluginRegistry,
    ) -> None:
        """
        Register a plugin registry.

        Args:
            plugin_type: Type of plugins the registry handles.
            registry: The registry instance.
        """
        self._registries[plugin_type] = registry

    def get_registry(self, plugin_type: PluginType) -> PluginRegistry:
        """
        Get a plugin registry by type.

        Args:
            plugin_type: Type of plugins.

        Returns:
            The registry for that plugin type.

        Raises:
            KeyError: If no registry is registered for that type.
        """
        if plugin_type not in self._registries:
            raise KeyError(f"No registry for plugin type: {plugin_type.value}")
        return self._registries[plugin_type]

    def discover_all(self) -> dict[PluginType, int]:
        """
        Discover plugins from all registered registries.

        Returns:
            Dictionary mapping plugin type to number of plugins discovered.
        """
        if self._discovery_done:
            return {}

        results = {}
        for plugin_type, registry in self._registries.items():
            count = registry.discover_entry_points()
            results[plugin_type] = count

        self._discovery_done = True
        return results

    def list_plugins(
        self,
        plugin_type: PluginType | None = None,
        enabled_only: bool = False,
        builtin_only: bool = False,
        external_only: bool = False,
    ) -> list[PluginInfo]:
        """
        List plugins, optionally filtered by type or status.

        Args:
            plugin_type: Optional type to filter by.
            enabled_only: Only return enabled plugins.
            builtin_only: Only return built-in plugins.
            external_only: Only return external plugins.

        Returns:
            List of PluginInfo objects.
        """
        if plugin_type is not None:
            if plugin_type not in self._registries:
                return []
            registries = [self._registries[plugin_type]]
        else:
            registries = list(self._registries.values())

        plugins = []
        for registry in registries:
            for info in registry.list_all():
                if enabled_only and not info.enabled:
                    continue
                if builtin_only and not info.builtin:
                    continue
                if external_only and info.builtin:
                    continue
                plugins.append(info)

        return sorted(plugins, key=lambda p: (p.plugin_type.value, p.name))

    def get_plugin(
        self,
        plugin_type: PluginType,
        name: str,
        **kwargs: Any,
    ) -> Any:
        """
        Get a plugin instance by type and name.

        Args:
            plugin_type: Type of plugin.
            name: Name of the plugin.
            **kwargs: Arguments passed to plugin constructor.

        Returns:
            Plugin instance.

        Raises:
            PluginNotFoundError: If plugin not found.
        """
        try:
            registry = self.get_registry(plugin_type)
            return registry.get(name, **kwargs)
        except KeyError as e:
            raise PluginNotFoundError(name, plugin_type.value) from e

    def get_plugin_info(
        self,
        plugin_type: PluginType,
        name: str,
    ) -> PluginInfo:
        """
        Get plugin metadata by type and name.

        Args:
            plugin_type: Type of plugin.
            name: Name of the plugin.

        Returns:
            PluginInfo with plugin metadata.

        Raises:
            PluginNotFoundError: If plugin not found.
        """
        try:
            registry = self.get_registry(plugin_type)
            return registry.get_info(name)
        except KeyError as e:
            raise PluginNotFoundError(name, plugin_type.value) from e

    def has_plugin(self, plugin_type: PluginType, name: str) -> bool:
        """
        Check if a plugin exists.

        Args:
            plugin_type: Type of plugin.
            name: Name of the plugin.

        Returns:
            True if plugin exists.
        """
        if plugin_type not in self._registries:
            return False
        return self._registries[plugin_type].has(name)

    def enable_plugin(self, plugin_type: PluginType, name: str) -> None:
        """
        Enable a plugin.

        Args:
            plugin_type: Type of plugin.
            name: Name of the plugin.

        Raises:
            PluginNotFoundError: If plugin not found.
        """
        try:
            registry = self.get_registry(plugin_type)
            registry.enable(name)
        except KeyError as e:
            raise PluginNotFoundError(name, plugin_type.value) from e

    def disable_plugin(self, plugin_type: PluginType, name: str) -> None:
        """
        Disable a plugin.

        Args:
            plugin_type: Type of plugin.
            name: Name of the plugin.

        Raises:
            PluginNotFoundError: If plugin not found.
        """
        try:
            registry = self.get_registry(plugin_type)
            registry.disable(name)
        except KeyError as e:
            raise PluginNotFoundError(name, plugin_type.value) from e

    def count_plugins(self, plugin_type: PluginType | None = None) -> int:
        """
        Count registered plugins.

        Args:
            plugin_type: Optional type to count.

        Returns:
            Number of plugins.
        """
        if plugin_type is not None:
            if plugin_type not in self._registries:
                return 0
            return len(self._registries[plugin_type].list_names())

        return sum(len(registry.list_names()) for registry in self._registries.values())

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of all registered plugins.

        Returns:
            Dictionary with plugin counts by type and status.
        """
        summary = {
            "total": 0,
            "enabled": 0,
            "disabled": 0,
            "builtin": 0,
            "external": 0,
            "by_type": {},
        }

        for plugin_type, registry in self._registries.items():
            type_summary = {
                "total": len(registry.list_names()),
                "enabled": len(registry.list_enabled()),
                "builtin": len(registry.list_builtin()),
                "external": len(registry.list_external()),
            }
            type_summary["disabled"] = type_summary["total"] - type_summary["enabled"]

            summary["by_type"][plugin_type.value] = type_summary
            summary["total"] += type_summary["total"]
            summary["enabled"] += type_summary["enabled"]
            summary["disabled"] += type_summary["disabled"]
            summary["builtin"] += type_summary["builtin"]
            summary["external"] += type_summary["external"]

        return summary

    def reload_all(self) -> None:
        """Reload all registries."""
        self._discovery_done = False
        for registry in self._registries.values():
            registry.reload()


# Global plugin manager instance
_global_manager: PluginManager | None = None


def get_plugin_manager() -> PluginManager:
    """
    Get the global plugin manager.

    Returns:
        The global PluginManager instance.
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = PluginManager()
        _initialise_registries(_global_manager)
    return _global_manager


def _initialise_registries(manager: PluginManager) -> None:
    """
    Initialise the default registries.

    Args:
        manager: The plugin manager to initialise.
    """
    # Import registries here to avoid circular imports
    from persona.core.plugins.registries import (
        get_formatter_registry,
        get_loader_registry,
        get_provider_registry,
        get_validator_registry,
    )

    manager.register_registry(PluginType.FORMATTER, get_formatter_registry())
    manager.register_registry(PluginType.LOADER, get_loader_registry())
    manager.register_registry(PluginType.PROVIDER, get_provider_registry())
    manager.register_registry(PluginType.VALIDATOR, get_validator_registry())

    # Discover entry points
    manager.discover_all()
