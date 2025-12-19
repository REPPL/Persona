"""
Pipeline stages for hybrid persona generation.

This module provides the individual stages of the hybrid pipeline:
- Draft: Generate initial personas using local models
- Filter: Evaluate quality using PersonaJudge
- Refine: Improve low-quality personas using frontier models

Also provides base classes for creating custom pipeline stages.
"""

from persona.core.hybrid.stages.base import (
    PipelineContext,
    PipelineStage,
    StageInput,
    StageOutput,
)
from persona.core.hybrid.stages.draft import draft_personas
from persona.core.hybrid.stages.filter import filter_personas
from persona.core.hybrid.stages.refine import refine_personas

__all__ = [
    # Base classes
    "PipelineStage",
    "StageInput",
    "StageOutput",
    "PipelineContext",
    # Stage functions (legacy interface)
    "draft_personas",
    "filter_personas",
    "refine_personas",
]
