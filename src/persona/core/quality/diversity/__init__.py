"""
Lexical diversity analysis for personas.

This package provides comprehensive lexical diversity metrics to assess
the richness and variety of vocabulary used in generated personas.

Metrics include:
- TTR (Type-Token Ratio): Basic unique word ratio
- MATTR (Moving-Average Type-Token Ratio): Window-based TTR
- MTLD (Measure of Textual Lexical Diversity): Bidirectional factor-based
- Hapax Ratio: Proportion of words appearing exactly once
"""

from persona.core.quality.diversity.analyser import LexicalDiversityAnalyser
from persona.core.quality.diversity.models import (
    BatchDiversityReport,
    DiversityConfig,
    DiversityReport,
    InterpretationLevel,
)

__all__ = [
    "LexicalDiversityAnalyser",
    "DiversityConfig",
    "DiversityReport",
    "BatchDiversityReport",
    "InterpretationLevel",
]
