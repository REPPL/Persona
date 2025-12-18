"""
Batch processing module for v0.7.0.

Provides folder processing, multi-file handling, context management,
token tracking, and persona count estimation.
"""

from persona.core.batch.combiner import (
    CombinedContent,
    FileCombiner,
    SeparatorStyle,
)
from persona.core.batch.context import (
    ContextBudget,
    ContextManager,
    ContextWarning,
    WarningLevel,
)
from persona.core.batch.count import (
    CountSpecification,
    CountType,
    parse_count,
)
from persona.core.batch.estimator import (
    CountEstimate,
    EstimationFactors,
    PersonaEstimator,
)
from persona.core.batch.processor import (
    BatchConfig,
    BatchProcessor,
    BatchResult,
)
from persona.core.batch.scanner import (
    FileInfo,
    FolderScanner,
    ScanResult,
)
from persona.core.batch.sources import (
    DataSourceTracker,
    SourceMetadata,
    SourceSummary,
)
from persona.core.batch.tokens import (
    TokenBreakdown,
    TokenCounter,
    TokenUsage,
)

__all__ = [
    # Scanner (F-059)
    "FolderScanner",
    "ScanResult",
    "FileInfo",
    # Combiner (F-060)
    "FileCombiner",
    "SeparatorStyle",
    "CombinedContent",
    # Count (F-061)
    "CountSpecification",
    "CountType",
    "parse_count",
    # Context (F-062)
    "ContextManager",
    "ContextBudget",
    "ContextWarning",
    "WarningLevel",
    # Tokens (F-063)
    "TokenCounter",
    "TokenUsage",
    "TokenBreakdown",
    # Sources (F-064)
    "DataSourceTracker",
    "SourceMetadata",
    "SourceSummary",
    # Estimator (F-065)
    "PersonaEstimator",
    "CountEstimate",
    "EstimationFactors",
    # Processor (F-020)
    "BatchProcessor",
    "BatchConfig",
    "BatchResult",
]
