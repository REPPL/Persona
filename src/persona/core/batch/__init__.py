"""
Batch processing module for v0.7.0.

Provides folder processing, multi-file handling, context management,
token tracking, and persona count estimation.
"""

from persona.core.batch.scanner import (
    FolderScanner,
    ScanResult,
    FileInfo,
)
from persona.core.batch.combiner import (
    FileCombiner,
    SeparatorStyle,
    CombinedContent,
)
from persona.core.batch.count import (
    CountSpecification,
    CountType,
    parse_count,
)
from persona.core.batch.context import (
    ContextManager,
    ContextBudget,
    ContextWarning,
    WarningLevel,
)
from persona.core.batch.tokens import (
    TokenCounter,
    TokenUsage,
    TokenBreakdown,
)
from persona.core.batch.sources import (
    DataSourceTracker,
    SourceMetadata,
    SourceSummary,
)
from persona.core.batch.estimator import (
    PersonaEstimator,
    CountEstimate,
    EstimationFactors,
)
from persona.core.batch.processor import (
    BatchProcessor,
    BatchConfig,
    BatchResult,
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
