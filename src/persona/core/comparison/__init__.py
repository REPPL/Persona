"""
Persona comparison module.

This module provides functionality for comparing personas
to identify similarities, differences, and overlaps.
"""

from persona.core.comparison.comparator import (
    PersonaComparator,
    ComparisonResult,
    SimilarityScore,
)

__all__ = [
    "PersonaComparator",
    "ComparisonResult",
    "SimilarityScore",
]
