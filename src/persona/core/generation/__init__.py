"""
Persona generation pipeline module.

This module provides the core generation pipeline that orchestrates
data loading, prompt rendering, LLM calls, and output parsing.
"""

from persona.core.generation.pipeline import (
    GenerationPipeline,
    GenerationConfig,
    GenerationResult,
)
from persona.core.generation.parser import PersonaParser, Persona

__all__ = [
    "GenerationPipeline",
    "GenerationConfig",
    "GenerationResult",
    "PersonaParser",
    "Persona",
]
