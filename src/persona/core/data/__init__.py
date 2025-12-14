"""
Data loading and processing module.

This module provides functionality for loading qualitative research data
from various file formats and preparing it for LLM analysis.
"""

from persona.core.data.loader import DataLoader
from persona.core.data.formats import (
    CSVLoader,
    HTMLLoader,
    JSONLoader,
    MarkdownLoader,
    OrgLoader,
    TextLoader,
    YAMLLoader,
)
from persona.core.data.empathy_map import (
    EmpathyMap,
    EmpathyMapDimension,
    EmpathyMapLoader,
    EmpathyMapValidationError,
    EmpathyMapValidationResult,
    ParticipantTypeMap,
)
from persona.core.data.workshop import (
    WorkshopCategory,
    PostItNote,
    WorkshopExtractionResult,
    WorkshopImportConfig,
    WorkshopImporter,
    MockVisionExtractor,
    LLMVisionExtractor,
)

__all__ = [
    "DataLoader",
    "CSVLoader",
    "HTMLLoader",
    "JSONLoader",
    "MarkdownLoader",
    "OrgLoader",
    "TextLoader",
    "YAMLLoader",
    # Empathy map support
    "EmpathyMap",
    "EmpathyMapDimension",
    "EmpathyMapLoader",
    "EmpathyMapValidationError",
    "EmpathyMapValidationResult",
    "ParticipantTypeMap",
    # Workshop import
    "WorkshopCategory",
    "PostItNote",
    "WorkshopExtractionResult",
    "WorkshopImportConfig",
    "WorkshopImporter",
    "MockVisionExtractor",
    "LLMVisionExtractor",
]
