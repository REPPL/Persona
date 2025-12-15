"""
Persona quality metrics and scoring.

This package provides comprehensive quality assessment for generated personas,
evaluating them across multiple dimensions including completeness, consistency,
evidence strength, distinctiveness, and realism.
"""

from persona.core.quality.config import QualityConfig
from persona.core.quality.models import (
    BatchQualityResult,
    DimensionScore,
    QualityLevel,
    QualityScore,
)
from persona.core.quality.scorer import QualityScorer

__all__ = [
    "QualityScorer",
    "QualityScore",
    "QualityLevel",
    "DimensionScore",
    "BatchQualityResult",
    "QualityConfig",
]
