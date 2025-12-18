"""
Persona quality metrics and scoring.

This package provides comprehensive quality assessment for generated personas,
evaluating them across multiple dimensions including completeness, consistency,
evidence strength, distinctiveness, and realism.

The package uses a registry pattern for extensible metrics, allowing custom
metrics to be registered and discovered via entry points.
"""

from persona.core.quality.base import (
    MetricCategory,
    QualityMetric,
    get_metric_requirements,
)
from persona.core.quality.config import QualityConfig
from persona.core.quality.models import (
    BatchQualityResult,
    DimensionScore,
    QualityLevel,
    QualityScore,
)
from persona.core.quality.registry import (
    MetricInfo,
    MetricRegistry,
    get_registry,
    register_metric,
)
from persona.core.quality.scorer import QualityScorer

__all__ = [
    # Core classes
    "QualityScorer",
    "QualityScore",
    "QualityLevel",
    "DimensionScore",
    "BatchQualityResult",
    "QualityConfig",
    # Registry
    "QualityMetric",
    "MetricRegistry",
    "MetricInfo",
    "MetricCategory",
    "get_registry",
    "register_metric",
    "get_metric_requirements",
]
