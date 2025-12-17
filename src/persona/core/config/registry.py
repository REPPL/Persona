"""
Global experiment registry for experiments outside ./experiments/.

This module provides registry management that allows experiments to exist
anywhere on the filesystem while being discoverable by name.
"""

from pathlib import Path
from typing import Optional

import yaml


class ExperimentRegistry:
    """
    Global registry mapping experiment names to filesystem paths.

    Stored at ~/.config/persona/experiments.yaml, enabling experiments
    to live anywhere on disk while remaining accessible by name.

    Example:
        ```python
        registry = ExperimentRegistry()

        # Register an experiment
        registry.register("client-study", "/projects/client/personas")

        # Get path
        path = registry.get_path("client-study")  # Returns Path object

        # List all registered
        for name, path in registry.list_experiments():
            print(f"{name}: {path}")

        # Unregister
        registry.unregister("client-study")
        ```

    Attributes:
        config_path: Path to the registry file.
    """

    DEFAULT_CONFIG_DIR = Path.home() / ".config" / "persona"
    CONFIG_FILE = "experiments.yaml"

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialise the registry.

        Args:
            config_dir: Directory for config files. Defaults to ~/.config/persona/
        """
        self._config_dir = Path(config_dir) if config_dir else self.DEFAULT_CONFIG_DIR
        self._experiments: Optional[dict[str, str]] = None

    @property
    def config_path(self) -> Path:
        """Path to the registry file."""
        return self._config_dir / self.CONFIG_FILE

    def _load(self) -> dict[str, str]:
        """Load registry from disk."""
        if self._experiments is not None:
            return self._experiments

        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = yaml.safe_load(f) or {}
                self._experiments = data.get("experiments", {})
            except (yaml.YAMLError, OSError):
                self._experiments = {}
        else:
            self._experiments = {}

        return self._experiments

    def _save(self) -> None:
        """Save registry to disk."""
        if self._experiments is None:
            return

        # Ensure directory exists
        self._config_dir.mkdir(parents=True, exist_ok=True)

        data = {"experiments": self._experiments}

        with open(self.config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=True)

    def register(
        self,
        name: str,
        path: Path | str,
        *,
        force: bool = False,
    ) -> None:
        """
        Register an experiment in the global registry.

        Args:
            name: Experiment name for lookup.
            path: Filesystem path to experiment directory.
            force: Overwrite existing registration.

        Raises:
            ValueError: If name already registered and force=False.
            FileNotFoundError: If path doesn't exist.
        """
        experiments = self._load()
        path = Path(path).resolve()

        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if name in experiments and not force:
            raise ValueError(
                f"Experiment '{name}' already registered at: {experiments[name]}\n"
                f"Use force=True to overwrite."
            )

        experiments[name] = str(path)
        self._save()

    def unregister(self, name: str) -> bool:
        """
        Remove an experiment from the registry.

        Note: This only removes the registry entry, not the actual files.

        Args:
            name: Experiment name to remove.

        Returns:
            True if removed, False if not found.
        """
        experiments = self._load()

        if name in experiments:
            del experiments[name]
            self._save()
            return True
        return False

    def get_path(self, name: str) -> Optional[Path]:
        """
        Get filesystem path for a registered experiment.

        Args:
            name: Experiment name.

        Returns:
            Path to experiment directory, or None if not registered.
        """
        experiments = self._load()
        path_str = experiments.get(name)

        if path_str:
            return Path(path_str)
        return None

    def is_registered(self, name: str) -> bool:
        """Check if an experiment is registered."""
        experiments = self._load()
        return name in experiments

    def list_experiments(self) -> list[tuple[str, Path]]:
        """
        List all registered experiments.

        Returns:
            List of (name, path) tuples, sorted by name.
        """
        experiments = self._load()
        return sorted(
            [(name, Path(path)) for name, path in experiments.items()],
            key=lambda x: x[0],
        )

    def validate(self) -> list[tuple[str, str]]:
        """
        Validate all registered experiments.

        Checks that registered paths still exist.

        Returns:
            List of (name, error) tuples for invalid registrations.
        """
        experiments = self._load()
        errors = []

        for name, path_str in experiments.items():
            path = Path(path_str)
            if not path.exists():
                errors.append((name, f"Path does not exist: {path}"))
            elif not path.is_dir():
                errors.append((name, f"Path is not a directory: {path}"))

        return errors

    def cleanup(self) -> list[str]:
        """
        Remove invalid registrations.

        Removes entries where the path no longer exists.

        Returns:
            List of removed experiment names.
        """
        experiments = self._load()
        removed = []

        for name, path_str in list(experiments.items()):
            path = Path(path_str)
            if not path.exists() or not path.is_dir():
                del experiments[name]
                removed.append(name)

        if removed:
            self._save()

        return removed


def get_registry(config_dir: Optional[Path] = None) -> ExperimentRegistry:
    """
    Get a registry instance.

    Args:
        config_dir: Optional custom config directory.

    Returns:
        ExperimentRegistry instance.
    """
    return ExperimentRegistry(config_dir)


def resolve_experiment_path(
    name: str,
    base_dir: Optional[Path] = None,
) -> Optional[Path]:
    """
    Resolve an experiment name to a path.

    Checks in order:
    1. Local experiments directory (./experiments/<name>)
    2. Custom base_dir if provided
    3. Global registry

    Args:
        name: Experiment name.
        base_dir: Optional local base directory.

    Returns:
        Path to experiment, or None if not found.
    """
    # Check local experiments directory
    local_path = (base_dir or Path("experiments")) / name
    if local_path.exists():
        return local_path

    # Check global registry
    registry = get_registry()
    return registry.get_path(name)
