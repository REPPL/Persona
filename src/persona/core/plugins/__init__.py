"""
Plugin system for Persona extensibility.

This module provides a unified plugin architecture for extending Persona
with custom formatters, loaders, providers, and validators via entry points.
"""

from persona.core.plugins.base import (
    PluginInfo,
    PluginRegistry,
    PluginType,
)
from persona.core.plugins.discovery import (
    discover_plugins,
    get_entry_point_group,
)
from persona.core.plugins.exceptions import (
    PluginError,
    PluginLoadError,
    PluginNotFoundError,
    PluginValidationError,
)
from persona.core.plugins.manager import PluginManager, get_plugin_manager

__all__ = [
    # Base classes
    "PluginInfo",
    "PluginRegistry",
    "PluginType",
    # Discovery
    "discover_plugins",
    "get_entry_point_group",
    # Exceptions
    "PluginError",
    "PluginNotFoundError",
    "PluginLoadError",
    "PluginValidationError",
    # Manager
    "PluginManager",
    "get_plugin_manager",
]
