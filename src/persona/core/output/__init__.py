"""
Output formatting and file management module.

This module provides functionality for formatting and saving
generated personas to various output formats.
"""

from persona.core.output.manager import OutputManager
from persona.core.output.formatters import JSONFormatter, MarkdownFormatter, TextFormatter
from persona.core.output.empathy_table import (
    EmpathyTableFormatter,
    EmpathyTableRow,
    EmpathyTableConfig,
    TableFormat,
)
from persona.core.output.registry import (
    BaseFormatterV2,
    FormatterInfo,
    FormatterRegistry,
    OutputSection,
    SectionConfig,
    get_registry,
    register,
)
from persona.core.output.narrative import (
    NarrativeConfig,
    NarrativeFormatter,
    Perspective,
    FirstPersonNarrativeFormatter,
    ThirdPersonNarrativeFormatter,
)
from persona.core.output.tables import (
    ASCIITableFormatter,
    CSVTableFormatter,
    LaTeXTableFormatter,
    MarkdownTableFormatter,
    PersonaComparisonTable,
    TableColumn,
    TableConfig,
    TableOutputFormat,
)
from persona.core.output.usage import (
    FeaturePrediction,
    InteractionPoint,
    InteractionType,
    JourneyStep,
    ProductContext,
    UsageFormatter,
    UsageLikelihood,
    UsageScenario,
    UsageScenarioGenerator,
)
from persona.core.output.readme import (
    CustomReadmeTemplate,
    GenerationSummary,
    PersonaSummary,
    ReadmeGenerator,
)
from persona.core.output.response_capture import (
    RequestCapture,
    ResponseCapture,
    ResponseCaptureManager,
    ResponseCaptureStore,
    TokenUsage,
    create_request_capture,
)

__all__ = [
    # Core
    "OutputManager",
    "JSONFormatter",
    "MarkdownFormatter",
    "TextFormatter",
    # Empathy table output
    "EmpathyTableFormatter",
    "EmpathyTableRow",
    "EmpathyTableConfig",
    "TableFormat",
    # Registry (F-039)
    "BaseFormatterV2",
    "FormatterInfo",
    "FormatterRegistry",
    "OutputSection",
    "SectionConfig",
    "get_registry",
    "register",
    # Narrative (F-036)
    "NarrativeConfig",
    "NarrativeFormatter",
    "Perspective",
    "FirstPersonNarrativeFormatter",
    "ThirdPersonNarrativeFormatter",
    # Tables (F-037)
    "ASCIITableFormatter",
    "CSVTableFormatter",
    "LaTeXTableFormatter",
    "MarkdownTableFormatter",
    "PersonaComparisonTable",
    "TableColumn",
    "TableConfig",
    "TableOutputFormat",
    # Usage (F-038)
    "FeaturePrediction",
    "InteractionPoint",
    "InteractionType",
    "JourneyStep",
    "ProductContext",
    "UsageFormatter",
    "UsageLikelihood",
    "UsageScenario",
    "UsageScenarioGenerator",
    # README (F-041)
    "CustomReadmeTemplate",
    "GenerationSummary",
    "PersonaSummary",
    "ReadmeGenerator",
    # Response Capture (F-042)
    "RequestCapture",
    "ResponseCapture",
    "ResponseCaptureManager",
    "ResponseCaptureStore",
    "TokenUsage",
    "create_request_capture",
]
