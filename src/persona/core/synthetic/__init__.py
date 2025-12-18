"""
Synthetic data generation module.

This module provides functionality for generating realistic
synthetic interview data for demos and testing, as well as
privacy-preserving synthetic data generation from sensitive sources.
"""

from persona.core.synthetic.analyser import DataAnalyser
from persona.core.synthetic.generator import (
    DataDomain,
    GenerationConfig,
    SyntheticDataGenerator,
    SyntheticInterview,
    SyntheticParticipant,
)
from persona.core.synthetic.models import (
    ColumnType,
    DataSchema,
    DistributionStats,
    SyntheticResult,
    ValidationResult,
)
from persona.core.synthetic.pipeline import SyntheticPipeline
from persona.core.synthetic.validator import SyntheticValidator

__all__ = [
    # Demo/test data generation (existing)
    "SyntheticDataGenerator",
    "SyntheticInterview",
    "SyntheticParticipant",
    "DataDomain",
    "GenerationConfig",
    # Privacy-preserving synthetic data generation (F-115)
    "SyntheticPipeline",
    "DataAnalyser",
    "SyntheticValidator",
    "SyntheticResult",
    "ValidationResult",
    "DataSchema",
    "DistributionStats",
    "ColumnType",
]
