"""
Synthetic data generation module.

This module provides functionality for generating realistic
synthetic interview data for demos and testing, as well as
privacy-preserving synthetic data generation from sensitive sources.
"""

from persona.core.synthetic.generator import (
    SyntheticDataGenerator,
    SyntheticInterview,
    SyntheticParticipant,
    DataDomain,
    GenerationConfig,
)
from persona.core.synthetic.pipeline import SyntheticPipeline
from persona.core.synthetic.analyser import DataAnalyser
from persona.core.synthetic.validator import SyntheticValidator
from persona.core.synthetic.models import (
    SyntheticResult,
    ValidationResult,
    DataSchema,
    DistributionStats,
    ColumnType,
)

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
