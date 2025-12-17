"""
Experiment context providing unified path management and operations.

This module provides the ExperimentContext class, a semantic model for
accessing experiment paths, configuration, and operations in a DRY manner.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

from persona.core.experiments.history import RunHistoryManager, RunInfo


@dataclass
class ExperimentContext:
    """
    Unified context for experiment paths and operations.

    Provides semantic access to experiment directories, configuration,
    and run history without scattered path construction.

    Example:
        ```python
        # Load by name
        ctx = ExperimentContext.load("my-research")

        # Access paths
        data_files = list(ctx.data_dir.glob("*.csv"))
        output_path = ctx.outputs_dir / "20241217_123456"

        # Record runs
        ctx.record_run(
            provider="anthropic",
            model="claude-sonnet",
            persona_count=3,
            tokens={"input": 100, "output": 200},
            output_dir="20241217_123456",
        )

        # List runs
        for run in ctx.list_runs(status="success"):
            print(f"{run.run_id}: {run.persona_count} personas")
        ```

    Attributes:
        root: Path to experiment directory.
        name: Name of the experiment.
    """

    root: Path
    name: str
    _history_manager: Optional[RunHistoryManager] = field(
        default=None, repr=False, compare=False
    )

    # Path properties

    @property
    def config_path(self) -> Path:
        """Path to experiment config.yaml file."""
        return self.root / "config.yaml"

    @property
    def data_dir(self) -> Path:
        """Path to experiment data directory."""
        return self.root / "data"

    @property
    def outputs_dir(self) -> Path:
        """Path to experiment outputs directory."""
        return self.root / "outputs"

    @property
    def history_path(self) -> Path:
        """Path to experiment history.json file."""
        return self.root / "history.json"

    @property
    def readme_path(self) -> Path:
        """Path to experiment README.md file."""
        return self.root / "README.md"

    # Status properties

    @property
    def exists(self) -> bool:
        """Whether the experiment directory exists."""
        return self.root.exists()

    @property
    def has_config(self) -> bool:
        """Whether the experiment has a config.yaml file."""
        return self.config_path.exists()

    @property
    def has_data(self) -> bool:
        """Whether the experiment has any data files."""
        if not self.data_dir.exists():
            return False
        return any(self.data_dir.iterdir())

    @property
    def has_outputs(self) -> bool:
        """Whether the experiment has any output directories."""
        if not self.outputs_dir.exists():
            return False
        return any(self.outputs_dir.iterdir())

    @property
    def has_history(self) -> bool:
        """Whether the experiment has a history.json file."""
        return self.history_path.exists()

    # Configuration

    def load_config(self) -> dict[str, Any]:
        """
        Load experiment configuration.

        Returns:
            Configuration dictionary, or empty dict if no config file.
        """
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError):
            return {}

    def save_config(self, config: dict[str, Any]) -> None:
        """
        Save experiment configuration.

        Args:
            config: Configuration dictionary to save.
        """
        with open(self.config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys).
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        config = self.load_config()
        keys = key.split(".")
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    # Data operations

    def list_data_files(self, pattern: str = "*") -> list[Path]:
        """
        List data files in the experiment.

        Args:
            pattern: Glob pattern to match files.

        Returns:
            List of matching file paths.
        """
        if not self.data_dir.exists():
            return []
        return sorted(self.data_dir.glob(pattern))

    def get_data_summary(self) -> dict[str, Any]:
        """
        Get summary of experiment data.

        Returns:
            Dictionary with file count, total size, and file types.
        """
        files = self.list_data_files("**/*")
        files = [f for f in files if f.is_file()]

        total_size = sum(f.stat().st_size for f in files)
        extensions = {}
        for f in files:
            ext = f.suffix.lower() or "(no extension)"
            extensions[ext] = extensions.get(ext, 0) + 1

        return {
            "file_count": len(files),
            "total_size_bytes": total_size,
            "extensions": extensions,
        }

    # Output operations

    def list_outputs(self) -> list[Path]:
        """
        List output directories.

        Returns:
            List of output directory paths, sorted by name (typically timestamp).
        """
        if not self.outputs_dir.exists():
            return []

        return sorted(
            [d for d in self.outputs_dir.iterdir() if d.is_dir()],
            reverse=True,  # Most recent first
        )

    def get_latest_output(self) -> Optional[Path]:
        """
        Get the most recent output directory.

        Returns:
            Path to latest output directory, or None if no outputs.
        """
        outputs = self.list_outputs()
        return outputs[0] if outputs else None

    # Run history operations

    @property
    def _history(self) -> RunHistoryManager:
        """Get or create history manager."""
        if self._history_manager is None:
            self._history_manager = RunHistoryManager(self.root, self.name)
        return self._history_manager

    def record_run(
        self,
        provider: str,
        model: str,
        persona_count: int,
        tokens: dict[str, int],
        output_dir: str,
        data_source: str = "",
        config: Optional[dict[str, Any]] = None,
        status: str = "success",
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> RunInfo:
        """
        Record a generation run in history.

        Args:
            provider: LLM provider name.
            model: Model identifier.
            persona_count: Number of personas generated.
            tokens: Token usage ({"input": N, "output": M}).
            output_dir: Relative path to output directory.
            data_source: Path to input data.
            config: Generation configuration.
            status: Run status.
            started_at: When the run started.
            completed_at: When the run ended.

        Returns:
            The recorded RunInfo.
        """
        return self._history.record_run(
            provider=provider,
            model=model,
            persona_count=persona_count,
            tokens=tokens,
            output_dir=output_dir,
            data_source=data_source,
            config=config,
            status=status,  # type: ignore
            started_at=started_at,
            completed_at=completed_at,
        )

    def list_runs(
        self,
        *,
        status: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[RunInfo]:
        """
        List runs with optional filtering.

        Args:
            status: Filter by status.
            provider: Filter by provider.
            model: Filter by model.
            limit: Maximum number of runs to return.

        Returns:
            List of matching RunInfo objects.
        """
        return self._history.list_runs(
            status=status,
            provider=provider,
            model=model,
            limit=limit,
        )

    def get_run(self, run_id: str) -> Optional[RunInfo]:
        """
        Get a specific run by ID.

        Args:
            run_id: Run identifier.

        Returns:
            RunInfo if found, None otherwise.
        """
        return self._history.get_run(run_id)

    def get_run_statistics(self) -> dict[str, Any]:
        """
        Get aggregate statistics for all runs.

        Returns:
            Dictionary with run counts, persona counts, and token totals.
        """
        runs = self.list_runs()

        if not runs:
            return {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "total_personas": 0,
                "total_tokens": 0,
            }

        return {
            "total_runs": len(runs),
            "successful_runs": sum(1 for r in runs if r.status == "success"),
            "failed_runs": sum(1 for r in runs if r.status == "failed"),
            "total_personas": sum(r.persona_count for r in runs),
            "total_tokens": sum(r.tokens.total for r in runs),
        }

    # Factory methods

    @classmethod
    def from_path(cls, path: Path) -> "ExperimentContext":
        """
        Create context from filesystem path.

        Args:
            path: Path to experiment directory.

        Returns:
            ExperimentContext instance.

        Raises:
            FileNotFoundError: If path doesn't exist.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Experiment not found: {path}")

        return cls(root=path, name=path.name)

    @classmethod
    def load(
        cls,
        name: str,
        base_dir: Optional[Path] = None,
    ) -> "ExperimentContext":
        """
        Load experiment by name.

        Looks for experiment in:
        1. base_dir/<name> (if base_dir provided)
        2. ./experiments/<name> (default)
        3. Global registry (future)

        Args:
            name: Experiment name.
            base_dir: Base directory for experiments.

        Returns:
            ExperimentContext instance.

        Raises:
            FileNotFoundError: If experiment not found.
        """
        # Try specified base_dir or default
        search_dir = base_dir or Path("experiments")
        experiment_path = search_dir / name

        if experiment_path.exists():
            return cls.from_path(experiment_path)

        # Future: Check global registry here

        raise FileNotFoundError(
            f"Experiment not found: {name}\n"
            f"Searched in: {search_dir}"
        )

    @classmethod
    def create(
        cls,
        name: str,
        base_dir: Optional[Path] = None,
        description: str = "",
        provider: str = "anthropic",
        count: int = 3,
        copy_global_config: bool = True,
    ) -> "ExperimentContext":
        """
        Create a new experiment.

        Args:
            name: Experiment name.
            base_dir: Base directory for experiments.
            description: Experiment description.
            provider: Default provider.
            count: Default persona count.
            copy_global_config: Whether to copy global config as template.

        Returns:
            ExperimentContext for the new experiment.

        Raises:
            ValueError: If experiment already exists.
        """
        search_dir = base_dir or Path("experiments")
        experiment_path = search_dir / name

        if experiment_path.exists():
            raise ValueError(f"Experiment already exists: {name}")

        # Create directory structure
        experiment_path.mkdir(parents=True)
        (experiment_path / "data").mkdir()
        (experiment_path / "outputs").mkdir()

        # Create config.yaml
        config = {
            "name": name,
            "description": description,
            "defaults": {
                "provider": provider,
                "count": count,
            },
        }

        # Optionally merge with global config template
        if copy_global_config:
            global_config_path = Path.home() / ".config" / "persona" / "config.yaml"
            if global_config_path.exists():
                try:
                    with open(global_config_path) as f:
                        global_config = yaml.safe_load(f) or {}
                    # Copy relevant sections as commented examples
                    if "defaults" in global_config:
                        config["defaults"] = {
                            **global_config.get("defaults", {}),
                            **config["defaults"],
                        }
                except (yaml.YAMLError, OSError):
                    pass

        with open(experiment_path / "config.yaml", "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        # Create README.md
        readme_content = f"""# {name}

{description or "Experiment for persona generation."}

## Data

Add your research data files to the `data/` directory.

Supported formats:
- CSV (.csv)
- JSON (.json)
- YAML (.yaml, .yml)
- Text (.txt)

## Usage

```bash
# Generate personas
persona generate --from {name} --experiment {name}

# View runs
persona experiment runs {name}
```

## Configuration

Edit `config.yaml` to set default provider, model, and other options.
"""

        with open(experiment_path / "README.md", "w") as f:
            f.write(readme_content)

        return cls(root=experiment_path, name=name)
