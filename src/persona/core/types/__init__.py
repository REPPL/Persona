"""
Type definitions for the Persona library.

This module provides TypedDict definitions for type-safe
persona data structures throughout the codebase.
"""

from persona.core.types.persona import (
    DraftPersonaDict,
    EvaluatedPersonaDict,
    PersonaDict,
    RefinedPersonaDict,
)

__all__ = [
    "PersonaDict",
    "DraftPersonaDict",
    "EvaluatedPersonaDict",
    "RefinedPersonaDict",
]
