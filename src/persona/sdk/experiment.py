"""
Experiment SDK class.

This module provides the ExperimentSDK class for programmatic
experiment management.
"""

from pathlib import Path
from typing import Any

from persona.sdk.models import (
    ExperimentConfig,
    ExperimentModel,
    PersonaConfig,
    GenerationResultModel,
)
from persona.sdk.exceptions import (
    ConfigurationError,
    DataError,
    ValidationError,
)
from persona.sdk.generator import PersonaGenerator


class ExperimentSDK:
    """
    Manage persona generation experiments.

    Experiments organise multiple generation runs with shared
    configuration and data storage.

    Example:
        from persona.sdk import ExperimentSDK, ExperimentConfig

        # Create experiment
        sdk = ExperimentSDK("./experiments")
        exp = sdk.create(ExperimentConfig(
            name="user-research-2024",
            description="Q4 user research study",
        ))

        # Add data
        sdk.add_data(exp.name, "./interviews.csv")

        # Generate personas
        result = sdk.generate(exp.name)

        # List experiments
        for exp in sdk.list_experiments():
            print(f"{exp.name}: {exp.run_count} runs")
    """

    def __init__(self, base_dir: str | Path = "./experiments") -> None:
        """
        Initialise ExperimentSDK.

        Args:
            base_dir: Base directory for experiments.
        """
        self._base_dir = Path(base_dir)

    @property
    def base_dir(self) -> Path:
        """Return base directory path."""
        return self._base_dir

    def create(self, config: ExperimentConfig) -> ExperimentModel:
        """
        Create a new experiment.

        Args:
            config: Experiment configuration.

        Returns:
            The created ExperimentModel.

        Raises:
            ConfigurationError: If experiment already exists.
            ValidationError: If configuration is invalid.

        Example:
            exp = sdk.create(ExperimentConfig(
                name="user-research-2024",
                provider="anthropic",
            ))
        """
        from persona.core.experiments import ExperimentManager

        manager = ExperimentManager(self._base_dir)

        # Check if exists
        if manager.exists(config.name):
            raise ConfigurationError(
                f"Experiment already exists: {config.name}",
                field="name",
                value=config.name,
            )

        try:
            # Convert config to dict with mode='json' to ensure enum values are strings
            config_dict = config.model_dump(mode="json")
            core_exp = manager.create(
                name=config_dict["name"],
                description=config_dict["description"],
                provider=config_dict["provider"],
                model=config_dict["model"],
                workflow=config_dict["workflow"],
                count=config_dict["count"],
                complexity=config_dict["complexity"],
                detail_level=config_dict["detail_level"],
            )
        except ValueError as e:
            raise ConfigurationError(str(e), field="name") from e

        return ExperimentModel.from_core_experiment(core_exp)

    def load(self, name: str) -> ExperimentModel:
        """
        Load an existing experiment.

        Args:
            name: Experiment name.

        Returns:
            The loaded ExperimentModel.

        Raises:
            ConfigurationError: If experiment doesn't exist.

        Example:
            exp = sdk.load("user-research-2024")
        """
        from persona.core.experiments import ExperimentManager

        manager = ExperimentManager(self._base_dir)

        try:
            core_exp = manager.load(name)
        except FileNotFoundError as e:
            raise ConfigurationError(
                f"Experiment not found: {name}",
                field="name",
                value=name,
            ) from e

        return ExperimentModel.from_core_experiment(core_exp)

    def list_experiments(self) -> list[ExperimentModel]:
        """
        List all experiments.

        Returns:
            List of ExperimentModel instances.

        Example:
            for exp in sdk.list_experiments():
                print(f"{exp.name}: {exp.description}")
        """
        from persona.core.experiments import ExperimentManager

        manager = ExperimentManager(self._base_dir)
        experiments = []

        for name in manager.list_experiments():
            try:
                exp = self.load(name)
                experiments.append(exp)
            except ConfigurationError:
                continue

        return experiments

    def delete(self, name: str, confirm: bool = False) -> bool:
        """
        Delete an experiment.

        Args:
            name: Experiment name.
            confirm: Must be True to actually delete.

        Returns:
            True if deleted.

        Raises:
            ConfigurationError: If experiment doesn't exist.

        Example:
            sdk.delete("old-experiment", confirm=True)
        """
        from persona.core.experiments import ExperimentManager

        manager = ExperimentManager(self._base_dir)

        if not manager.exists(name):
            raise ConfigurationError(
                f"Experiment not found: {name}",
                field="name",
                value=name,
            )

        return manager.delete(name, confirm=confirm)

    def exists(self, name: str) -> bool:
        """
        Check if an experiment exists.

        Args:
            name: Experiment name.

        Returns:
            True if experiment exists.
        """
        from persona.core.experiments import ExperimentManager

        manager = ExperimentManager(self._base_dir)
        return manager.exists(name)

    def add_data(
        self,
        experiment_name: str,
        data_path: str | Path,
        copy: bool = True,
    ) -> Path:
        """
        Add data file to an experiment.

        Args:
            experiment_name: Experiment name.
            data_path: Path to data file.
            copy: If True, copy file; if False, create symlink.

        Returns:
            Path to the data file in experiment.

        Raises:
            ConfigurationError: If experiment doesn't exist.
            DataError: If data file doesn't exist.

        Example:
            sdk.add_data("my-experiment", "./interviews.csv")
        """
        import shutil

        exp = self.load(experiment_name)
        source = Path(data_path)

        if not source.exists():
            raise DataError(
                f"Data file not found: {data_path}",
                path=str(data_path),
            )

        dest = exp.data_dir / source.name

        if copy:
            shutil.copy2(source, dest)
        else:
            if dest.exists():
                dest.unlink()
            dest.symlink_to(source.resolve())

        return dest

    def list_data(self, experiment_name: str) -> list[Path]:
        """
        List data files in an experiment.

        Args:
            experiment_name: Experiment name.

        Returns:
            List of data file paths.

        Example:
            files = sdk.list_data("my-experiment")
        """
        exp = self.load(experiment_name)

        if not exp.data_dir.exists():
            return []

        return sorted([
            f for f in Path(exp.data_dir).iterdir()
            if f.is_file() and not f.name.startswith(".")
        ])

    def generate(
        self,
        experiment_name: str,
        config: PersonaConfig | None = None,
    ) -> GenerationResultModel:
        """
        Generate personas for an experiment.

        Uses the experiment's data files and configuration.

        Args:
            experiment_name: Experiment name.
            config: Override generation config. If None, uses experiment defaults.

        Returns:
            GenerationResultModel with generated personas.

        Raises:
            ConfigurationError: If experiment doesn't exist.
            DataError: If no data files in experiment.

        Example:
            result = sdk.generate("my-experiment")
            for persona in result.personas:
                print(persona.name)
        """
        exp = self.load(experiment_name)

        # Check for data files
        data_files = self.list_data(experiment_name)
        if not data_files:
            raise DataError(
                f"No data files in experiment: {experiment_name}",
                path=str(exp.data_dir),
            )

        # Create config from experiment defaults if not provided
        if config is None:
            config = PersonaConfig(
                count=3,  # Use experiment's count if stored
                workflow=exp.workflow,
            )

        # Create generator with experiment settings
        generator = PersonaGenerator(
            provider=exp.provider,
            model=exp.model,
        )

        # Generate from data directory
        return generator.generate(exp.data_dir, config)

    def get_outputs(self, experiment_name: str) -> list[Path]:
        """
        List output directories for an experiment.

        Args:
            experiment_name: Experiment name.

        Returns:
            List of output directory paths.

        Example:
            outputs = sdk.get_outputs("my-experiment")
            for output in outputs:
                print(f"Run: {output.name}")
        """
        exp = self.load(experiment_name)

        if not exp.outputs_dir.exists():
            return []

        return sorted([
            d for d in Path(exp.outputs_dir).iterdir()
            if d.is_dir()
        ])

    def get_statistics(self, experiment_name: str) -> dict[str, Any]:
        """
        Get statistics for an experiment.

        Args:
            experiment_name: Experiment name.

        Returns:
            Dictionary with experiment statistics.

        Example:
            stats = sdk.get_statistics("my-experiment")
            print(f"Total runs: {stats['run_count']}")
        """
        exp = self.load(experiment_name)
        outputs = self.get_outputs(experiment_name)
        data_files = self.list_data(experiment_name)

        # Calculate total size
        total_data_size = sum(
            f.stat().st_size for f in data_files if f.is_file()
        )

        return {
            "name": exp.name,
            "description": exp.description,
            "provider": exp.provider,
            "model": exp.model,
            "workflow": exp.workflow,
            "created_at": exp.created_at.isoformat(),
            "run_count": len(outputs),
            "data_file_count": len(data_files),
            "data_size_bytes": total_data_size,
            "output_count": len(outputs),
        }
