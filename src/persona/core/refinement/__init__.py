"""
Interactive persona refinement module.

This module provides functionality for iteratively refining
personas through natural language instructions.
"""

from persona.core.refinement.refiner import (
    PersonaRefiner,
    RefinementHistory,
    RefinementInstruction,
    RefinementResult,
    RefinementSession,
)

__all__ = [
    "PersonaRefiner",
    "RefinementSession",
    "RefinementInstruction",
    "RefinementResult",
    "RefinementHistory",
]
