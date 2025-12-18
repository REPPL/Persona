"""
Data loading and processing module.

This module provides functionality for loading qualitative research data
from various file formats and preparing it for LLM analysis.
"""

from persona.core.data.attribution import Attribution
from persona.core.data.empathy_map import (
    EmpathyMap,
    EmpathyMapDimension,
    EmpathyMapLoader,
    EmpathyMapValidationError,
    EmpathyMapValidationResult,
    ParticipantTypeMap,
)
from persona.core.data.formats import (
    CSVLoader,
    HTMLLoader,
    JSONLoader,
    MarkdownLoader,
    OrgLoader,
    TextLoader,
    YAMLLoader,
)
from persona.core.data.loader import DataLoader
from persona.core.data.url import (
    SourceType,
    TermsNotAcceptedError,
    URLFetcher,
    URLFetchResult,
    URLSource,
    URLValidationError,
)
from persona.core.data.url_cache import CacheEntry, URLCache
from persona.core.data.workshop import (
    LLMVisionExtractor,
    MockVisionExtractor,
    PostItNote,
    WorkshopCategory,
    WorkshopExtractionResult,
    WorkshopImportConfig,
    WorkshopImporter,
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
    # Attribution
    "Attribution",
    # URL data loading
    "URLFetcher",
    "URLFetchResult",
    "URLSource",
    "URLCache",
    "CacheEntry",
    "SourceType",
    "URLValidationError",
    "TermsNotAcceptedError",
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
