"""
Experiment management for persona generation.

This module provides the ExperimentManager class for creating,
listing, and managing experiments, and the ExperimentEditor class
for editing experiment configurations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
import copy
import shutil

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

    def update_config(self, name: str, config: ExperimentConfig) -> None:
        """
        Update an experiment's configuration.

        Args:
            name: Experiment name.
            config: New configuration.
        """
        safe_name = self._sanitise_name(name)
        exp_path = self._base_dir / safe_name

        if not exp_path.exists():
            raise FileNotFoundError(f"Experiment not found: {name}")

        self._save_config(exp_path, config)


@dataclass
class EditHistoryEntry:
    """
    A single edit history entry.

    Attributes:
        timestamp: When the edit was made.
        field: The field that was changed.
        old_value: Previous value.
        new_value: New value.
        action: Type of edit action.
    """

    timestamp: datetime
    field: str
    old_value: Any
    new_value: Any
    action: str = "update"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "field": self.field,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "action": self.action,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EditHistoryEntry":
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            field=data["field"],
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            action=data.get("action", "update"),
        )


class ExperimentEditor:
    """
    Editor for modifying experiment configurations.

    Supports direct field updates, data source management,
    and maintains edit history for rollback.

    Example:
        manager = ExperimentManager("./experiments")
        editor = ExperimentEditor(manager)
        editor.set_field("my-experiment", "count", 5)
        editor.add_source("my-experiment", Path("./new-data.csv"))
        editor.rollback("my-experiment")
    """

    HISTORY_FILE = "edit_history.yaml"

    def __init__(self, manager: ExperimentManager) -> None:
        """
        Initialise the experiment editor.

        Args:
            manager: ExperimentManager instance.
        """
        self._manager = manager

    def set_field(
        self,
        name: str,
        field_path: str,
        value: Any,
        *,
        save_history: bool = True,
    ) -> ExperimentConfig:
        """
        Set a field in the experiment configuration.

        Args:
            name: Experiment name.
            field_path: Dot-separated field path (e.g., "generation.model").
            value: New value for the field.
            save_history: Whether to save edit history.

        Returns:
            Updated ExperimentConfig.

        Raises:
            FileNotFoundError: If experiment doesn't exist.
            ValueError: If field path is invalid.
        """
        experiment = self._manager.load(name)
        config = experiment.config
        old_config = copy.deepcopy(config)

        # Parse field path (handle nested paths like "generation.model")
        parts = field_path.split(".")
        field_name = parts[-1]

        # For now, we only support top-level fields
        if len(parts) > 1:
            # Map nested paths to config fields
            field_mapping = {
                "generation.model": "model",
                "generation.provider": "provider",
                "generation.count": "count",
                "generation.complexity": "complexity",
                "generation.detail_level": "detail_level",
                "workflow": "workflow",
            }
            if field_path in field_mapping:
                field_name = field_mapping[field_path]
            else:
                raise ValueError(f"Invalid field path: {field_path}")

        # Validate field exists
        valid_fields = {
            "name", "description", "provider", "model",
            "workflow", "count", "complexity", "detail_level"
        }
        if field_name not in valid_fields:
            raise ValueError(
                f"Invalid field: {field_name}. "
                f"Valid fields: {', '.join(sorted(valid_fields))}"
            )

        # Type coercion
        if field_name == "count":
            value = int(value)

        # Get old value for history
        old_value = getattr(config, field_name)

        # Update field
        setattr(config, field_name, value)

        # Save updated config
        self._manager.update_config(name, config)

        # Save history
        if save_history:
            self._add_history_entry(
                experiment.path,
                EditHistoryEntry(
                    timestamp=datetime.now(),
                    field=field_path,
                    old_value=old_value,
                    new_value=value,
                    action="update",
                ),
            )

        return config

    def set_fields(
        self,
        name: str,
        updates: dict[str, Any],
    ) -> ExperimentConfig:
        """
        Set multiple fields at once.

        Args:
            name: Experiment name.
            updates: Dictionary of field_path -> value.

        Returns:
            Updated ExperimentConfig.
        """
        config = None
        for field_path, value in updates.items():
            config = self.set_field(name, field_path, value)
        return config

    def add_source(self, name: str, source_path: Path) -> Path:
        """
        Add a data source to the experiment.

        Args:
            name: Experiment name.
            source_path: Path to the source file to add.

        Returns:
            Path to the copied file in the experiment.

        Raises:
            FileNotFoundError: If experiment or source doesn't exist.
            ValueError: If source file already exists in experiment.
        """
        experiment = self._manager.load(name)

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        dest_path = experiment.data_dir / source_path.name

        if dest_path.exists():
            raise ValueError(f"Source already exists: {source_path.name}")

        # Copy file
        shutil.copy2(source_path, dest_path)

        # Save history
        self._add_history_entry(
            experiment.path,
            EditHistoryEntry(
                timestamp=datetime.now(),
                field="data_sources",
                old_value=None,
                new_value=str(source_path.name),
                action="add_source",
            ),
        )

        return dest_path

    def remove_source(self, name: str, source_name: str) -> bool:
        """
        Remove a data source from the experiment.

        Args:
            name: Experiment name.
            source_name: Name of the source file to remove.

        Returns:
            True if removed successfully.

        Raises:
            FileNotFoundError: If experiment or source doesn't exist.
        """
        experiment = self._manager.load(name)

        source_path = experiment.data_dir / source_name

        if not source_path.exists():
            raise FileNotFoundError(f"Source not found: {source_name}")

        # Remove file
        source_path.unlink()

        # Save history
        self._add_history_entry(
            experiment.path,
            EditHistoryEntry(
                timestamp=datetime.now(),
                field="data_sources",
                old_value=str(source_name),
                new_value=None,
                action="remove_source",
            ),
        )

        return True

    def list_sources(self, name: str) -> list[str]:
        """
        List all data sources in an experiment.

        Args:
            name: Experiment name.

        Returns:
            List of source file names.
        """
        experiment = self._manager.load(name)

        if not experiment.data_dir.exists():
            return []

        return sorted([
            f.name for f in experiment.data_dir.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ])

    def get_history(self, name: str) -> list[EditHistoryEntry]:
        """
        Get edit history for an experiment.

        Args:
            name: Experiment name.

        Returns:
            List of edit history entries.
        """
        experiment = self._manager.load(name)
        history_path = experiment.path / self.HISTORY_FILE

        if not history_path.exists():
            return []

        with open(history_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "history" not in data:
            return []

        return [
            EditHistoryEntry.from_dict(entry)
            for entry in data["history"]
        ]

    def rollback(self, name: str, steps: int = 1) -> ExperimentConfig | None:
        """
        Rollback the last N edits.

        Args:
            name: Experiment name.
            steps: Number of edits to rollback.

        Returns:
            Updated config, or None if nothing to rollback.

        Raises:
            ValueError: If trying to rollback more steps than available.
        """
        history = self.get_history(name)

        if not history:
            return None

        if steps > len(history):
            raise ValueError(
                f"Cannot rollback {steps} steps. "
                f"Only {len(history)} edits available."
            )

        # Get the edits to rollback (most recent first)
        to_rollback = history[-steps:]

        experiment = self._manager.load(name)
        config = experiment.config

        # Reverse each edit
        for entry in reversed(to_rollback):
            if entry.action == "update":
                # Map field path back to config field
                parts = entry.field.split(".")
                field_name = parts[-1]

                field_mapping = {
                    "generation.model": "model",
                    "generation.provider": "provider",
                    "generation.count": "count",
                    "generation.complexity": "complexity",
                    "generation.detail_level": "detail_level",
                    "workflow": "workflow",
                }
                if entry.field in field_mapping:
                    field_name = field_mapping[entry.field]

                setattr(config, field_name, entry.old_value)

            elif entry.action == "add_source":
                # Remove the added source
                source_path = experiment.data_dir / entry.new_value
                if source_path.exists():
                    source_path.unlink()

            elif entry.action == "remove_source":
                # Cannot restore removed sources - just log it
                pass

        # Save updated config
        self._manager.update_config(name, config)

        # Update history (remove rolled back entries)
        self._save_history(experiment.path, history[:-steps])

        return config

    def clear_history(self, name: str) -> None:
        """
        Clear edit history for an experiment.

        Args:
            name: Experiment name.
        """
        experiment = self._manager.load(name)
        history_path = experiment.path / self.HISTORY_FILE

        if history_path.exists():
            history_path.unlink()

    def _add_history_entry(
        self,
        exp_path: Path,
        entry: EditHistoryEntry,
    ) -> None:
        """Add an entry to edit history."""
        history_path = exp_path / self.HISTORY_FILE

        if history_path.exists():
            with open(history_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        if "history" not in data:
            data["history"] = []

        data["history"].append(entry.to_dict())

        with open(history_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False)

    def _save_history(
        self,
        exp_path: Path,
        history: list[EditHistoryEntry],
    ) -> None:
        """Save complete history."""
        history_path = exp_path / self.HISTORY_FILE

        data = {
            "history": [entry.to_dict() for entry in history]
        }

        with open(history_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False)


@dataclass
class RunMetadata:
    """
    Metadata for a single generation run.

    Attributes:
        run_id: Unique run identifier.
        timestamp: When the run started.
        model: Model used for generation.
        provider: Provider used.
        persona_count: Number of personas generated.
        input_tokens: Total input tokens used.
        output_tokens: Total output tokens used.
        cost: Estimated cost in USD.
        status: Run status (completed, failed, cancelled).
        duration_seconds: Run duration in seconds.
        output_dir: Relative path to output directory.
    """

    run_id: int
    timestamp: datetime
    model: str
    provider: str
    persona_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    status: str = "completed"
    duration_seconds: float = 0.0
    output_dir: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp.isoformat(),
            "model": self.model,
            "provider": self.provider,
            "persona_count": self.persona_count,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "output_dir": self.output_dir,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunMetadata":
        """Create from dictionary."""
        return cls(
            run_id=data.get("run_id", 0),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            model=data.get("model", "unknown"),
            provider=data.get("provider", "unknown"),
            persona_count=data.get("persona_count", 0),
            input_tokens=data.get("input_tokens", 0),
            output_tokens=data.get("output_tokens", 0),
            cost=data.get("cost", 0.0),
            status=data.get("status", "unknown"),
            duration_seconds=data.get("duration_seconds", 0.0),
            output_dir=data.get("output_dir", ""),
        )


@dataclass
class RunStatistics:
    """
    Aggregate statistics for experiment runs.

    Attributes:
        total_runs: Total number of runs.
        completed_runs: Number of completed runs.
        failed_runs: Number of failed runs.
        total_personas: Total personas generated.
        total_cost: Total cost in USD.
        total_input_tokens: Total input tokens.
        total_output_tokens: Total output tokens.
        avg_cost_per_run: Average cost per run.
        avg_personas_per_run: Average personas per run.
        models_used: Set of models used.
        providers_used: Set of providers used.
    """

    total_runs: int = 0
    completed_runs: int = 0
    failed_runs: int = 0
    total_personas: int = 0
    total_cost: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    avg_cost_per_run: float = 0.0
    avg_personas_per_run: float = 0.0
    models_used: list[str] = field(default_factory=list)
    providers_used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_runs": self.total_runs,
            "completed_runs": self.completed_runs,
            "failed_runs": self.failed_runs,
            "total_personas": self.total_personas,
            "total_cost": self.total_cost,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "avg_cost_per_run": self.avg_cost_per_run,
            "avg_personas_per_run": self.avg_personas_per_run,
            "models_used": self.models_used,
            "providers_used": self.providers_used,
        }


class RunHistory:
    """
    Manager for experiment run history.

    Tracks all generation runs for an experiment with metadata,
    provides statistics, and supports run comparison.

    Example:
        manager = ExperimentManager("./experiments")
        history = RunHistory(manager)
        history.record_run("my-experiment", run_metadata)
        runs = history.get_runs("my-experiment")
        stats = history.get_statistics("my-experiment")
    """

    HISTORY_FILE = "run_history.yaml"

    def __init__(self, manager: ExperimentManager) -> None:
        """
        Initialise run history.

        Args:
            manager: ExperimentManager instance.
        """
        self._manager = manager

    def record_run(
        self,
        name: str,
        model: str,
        provider: str,
        persona_count: int = 0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
        status: str = "completed",
        duration_seconds: float = 0.0,
        output_dir: str = "",
    ) -> RunMetadata:
        """
        Record a new generation run.

        Args:
            name: Experiment name.
            model: Model used.
            provider: Provider used.
            persona_count: Number of personas generated.
            input_tokens: Input tokens used.
            output_tokens: Output tokens used.
            cost: Estimated cost in USD.
            status: Run status.
            duration_seconds: Run duration.
            output_dir: Relative path to output directory.

        Returns:
            The recorded RunMetadata.
        """
        experiment = self._manager.load(name)
        history_path = experiment.path / self.HISTORY_FILE

        # Load existing runs
        runs = self._load_runs(history_path)

        # Determine next run ID
        run_id = max((r.run_id for r in runs), default=0) + 1

        # Create new run metadata
        run = RunMetadata(
            run_id=run_id,
            timestamp=datetime.now(),
            model=model,
            provider=provider,
            persona_count=persona_count,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            status=status,
            duration_seconds=duration_seconds,
            output_dir=output_dir,
        )

        runs.append(run)

        # Save
        self._save_runs(history_path, runs)

        return run

    def get_runs(
        self,
        name: str,
        last: int | None = None,
        status: str | None = None,
    ) -> list[RunMetadata]:
        """
        Get runs for an experiment.

        Args:
            name: Experiment name.
            last: Return only the last N runs.
            status: Filter by status.

        Returns:
            List of RunMetadata sorted by timestamp descending.
        """
        experiment = self._manager.load(name)
        history_path = experiment.path / self.HISTORY_FILE

        runs = self._load_runs(history_path)

        # Sort by timestamp descending (most recent first)
        runs.sort(key=lambda r: r.timestamp, reverse=True)

        # Filter by status
        if status:
            runs = [r for r in runs if r.status == status]

        # Limit to last N
        if last and last > 0:
            runs = runs[:last]

        return runs

    def get_run(self, name: str, run_id: int) -> RunMetadata | None:
        """
        Get a specific run by ID.

        Args:
            name: Experiment name.
            run_id: Run ID.

        Returns:
            RunMetadata if found, None otherwise.
        """
        runs = self.get_runs(name)
        for run in runs:
            if run.run_id == run_id:
                return run
        return None

    def get_statistics(self, name: str) -> RunStatistics:
        """
        Get aggregate statistics for an experiment.

        Args:
            name: Experiment name.

        Returns:
            RunStatistics with aggregate data.
        """
        runs = self.get_runs(name)

        if not runs:
            return RunStatistics()

        completed = [r for r in runs if r.status == "completed"]
        failed = [r for r in runs if r.status == "failed"]

        total_personas = sum(r.persona_count for r in completed)
        total_cost = sum(r.cost for r in runs)
        total_input = sum(r.input_tokens for r in runs)
        total_output = sum(r.output_tokens for r in runs)

        models = list(set(r.model for r in runs))
        providers = list(set(r.provider for r in runs))

        return RunStatistics(
            total_runs=len(runs),
            completed_runs=len(completed),
            failed_runs=len(failed),
            total_personas=total_personas,
            total_cost=total_cost,
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            avg_cost_per_run=total_cost / len(runs) if runs else 0.0,
            avg_personas_per_run=total_personas / len(completed) if completed else 0.0,
            models_used=models,
            providers_used=providers,
        )

    def diff_runs(
        self,
        name: str,
        run_id_1: int,
        run_id_2: int,
    ) -> dict[str, Any]:
        """
        Compare two runs.

        Args:
            name: Experiment name.
            run_id_1: First run ID.
            run_id_2: Second run ID.

        Returns:
            Dictionary with differences.

        Raises:
            ValueError: If run IDs not found.
        """
        run1 = self.get_run(name, run_id_1)
        run2 = self.get_run(name, run_id_2)

        if not run1:
            raise ValueError(f"Run #{run_id_1} not found")
        if not run2:
            raise ValueError(f"Run #{run_id_2} not found")

        # Calculate differences
        diff = {
            "run_1": run1.to_dict(),
            "run_2": run2.to_dict(),
            "differences": {},
        }

        # Compare fields
        fields_to_compare = [
            "model", "provider", "persona_count",
            "cost", "status", "input_tokens", "output_tokens"
        ]

        for field in fields_to_compare:
            val1 = getattr(run1, field)
            val2 = getattr(run2, field)
            if val1 != val2:
                diff["differences"][field] = {
                    "run_1": val1,
                    "run_2": val2,
                }

        # Calculate delta for numeric fields
        diff["delta"] = {
            "persona_count": run2.persona_count - run1.persona_count,
            "cost": run2.cost - run1.cost,
            "input_tokens": run2.input_tokens - run1.input_tokens,
            "output_tokens": run2.output_tokens - run1.output_tokens,
            "duration_seconds": run2.duration_seconds - run1.duration_seconds,
        }

        return diff

    def clear_history(self, name: str) -> None:
        """
        Clear all run history for an experiment.

        Args:
            name: Experiment name.
        """
        experiment = self._manager.load(name)
        history_path = experiment.path / self.HISTORY_FILE

        if history_path.exists():
            history_path.unlink()

    def _load_runs(self, history_path: Path) -> list[RunMetadata]:
        """Load runs from history file."""
        if not history_path.exists():
            return []

        with open(history_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "runs" not in data:
            return []

        return [
            RunMetadata.from_dict(run)
            for run in data["runs"]
        ]

    def _save_runs(self, history_path: Path, runs: list[RunMetadata]) -> None:
        """Save runs to history file."""
        data = {
            "runs": [run.to_dict() for run in runs]
        }

        with open(history_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False)
