"""
Abstract storage interface for experiments.

Provides a base class for experiment storage backends (YAML, SQLite, etc.).
This allows switching between storage mechanisms without changing the
business logic.
"""

from abc import ABC, abstractmethod
from typing import Any


class ExperimentStore(ABC):
    """
    Abstract base class for experiment storage.

    Implementations should handle:
    - Experiment CRUD operations
    - Variant management
    - Run history tracking
    - Project-experiment associations

    Example:
        ```python
        store = SQLiteExperimentStore(db_path)
        exp_id = store.create_experiment(
            name="user-research",
            project_id="proj-123",
            hypothesis="Users prefer dark mode"
        )
        store.create_run(
            experiment_id=exp_id,
            model="claude-sonnet-4-20250514",
            provider="anthropic",
        )
        ```
    """

    # =========================================================================
    # Experiment Operations
    # =========================================================================

    @abstractmethod
    def create_experiment(
        self,
        name: str,
        *,
        project_id: str | None = None,
        description: str = "",
        hypothesis: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a new experiment.

        Args:
            name: Experiment name.
            project_id: Optional project this experiment belongs to.
            description: Optional description.
            hypothesis: Optional research hypothesis.
            config: Optional default configuration.

        Returns:
            Unique experiment ID.

        Raises:
            ValueError: If experiment with name already exists in project.
        """
        ...

    @abstractmethod
    def get_experiment(self, experiment_id: str) -> dict[str, Any] | None:
        """
        Get experiment by ID.

        Args:
            experiment_id: Unique experiment identifier.

        Returns:
            Experiment data dictionary or None if not found.
        """
        ...

    @abstractmethod
    def get_experiment_by_name(
        self,
        name: str,
        project_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Get experiment by name.

        Args:
            name: Experiment name.
            project_id: Optional project to search within.

        Returns:
            Experiment data dictionary or None if not found.
        """
        ...

    @abstractmethod
    def list_experiments(
        self,
        project_id: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        List experiments.

        Args:
            project_id: Filter by project (None for all).
            status: Filter by status (planned, active, completed, archived).

        Returns:
            List of experiment data dictionaries.
        """
        ...

    @abstractmethod
    def update_experiment(
        self,
        experiment_id: str,
        **updates: Any,
    ) -> bool:
        """
        Update experiment fields.

        Args:
            experiment_id: Experiment to update.
            **updates: Fields to update.

        Returns:
            True if updated, False if not found.
        """
        ...

    @abstractmethod
    def delete_experiment(self, experiment_id: str) -> bool:
        """
        Delete an experiment.

        Args:
            experiment_id: Experiment to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...

    # =========================================================================
    # Variant Operations
    # =========================================================================

    @abstractmethod
    def create_variant(
        self,
        experiment_id: str,
        name: str,
        parameters: dict[str, Any],
        *,
        description: str = "",
    ) -> str:
        """
        Create a variant (named parameter set) for an experiment.

        Args:
            experiment_id: Parent experiment.
            name: Variant name (unique within experiment).
            parameters: Parameter dictionary.
            description: Optional description.

        Returns:
            Unique variant ID.

        Raises:
            ValueError: If variant name already exists in experiment.
        """
        ...

    @abstractmethod
    def get_variant(self, variant_id: str) -> dict[str, Any] | None:
        """
        Get variant by ID.

        Args:
            variant_id: Unique variant identifier.

        Returns:
            Variant data dictionary or None if not found.
        """
        ...

    @abstractmethod
    def list_variants(self, experiment_id: str) -> list[dict[str, Any]]:
        """
        List variants for an experiment.

        Args:
            experiment_id: Parent experiment.

        Returns:
            List of variant data dictionaries.
        """
        ...

    @abstractmethod
    def update_variant(
        self,
        variant_id: str,
        **updates: Any,
    ) -> bool:
        """
        Update variant fields.

        Args:
            variant_id: Variant to update.
            **updates: Fields to update.

        Returns:
            True if updated, False if not found.
        """
        ...

    @abstractmethod
    def delete_variant(self, variant_id: str) -> bool:
        """
        Delete a variant.

        Args:
            variant_id: Variant to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...

    # =========================================================================
    # Run Operations
    # =========================================================================

    @abstractmethod
    def create_run(
        self,
        experiment_id: str,
        model: str,
        provider: str,
        *,
        variant_id: str | None = None,
        parameters: dict[str, Any] | None = None,
        output_dir: str = "",
    ) -> str:
        """
        Create a new run.

        Args:
            experiment_id: Parent experiment.
            model: Model used.
            provider: Provider used.
            variant_id: Optional variant (for named parameter sets).
            parameters: Optional override parameters.
            output_dir: Path to output directory.

        Returns:
            Unique run ID.
        """
        ...

    @abstractmethod
    def get_run(self, run_id: str) -> dict[str, Any] | None:
        """
        Get run by ID.

        Args:
            run_id: Unique run identifier.

        Returns:
            Run data dictionary or None if not found.
        """
        ...

    @abstractmethod
    def list_runs(
        self,
        experiment_id: str,
        *,
        variant_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        List runs for an experiment.

        Args:
            experiment_id: Parent experiment.
            variant_id: Filter by variant.
            status: Filter by status.
            limit: Maximum number of runs to return.

        Returns:
            List of run data dictionaries, newest first.
        """
        ...

    @abstractmethod
    def update_run(
        self,
        run_id: str,
        **updates: Any,
    ) -> bool:
        """
        Update run fields.

        Args:
            run_id: Run to update.
            **updates: Fields to update.

        Returns:
            True if updated, False if not found.
        """
        ...

    @abstractmethod
    def complete_run(
        self,
        run_id: str,
        *,
        persona_count: int = 0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
        duration_seconds: float = 0.0,
        metrics: dict[str, Any] | None = None,
        status: str = "completed",
    ) -> bool:
        """
        Mark a run as complete with final metrics.

        Args:
            run_id: Run to complete.
            persona_count: Number of personas generated.
            input_tokens: Total input tokens.
            output_tokens: Total output tokens.
            cost: Estimated cost in USD.
            duration_seconds: Run duration.
            metrics: Additional metrics dictionary.
            status: Final status (completed, failed, cancelled).

        Returns:
            True if updated, False if not found.
        """
        ...

    @abstractmethod
    def delete_run(self, run_id: str) -> bool:
        """
        Delete a run.

        Args:
            run_id: Run to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...

    # =========================================================================
    # Statistics and Queries
    # =========================================================================

    @abstractmethod
    def get_experiment_statistics(self, experiment_id: str) -> dict[str, Any]:
        """
        Get aggregate statistics for an experiment.

        Args:
            experiment_id: Experiment to analyse.

        Returns:
            Dictionary with statistics (total_runs, completed, failed,
            total_personas, total_cost, etc.).
        """
        ...

    @abstractmethod
    def compare_runs(
        self,
        run_id_1: str,
        run_id_2: str,
    ) -> dict[str, Any]:
        """
        Compare two runs.

        Args:
            run_id_1: First run.
            run_id_2: Second run.

        Returns:
            Dictionary with comparison data.
        """
        ...

    # =========================================================================
    # Lifecycle
    # =========================================================================

    @abstractmethod
    def close(self) -> None:
        """Close the store and release resources."""
        ...

    def __enter__(self) -> "ExperimentStore":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
