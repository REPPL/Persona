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
from persona.core.generation.variations import (
    ComplexityLevel,
    DetailLevel,
    ComplexitySpec,
    DetailSpec,
    PersonaVariation,
    VariationMatrix,
    VariationResult,
    VariationValidator,
    COMPLEXITY_SPECS,
    DETAIL_SPECS,
    estimate_tokens,
    estimate_cost,
)

__all__ = [
    "GenerationPipeline",
    "GenerationConfig",
    "GenerationResult",
    "PersonaParser",
    "Persona",
    # Variations (F-033, F-034, F-035)
    "ComplexityLevel",
    "DetailLevel",
    "ComplexitySpec",
    "DetailSpec",
    "PersonaVariation",
    "VariationMatrix",
    "VariationResult",
    "VariationValidator",
    "COMPLEXITY_SPECS",
    "DETAIL_SPECS",
    "estimate_tokens",
    "estimate_cost",
]
