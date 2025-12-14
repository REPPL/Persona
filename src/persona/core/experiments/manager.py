"""
Experiment management for persona generation.

This module provides the ExperimentManager class for creating,
listing, and managing experiments.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ExperimentConfig:
    """
    Configuration for an experiment.

    Attributes:
        name: Experiment name.
        description: Optional description.
        provider: Default LLM provider.
        model: Default model identifier.
        workflow: Workflow to use.
        count: Default persona count.
        complexity: Generation complexity.
        detail_level: Output detail level.
    """

    name: str
    description: str = ""
    provider: str = "anthropic"
    model: str | None = None
    workflow: str = "default"
    count: int = 3
    complexity: str = "moderate"
    detail_level: str = "standard"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperimentConfig":
        """Create config from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            provider=data.get("provider", "anthropic"),
            model=data.get("model"),
            workflow=data.get("workflow", "default"),
            count=data.get("count", 3),
            complexity=data.get("complexity", "moderate"),
            detail_level=data.get("detail_level", "standard"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "provider": self.provider,
            "model": self.model,
            "workflow": self.workflow,
            "count": self.count,
            "complexity": self.complexity,
            "detail_level": self.detail_level,
        }


@dataclass
class Experiment:
    """
    A persona generation experiment.

    Experiments organise multiple generation runs with shared
    configuration and data.

    Attributes:
        path: Path to experiment directory.
        config: Experiment configuration.
        created_at: When the experiment was created.
    """

    path: Path
    config: ExperimentConfig
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def name(self) -> str:
        """Return experiment name."""
        return self.config.name

    @property
    def data_dir(self) -> Path:
        """Return path to data directory."""
        return self.path / "data"

    @property
    def outputs_dir(self) -> Path:
        """Return path to outputs directory."""
        return self.path / "outputs"

    def list_outputs(self) -> list[Path]:
        """List all output directories."""
        if not self.outputs_dir.exists():
            return []
        return sorted([
            d for d in self.outputs_dir.iterdir()
            if d.is_dir() and (d / "metadata.json").exists()
        ])


class ExperimentManager:
    """
    Manager for creating and organising experiments.

    Experiments are stored in a base directory with the structure:

    ```
    experiments/
    └── my-experiment/
        ├── config.yaml       # Experiment settings
        ├── data/             # Input data files
        └── outputs/          # Generation outputs
            └── YYYYMMDD_HHMMSS/
    ```

    Example:
        manager = ExperimentManager("./experiments")
        exp = manager.create("user-research-2024")
        manager.list_experiments()
    """

    CONFIG_FILE = "config.yaml"

    def __init__(self, base_dir: str | Path = "./experiments") -> None:
        """
        Initialise the experiment manager.

        Args:
            base_dir: Base directory for experiments.
        """
        self._base_dir = Path(base_dir)

    def create(
        self,
        name: str,
        description: str = "",
        **config_kwargs: Any,
    ) -> Experiment:
        """
        Create a new experiment.

        Args:
            name: Experiment name (used as directory name).
            description: Optional description.
            **config_kwargs: Additional configuration options.

        Returns:
            The created Experiment.

        Raises:
            ValueError: If experiment with name already exists.
        """
        # Sanitise name for filesystem
        safe_name = self._sanitise_name(name)
        exp_path = self._base_dir / safe_name

        if exp_path.exists():
            raise ValueError(f"Experiment already exists: {name}")

        # Create directory structure
        exp_path.mkdir(parents=True)
        (exp_path / "data").mkdir()
        (exp_path / "outputs").mkdir()

        # Create config
        config = ExperimentConfig(
            name=name,
            description=description,
            **config_kwargs,
        )

        # Save config
        self._save_config(exp_path, config)

        # Create README
        self._create_readme(exp_path, config)

        return Experiment(
            path=exp_path,
            config=config,
            created_at=datetime.now(),
        )

    def load(self, name: str) -> Experiment:
        """
        Load an existing experiment.

        Args:
            name: Experiment name.

        Returns:
            The loaded Experiment.

        Raises:
            FileNotFoundError: If experiment doesn't exist.
        """
        safe_name = self._sanitise_name(name)
        exp_path = self._base_dir / safe_name

        if not exp_path.exists():
            raise FileNotFoundError(f"Experiment not found: {name}")

        config = self._load_config(exp_path)

        return Experiment(
            path=exp_path,
            config=config,
        )

    def list_experiments(self) -> list[str]:
        """
        List all experiment names.

        Returns:
            List of experiment names.
        """
        if not self._base_dir.exists():
            return []

        experiments = []
        for item in self._base_dir.iterdir():
            if item.is_dir() and (item / self.CONFIG_FILE).exists():
                experiments.append(item.name)

        return sorted(experiments)

    def delete(self, name: str, confirm: bool = False) -> bool:
        """
        Delete an experiment.

        Args:
            name: Experiment name.
            confirm: Whether deletion is confirmed.

        Returns:
            True if deleted, False otherwise.

        Raises:
            FileNotFoundError: If experiment doesn't exist.
        """
        if not confirm:
            return False

        safe_name = self._sanitise_name(name)
        exp_path = self._base_dir / safe_name

        if not exp_path.exists():
            raise FileNotFoundError(f"Experiment not found: {name}")

        import shutil
        shutil.rmtree(exp_path)
        return True

    def exists(self, name: str) -> bool:
        """Check if an experiment exists."""
        safe_name = self._sanitise_name(name)
        exp_path = self._base_dir / safe_name
        return exp_path.exists() and (exp_path / self.CONFIG_FILE).exists()

    def _sanitise_name(self, name: str) -> str:
        """Sanitise name for filesystem use."""
        # Replace spaces with hyphens, remove other problematic characters
        safe = name.lower().replace(" ", "-")
        safe = "".join(c for c in safe if c.isalnum() or c in "-_")
        return safe or "unnamed"

    def _save_config(self, exp_path: Path, config: ExperimentConfig) -> None:
        """Save experiment configuration."""
        config_path = exp_path / self.CONFIG_FILE
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False)

    def _load_config(self, exp_path: Path) -> ExperimentConfig:
        """Load experiment configuration."""
        config_path = exp_path / self.CONFIG_FILE
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return ExperimentConfig.from_dict(data or {})

    def _create_readme(self, exp_path: Path, config: ExperimentConfig) -> None:
        """Create experiment README file."""
        readme_content = f"""# Experiment: {config.name}

{config.description or 'No description provided.'}

## Configuration

- **Provider**: {config.provider}
- **Model**: {config.model or 'Default'}
- **Workflow**: {config.workflow}
- **Persona Count**: {config.count}
- **Complexity**: {config.complexity}
- **Detail Level**: {config.detail_level}

## Structure

```
{exp_path.name}/
├── config.yaml     # Experiment configuration
├── data/           # Place input data files here
├── outputs/        # Generation outputs
└── README.md       # This file
```

## Usage

Add your data files to the `data/` directory, then run:

```bash
persona generate --experiment {exp_path.name}
```
"""
        readme_path = exp_path / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")
