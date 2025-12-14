"""
Experiment management module.

This module provides functionality for organising generation runs
into experiments with configuration persistence.
"""

from persona.core.experiments.manager import (
    ExperimentManager,
    Experiment,
    ExperimentConfig,
    ExperimentEditor,
    EditHistoryEntry,
    RunHistory,
    RunMetadata,
    RunStatistics,
)

__all__ = [
    "ExperimentManager",
    "Experiment",
    "ExperimentConfig",
    "ExperimentEditor",
    "EditHistoryEntry",
    "RunHistory",
    "RunMetadata",
    "RunStatistics",
]
