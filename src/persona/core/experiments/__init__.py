"""
Experiment management module.

This module provides functionality for organising generation runs
into experiments with configuration persistence.

Two storage backends are available:
- YAML-based (ExperimentManager) - file-based, human-readable
- SQLite-based (SQLiteExperimentStore) - queryable, better for large datasets

Example:
    ```python
    # YAML-based (legacy, simple)
    from persona.core.experiments import ExperimentManager
    manager = ExperimentManager("./experiments")
    exp = manager.create("my-experiment")

    # SQLite-based (recommended for new projects)
    from persona.core.experiments import SQLiteExperimentStore
    with SQLiteExperimentStore("./experiments.db") as store:
        exp_id = store.create_experiment("my-experiment")
        store.create_run(exp_id, "claude-sonnet", "anthropic")
    ```
"""

# YAML-based manager (legacy)
from persona.core.experiments.manager import (
    EditHistoryEntry,
    Experiment,
    ExperimentConfig,
    ExperimentEditor,
    ExperimentManager,
    RunHistory,
    RunMetadata,
    RunStatistics,
)

# Pydantic models
from persona.core.experiments.models import (
    ExperimentModel,
    ExperimentStatistics,
    ExperimentStatus,
    RunComparison,
    RunModel,
    RunStatus,
    VariantModel,
)

# SQLite implementation
from persona.core.experiments.sqlite_store import (
    SQLiteExperimentStore,
    get_default_db_path,
)

# Abstract store interface
from persona.core.experiments.store import ExperimentStore

# Run history tracking
from persona.core.experiments.history import (
    RunHistoryManager,
    RunInfo,
    RunHistory as RunHistoryTracker,
    TokenUsage,
)

# Experiment context
from persona.core.experiments.context import ExperimentContext

# Experiment manifest
from persona.core.experiments.manifest import (
    ExperimentManifest,
    ExperimentSummary,
    ManifestManager,
)

__all__ = [
    # YAML-based (legacy)
    "ExperimentManager",
    "Experiment",
    "ExperimentConfig",
    "ExperimentEditor",
    "EditHistoryEntry",
    "RunHistory",
    "RunMetadata",
    "RunStatistics",
    # Pydantic models
    "ExperimentModel",
    "ExperimentStatus",
    "VariantModel",
    "RunModel",
    "RunStatus",
    "ExperimentStatistics",
    "RunComparison",
    # Abstract store
    "ExperimentStore",
    # SQLite store
    "SQLiteExperimentStore",
    "get_default_db_path",
    # Run history tracking
    "RunHistoryManager",
    "RunInfo",
    "RunHistoryTracker",
    "TokenUsage",
    # Experiment context
    "ExperimentContext",
    # Experiment manifest
    "ExperimentManifest",
    "ExperimentSummary",
    "ManifestManager",
]
