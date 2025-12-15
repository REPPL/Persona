"""
Entry point discovery for plugins.

This module provides functionality for discovering plugins via
Python entry points (setuptools entry_points / importlib.metadata).
"""

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from persona.core.plugins.base import PluginRegistry

# Entry point group names
ENTRY_POINT_GROUPS = {
    "formatter": "persona.formatters",
    "loader": "persona.loaders",
    "provider": "persona.providers",
    "validator": "persona.validators",
    "workflow": "persona.workflows",
}


def get_entry_point_group(plugin_type: str) -> str:
    """
    Get the entry point group name for a plugin type.

    Args:
        plugin_type: Type of plugin (formatter, loader, etc.).

    Returns:
        Entry point group name.

    Raises:
        ValueError: If plugin type is not recognised.
    """
    if plugin_type not in ENTRY_POINT_GROUPS:
        raise ValueError(
            f"Unknown plugin type: {plugin_type}. "
            f"Valid types: {', '.join(ENTRY_POINT_GROUPS.keys())}"
        )
    return ENTRY_POINT_GROUPS[plugin_type]


def discover_plugins(group: str, registry: "PluginRegistry") -> int:
    """
    Discover and register plugins from entry points.

    Uses importlib.metadata for Python 3.10+ or the backport for older versions.

    Args:
        group: Entry point group name (e.g., "persona.formatters").
        registry: The registry to register discovered plugins to.

    Returns:
        Number of plugins discovered and registered.
    """
    count = 0

    # Use importlib.metadata (Python 3.10+)
    if sys.version_info >= (3, 10):
        from importlib.metadata import entry_points

        eps = entry_points(group=group)
    else:
        # Fallback for older Python (shouldn't happen with Python 3.12 requirement)
        from importlib.metadata import entry_points as get_entry_points

        all_eps = get_entry_points()
        eps = all_eps.get(group, [])

    for ep in eps:
        try:
            # Load the plugin class
            plugin_class = ep.load()

            # Extract metadata if available
            description = ""
            version = "1.0.0"
            author = ""

            # Check for plugin metadata attributes
            if hasattr(plugin_class, "__plugin_description__"):
                description = plugin_class.__plugin_description__
            if hasattr(plugin_class, "__plugin_version__"):
                version = plugin_class.__plugin_version__
            if hasattr(plugin_class, "__plugin_author__"):
                author = plugin_class.__plugin_author__

            # Register the plugin
            registry.register_entry_point(
                name=ep.name,
                plugin_class=plugin_class,
                entry_point=f"{group}:{ep.name}",
                description=description,
                version=version,
                author=author,
            )
            count += 1

        except Exception as e:
            # Log but don't fail on individual plugin load errors
            # This allows the system to continue even if one plugin fails
            import warnings

            warnings.warn(
                f"Failed to load plugin '{ep.name}' from entry point "
                f"'{group}': {e}",
                RuntimeWarning,
            )

    return count


def list_entry_points(group: str) -> list[str]:
    """
    List available entry points for a group without loading them.

    Args:
        group: Entry point group name.

    Returns:
        List of entry point names.
    """
    if sys.version_info >= (3, 10):
        from importlib.metadata import entry_points

        eps = entry_points(group=group)
    else:
        from importlib.metadata import entry_points as get_entry_points

        all_eps = get_entry_points()
        eps = all_eps.get(group, [])

    return [ep.name for ep in eps]


def get_entry_point_info(group: str, name: str) -> dict | None:
    """
    Get information about a specific entry point.

    Args:
        group: Entry point group name.
        name: Entry point name.

    Returns:
        Dictionary with entry point info, or None if not found.
    """
    if sys.version_info >= (3, 10):
        from importlib.metadata import entry_points

        eps = entry_points(group=group)
    else:
        from importlib.metadata import entry_points as get_entry_points

        all_eps = get_entry_points()
        eps = all_eps.get(group, [])

    for ep in eps:
        if ep.name == name:
            return {
                "name": ep.name,
                "value": ep.value,
                "group": group,
            }

    return None
