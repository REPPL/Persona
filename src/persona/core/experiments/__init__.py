"""
Experiment management module.

This module provides functionality for organising generation runs
into experiments with configuration persistence.
"""

from persona.core.experiments.manager import ExperimentManager, Experiment

__all__ = [
    "ExperimentManager",
    "Experiment",
]
