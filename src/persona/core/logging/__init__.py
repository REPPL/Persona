"""Logging and monitoring (v0.9.0).

Provides comprehensive logging, progress tracking, and cost monitoring
for experiments and generation runs.
"""

from persona.core.logging.cost_tracker import (
    BudgetConfig,
    CostRecord,
    CostTracker,
    track_cost,
)
from persona.core.logging.experiment_logger import (
    EventType,
    ExperimentLogger,
    LogEvent,
    LogLevel,
    log_event,
    read_log_file,
)
from persona.core.logging.metadata import (
    GenerationMetadata,
    MetadataRecorder,
    calculate_checksum,
    record_metadata,
)
from persona.core.logging.progress import (
    ProgressTracker,
    TaskProgress,
    track_progress,
)
from persona.core.logging.structured import (
    LogContext,
    OutputFormat,
    StructuredLogger,
    configure_logging,
    get_logger,
)
from persona.core.logging.token_usage import (
    TokenBreakdown,
    TokenUsage,
    TokenUsageLogger,
    log_token_usage,
)

__all__ = [
    # Experiment logger (F-073)
    "ExperimentLogger",
    "LogEvent",
    "LogLevel",
    "EventType",
    "log_event",
    "read_log_file",
    # Structured logging (F-074)
    "StructuredLogger",
    "LogContext",
    "OutputFormat",
    "configure_logging",
    "get_logger",
    # Progress tracking (F-075)
    "ProgressTracker",
    "TaskProgress",
    "track_progress",
    # Metadata recording (F-076)
    "MetadataRecorder",
    "GenerationMetadata",
    "record_metadata",
    "calculate_checksum",
    # Token usage (F-077)
    "TokenUsageLogger",
    "TokenUsage",
    "TokenBreakdown",
    "log_token_usage",
    # Cost tracking (F-078)
    "CostTracker",
    "CostRecord",
    "BudgetConfig",
    "track_cost",
]
