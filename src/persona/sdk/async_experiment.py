"""
Async experiment SDK class.

This module provides async versions of experiment management
for integration with async applications.
"""

import asyncio
from pathlib import Path
from typing import Any

from persona.sdk.async_generator import AsyncPersonaGenerator
from persona.sdk.exceptions import (
    DataError,
)
from persona.sdk.experiment import ExperimentSDK
from persona.sdk.models import (
    ExperimentConfig,
    ExperimentModel,
    GenerationResultModel,
    PersonaConfig,
)


class AsyncExperimentSDK:
    """
    Async experiment management for integration with async applications.

    Provides async versions of ExperimentSDK methods.

    Example:
        import asyncio
        from persona.sdk import AsyncExperimentSDK, ExperimentConfig

        async def main():
            sdk = AsyncExperimentSDK("./experiments")

            # Create experiment
            exp = await sdk.acreate(ExperimentConfig(name="test"))

            # Add data
            await sdk.aadd_data(exp.name, "./interviews.csv")

            # Generate
            result = await sdk.agenerate(exp.name)

        asyncio.run(main())
    """

    def __init__(self, base_dir: str | Path = "./experiments") -> None:
        """
        Initialise AsyncExperimentSDK.

        Args:
            base_dir: Base directory for experiments.
        """
        self._sync_sdk = ExperimentSDK(base_dir)
        self._base_dir = Path(base_dir)

    @property
    def base_dir(self) -> Path:
        """Return base directory path."""
        return self._base_dir

    async def acreate(self, config: ExperimentConfig) -> ExperimentModel:
        """
        Asynchronously create a new experiment.

        Args:
            config: Experiment configuration.

        Returns:
            The created ExperimentModel.

        Raises:
            ConfigurationError: If experiment already exists.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sync_sdk.create(config),
        )

    async def aload(self, name: str) -> ExperimentModel:
        """
        Asynchronously load an existing experiment.

        Args:
            name: Experiment name.

        Returns:
            The loaded ExperimentModel.

        Raises:
            ConfigurationError: If experiment doesn't exist.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sync_sdk.load(name),
        )

    async def alist_experiments(self) -> list[ExperimentModel]:
        """
        Asynchronously list all experiments.

        Returns:
            List of ExperimentModel instances.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_sdk.list_experiments,
        )

    async def adelete(self, name: str, confirm: bool = False) -> bool:
        """
        Asynchronously delete an experiment.

        Args:
            name: Experiment name.
            confirm: Must be True to actually delete.

        Returns:
            True if deleted.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sync_sdk.delete(name, confirm=confirm),
        )

    async def aexists(self, name: str) -> bool:
        """
        Asynchronously check if an experiment exists.

        Args:
            name: Experiment name.

        Returns:
            True if experiment exists.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sync_sdk.exists(name),
        )

    async def aadd_data(
        self,
        experiment_name: str,
        data_path: str | Path,
        copy: bool = True,
    ) -> Path:
        """
        Asynchronously add data file to an experiment.

        Args:
            experiment_name: Experiment name.
            data_path: Path to data file.
            copy: If True, copy file; if False, create symlink.

        Returns:
            Path to the data file in experiment.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sync_sdk.add_data(experiment_name, data_path, copy=copy),
        )

    async def alist_data(self, experiment_name: str) -> list[Path]:
        """
        Asynchronously list data files in an experiment.

        Args:
            experiment_name: Experiment name.

        Returns:
            List of data file paths.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sync_sdk.list_data(experiment_name),
        )

    async def agenerate(
        self,
        experiment_name: str,
        config: PersonaConfig | None = None,
    ) -> GenerationResultModel:
        """
        Asynchronously generate personas for an experiment.

        Uses AsyncPersonaGenerator for non-blocking generation.

        Args:
            experiment_name: Experiment name.
            config: Override generation config.

        Returns:
            GenerationResultModel with generated personas.
        """
        exp = await self.aload(experiment_name)

        # Check for data files
        data_files = await self.alist_data(experiment_name)
        if not data_files:
            raise DataError(
                f"No data files in experiment: {experiment_name}",
                path=str(exp.data_dir),
            )

        # Create config from experiment defaults if not provided
        if config is None:
            config = PersonaConfig(
                count=3,
                workflow=exp.workflow,
            )

        # Use async generator
        generator = AsyncPersonaGenerator(
            provider=exp.provider,
            model=exp.model,
        )

        return await generator.agenerate(exp.data_dir, config)

    async def aget_outputs(self, experiment_name: str) -> list[Path]:
        """
        Asynchronously list output directories for an experiment.

        Args:
            experiment_name: Experiment name.

        Returns:
            List of output directory paths.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sync_sdk.get_outputs(experiment_name),
        )

    async def aget_statistics(self, experiment_name: str) -> dict[str, Any]:
        """
        Asynchronously get statistics for an experiment.

        Args:
            experiment_name: Experiment name.

        Returns:
            Dictionary with experiment statistics.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sync_sdk.get_statistics(experiment_name),
        )

    # Sync methods for convenience (no IO)
    def exists(self, name: str) -> bool:
        """Sync check if experiment exists."""
        return self._sync_sdk.exists(name)

    def list_experiments(self) -> list[ExperimentModel]:
        """Sync list experiments."""
        return self._sync_sdk.list_experiments()
