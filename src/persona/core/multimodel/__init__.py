"""
Multi-model generation module for v0.8.0.

Provides multi-model persona generation, execution strategies,
coverage analysis, confidence scoring, and consolidation mapping.
"""

from persona.core.multimodel.generator import (
    MultiModelGenerator,
    ModelSpec,
    MultiModelResult,
    ModelOutput,
)
from persona.core.multimodel.strategies import (
    ExecutionStrategy,
    ParallelStrategy,
    SequentialStrategy,
    ConsensusStrategy,
    ExecutionMode,
)
from persona.core.multimodel.coverage import (
    CoverageAnalyser,
    CoverageAnalysis,
    ThemeCoverage,
    SourceUtilisation,
)
from persona.core.multimodel.confidence import (
    ConfidenceScorer,
    ConfidenceLevel,
    AttributeConfidence,
    PersonaConfidence,
)
from persona.core.multimodel.consolidation import (
    ConsolidationMapper,
    PersonaSimilarity,
    ConsolidationMap,
    MergeRecommendation,
)
from persona.core.multimodel.cost import (
    MultiModelCostEstimator,
    MultiModelCostBreakdown,
    ModelCostDetail,
)
from persona.core.multimodel.capabilities import (
    ModelCapabilities,
    CapabilityChecker,
    CapabilityQuery,
    ModelComparison,
)

__all__ = [
    # Generator (F-066)
    "MultiModelGenerator",
    "ModelSpec",
    "MultiModelResult",
    "ModelOutput",
    # Strategies (F-067)
    "ExecutionStrategy",
    "ParallelStrategy",
    "SequentialStrategy",
    "ConsensusStrategy",
    "ExecutionMode",
    # Coverage (F-068)
    "CoverageAnalyser",
    "CoverageAnalysis",
    "ThemeCoverage",
    "SourceUtilisation",
    # Confidence (F-069)
    "ConfidenceScorer",
    "ConfidenceLevel",
    "AttributeConfidence",
    "PersonaConfidence",
    # Consolidation (F-070)
    "ConsolidationMapper",
    "PersonaSimilarity",
    "ConsolidationMap",
    "MergeRecommendation",
    # Cost (F-071)
    "MultiModelCostEstimator",
    "MultiModelCostBreakdown",
    "ModelCostDetail",
    # Capabilities (F-072)
    "ModelCapabilities",
    "CapabilityChecker",
    "CapabilityQuery",
    "ModelComparison",
]
