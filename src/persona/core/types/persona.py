"""
TypedDict definitions for persona data structures.

This module provides type-safe dictionary definitions for persona
data used throughout the hybrid pipeline and quality modules.

Example:
    from persona.core.types import PersonaDict

    def process_persona(persona: PersonaDict) -> None:
        # IDE autocomplete works for persona fields
        name = persona["name"]
        goals = persona["goals"]
"""

from typing import Any, NotRequired, TypedDict


class PersonaDict(TypedDict, total=False):
    """
    Base typed dictionary for persona data.

    This is the core persona structure used throughout the application.
    All fields except 'id' and 'name' are optional.

    Attributes:
        id: Unique identifier for the persona.
        name: Full name of the persona.
        age: Age of the persona.
        occupation: Job title or profession.
        background: Brief background paragraph.
        goals: List of goals or objectives.
        pain_points: List of frustrations or challenges.
        behaviours: List of typical behaviours.
        motivations: List of motivations or drivers.
        quote: A characteristic quote from the persona.
        demographics: Additional demographic information.
    """

    id: str
    name: str
    age: NotRequired[int]
    occupation: NotRequired[str]
    background: NotRequired[str]
    goals: NotRequired[list[str]]
    pain_points: NotRequired[list[str]]
    behaviours: NotRequired[list[str]]
    motivations: NotRequired[list[str]]
    quote: NotRequired[str]
    demographics: NotRequired[dict[str, Any]]


class DraftPersonaDict(PersonaDict):
    """
    Persona dictionary from the draft stage.

    Extends PersonaDict with metadata from initial generation.

    Attributes:
        _batch_idx: Batch index during generation.
        _generation_order: Order within the batch.
    """

    _batch_idx: NotRequired[int]
    _generation_order: NotRequired[int]


class EvaluationScoreDict(TypedDict, total=False):
    """
    Individual evaluation criterion score.

    Attributes:
        score: Numeric score (0.0-1.0).
        reasoning: Explanation for the score.
    """

    score: float
    reasoning: NotRequired[str]


class EvaluationResultDict(TypedDict, total=False):
    """
    Complete evaluation result from PersonaJudge.

    Attributes:
        overall_score: Overall quality score (0.0-1.0).
        scores: Per-criterion scores.
        feedback: General feedback.
        recommendations: Improvement recommendations.
    """

    overall_score: float
    scores: NotRequired[dict[str, EvaluationScoreDict]]
    feedback: NotRequired[str]
    recommendations: NotRequired[list[str]]


class EvaluatedPersonaDict(PersonaDict):
    """
    Persona dictionary after quality evaluation.

    Extends PersonaDict with evaluation metadata from the filter stage.

    Attributes:
        _evaluation: Evaluation result from PersonaJudge.
        _evaluation_error: Error message if evaluation failed.
    """

    _evaluation: NotRequired[EvaluationResultDict]
    _evaluation_error: NotRequired[str]


class RefinedPersonaDict(EvaluatedPersonaDict):
    """
    Persona dictionary after frontier model refinement.

    Extends EvaluatedPersonaDict with refinement metadata.

    Attributes:
        _refined: Flag indicating this persona was refined.
        _original_id: Original persona ID before refinement.
        _refinement_error: Error message if refinement failed.
        _refinement_notes: Notes about changes made during refinement.
        quality_score: Final quality score after refinement.
    """

    _refined: NotRequired[bool]
    _original_id: NotRequired[str]
    _refinement_error: NotRequired[str]
    _refinement_notes: NotRequired[str]
    quality_score: NotRequired[float]
