"""
Multi-model generation module for v0.8.0.

Provides multi-model persona generation, execution strategies,
coverage analysis, confidence scoring, and consolidation mapping.
"""

from persona.core.multimodel.capabilities import (
    CapabilityChecker,
    CapabilityQuery,
    ModelCapabilities,
    ModelComparison,
)
from persona.core.multimodel.confidence import (
    AttributeConfidence,
    ConfidenceLevel,
    ConfidenceScorer,
    PersonaConfidence,
)
from persona.core.multimodel.consolidation import (
    ConsolidationMap,
    ConsolidationMapper,
    MergeRecommendation,
    PersonaSimilarity,
)
from persona.core.multimodel.cost import (
    ModelCostDetail,
    MultiModelCostBreakdown,
    MultiModelCostEstimator,
)
from persona.core.multimodel.coverage import (
    CoverageAnalyser,
    CoverageAnalysis,
    SourceUtilisation,
    ThemeCoverage,
)
from persona.core.multimodel.generator import (
    ModelOutput,
    ModelSpec,
    MultiModelGenerator,
    MultiModelResult,
)
from persona.core.multimodel.strategies import (
    ConsensusStrategy,
    ExecutionMode,
    ExecutionStrategy,
    ParallelStrategy,
    SequentialStrategy,
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
