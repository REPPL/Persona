"""
Project registry management.

Provides a centralised registry for Persona projects, allowing them to be
referenced by name from anywhere on the filesystem. Supports both XDG
Base Directory Specification and legacy ~/.persona/ location.
"""

import os
from pathlib import Path
from typing import Any

import yaml

from persona.core.project.models import (
    GlobalDefaults,
    ProjectMetadata,
    ProjectRegistry,
)


def get_xdg_config_home() -> Path:
    """Get XDG_CONFIG_HOME directory.

    Returns:
        XDG_CONFIG_HOME if set, otherwise ~/.config
    """
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".config"


def get_registry_path() -> Path:
    """Get path to the project registry file.

    Checks in order:
    1. $XDG_CONFIG_HOME/persona/config.yaml (Linux standard)
    2. ~/.persona/config.yaml (legacy/macOS/Windows)

    Returns:
        Path to registry file (may not exist).
    """
    # Check XDG location first
    xdg_path = get_xdg_config_home() / "persona" / "config.yaml"
    if xdg_path.exists():
        return xdg_path

    # Fall back to legacy location
    legacy_path = Path.home() / ".persona" / "config.yaml"
    if legacy_path.exists():
        return legacy_path

    # If neither exists, prefer XDG on Linux, legacy elsewhere
    import sys

    if sys.platform.startswith("linux"):
        return xdg_path
    return legacy_path


def get_default_registry_path() -> Path:
    """Get default path for new registry file.

    Returns:
        Path where new registry should be created.
    """
    import sys

    if sys.platform.startswith("linux"):
        return get_xdg_config_home() / "persona" / "config.yaml"
    return Path.home() / ".persona" / "config.yaml"


class RegistryManager:
    """Manages the project registry.

    The registry stores:
    - Global defaults (provider, model, count)
    - Project name to path mappings

    Example registry file:
    ```yaml
    version: "1.0"
    defaults:
      provider: anthropic
      model: claude-sonnet-4-20250514
      count: 3
    projects:
      my-research: /path/to/my-research
      demo: /path/to/examples/demo-project
    ```
    """

    def __init__(self, registry_path: Path | None = None):
        """Initialise registry manager.

        Args:
            registry_path: Optional path to registry file. If not provided,
                           uses get_registry_path() to locate it.
        """
        self._registry_path = registry_path
        self._registry: ProjectRegistry | None = None

    @property
    def registry_path(self) -> Path:
        """Get path to registry file."""
        if self._registry_path is None:
            self._registry_path = get_registry_path()
        return self._registry_path

    def _load(self) -> ProjectRegistry:
        """Load registry from disk.

        Returns:
            ProjectRegistry instance (empty if file doesn't exist).
        """
        if self.registry_path.exists():
            try:
                with open(self.registry_path) as f:
                    data = yaml.safe_load(f) or {}
                return ProjectRegistry.model_validate(data)
            except Exception:
                # Return empty registry on error
                return ProjectRegistry()
        return ProjectRegistry()

    def _save(self) -> None:
        """Save registry to disk."""
        if self._registry is None:
            return

        # Ensure directory exists
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Build YAML with comments
        content = self._generate_yaml_content()

        with open(self.registry_path, "w") as f:
            f.write(content)

    def _generate_yaml_content(self) -> str:
        """Generate YAML content with helpful comments.

        Returns:
            YAML string with comments.
        """
        if self._registry is None:
            self._registry = ProjectRegistry()

        lines = [
            "# Persona Project Registry",
            "# See: https://github.com/REPPL/Persona",
            "",
            f'version: "{self._registry.version}"',
            "",
            "# Global defaults for all projects",
            "defaults:",
            f"  provider: {self._registry.defaults.provider}",
        ]

        if self._registry.defaults.model:
            lines.append(f"  model: {self._registry.defaults.model}")
        else:
            lines.append("  # model: claude-sonnet-4-20250514  # Uses provider default")

        lines.append(f"  count: {self._registry.defaults.count}")
        lines.append("")
        lines.append("# Registered projects (name: path)")
        lines.append("projects:")

        if self._registry.projects:
            for name, path in sorted(self._registry.projects.items()):
                lines.append(f"  {name}: {path}")
        else:
            lines.append("  # my-project: /path/to/my-project")

        lines.append("")

        return "\n".join(lines)

    def get_registry(self) -> ProjectRegistry:
        """Get the project registry.

        Returns:
            ProjectRegistry instance.
        """
        if self._registry is None:
            self._registry = self._load()
        return self._registry

    def get_defaults(self) -> GlobalDefaults:
        """Get global defaults.

        Returns:
            GlobalDefaults instance.
        """
        return self.get_registry().defaults

    def set_defaults(
        self,
        *,
        provider: str | None = None,
        model: str | None = None,
        count: int | None = None,
    ) -> None:
        """Update global defaults.

        Args:
            provider: Default LLM provider.
            model: Default model.
            count: Default persona count.
        """
        registry = self.get_registry()

        if provider is not None:
            registry.defaults.provider = provider
        if model is not None:
            registry.defaults.model = model
        if count is not None:
            registry.defaults.count = count

        self._save()

    def get_project_path(self, name: str) -> Path | None:
        """Get path to a registered project.

        Args:
            name: Project name.

        Returns:
            Path to project directory, or None if not registered.
        """
        return self.get_registry().get_project_path(name)

    def register_project(self, name: str, path: Path) -> None:
        """Register a project in the registry.

        Args:
            name: Project name (must be unique).
            path: Absolute path to project directory.

        Raises:
            ValueError: If project with this name already exists.
        """
        registry = self.get_registry()

        if name in registry.projects:
            raise ValueError(f"Project '{name}' is already registered")

        registry.register(name, path)
        self._save()

    def unregister_project(self, name: str) -> bool:
        """Remove a project from the registry.

        Args:
            name: Project name.

        Returns:
            True if project was unregistered, False if not found.
        """
        registry = self.get_registry()
        result = registry.unregister(name)
        if result:
            self._save()
        return result

    def update_project_path(self, name: str, path: Path) -> None:
        """Update path for an existing project.

        Args:
            name: Project name.
            path: New absolute path.

        Raises:
            ValueError: If project is not registered.
        """
        registry = self.get_registry()

        if name not in registry.projects:
            raise ValueError(f"Project '{name}' is not registered")

        registry.projects[name] = str(path.resolve())
        self._save()

    def list_projects(self) -> list[tuple[str, Path]]:
        """List all registered projects.

        Returns:
            List of (name, path) tuples sorted by name.
        """
        return sorted(self.get_registry().list_projects())

    def project_exists(self, name: str) -> bool:
        """Check if a project is registered.

        Args:
            name: Project name.

        Returns:
            True if project is registered.
        """
        return name in self.get_registry().projects

    def init_registry(self, *, force: bool = False) -> Path:
        """Initialise registry file with defaults.

        Args:
            force: Overwrite existing registry.

        Returns:
            Path to created registry file.

        Raises:
            FileExistsError: If registry exists and force is False.
        """
        # Use the provided registry path if set, otherwise use default
        path = self._registry_path or get_default_registry_path()

        if path.exists() and not force:
            raise FileExistsError(f"Registry already exists: {path}")

        self._registry_path = path
        self._registry = ProjectRegistry()
        self._save()

        return path


# Module-level instance for convenience
_registry_manager: RegistryManager | None = None


def get_registry_manager() -> RegistryManager:
    """Get the global registry manager instance.

    Returns:
        RegistryManager singleton.
    """
    global _registry_manager
    if _registry_manager is None:
        _registry_manager = RegistryManager()
    return _registry_manager


def get_project_path(name: str) -> Path | None:
    """Get path to a registered project.

    Convenience function using the global registry manager.

    Args:
        name: Project name.

    Returns:
        Path to project directory, or None if not registered.
    """
    return get_registry_manager().get_project_path(name)


def list_registered_projects() -> list[tuple[str, Path]]:
    """List all registered projects.

    Convenience function using the global registry manager.

    Returns:
        List of (name, path) tuples.
    """
    return get_registry_manager().list_projects()
