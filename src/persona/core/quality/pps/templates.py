"""
Survey question templates for PPS (Persona Perceived Similarity) evaluation.

This module provides templates for generating survey questions to assess
how well personas align with human perceptions of real user segments.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class QuestionType(Enum):
    """Types of PPS survey questions."""

    LIKERT_5 = "likert_5"  # 1-5 scale (Strongly Disagree to Strongly Agree)
    LIKERT_7 = "likert_7"  # 1-7 scale
    SEMANTIC_DIFF = "semantic_differential"  # Opposite adjectives
    RANKING = "ranking"  # Rank multiple options
    MULTIPLE_CHOICE = "multiple_choice"  # Select one or more options
    OPEN_ENDED = "open_ended"  # Free text response


class PpsDimension(Enum):
    """Dimensions of PPS evaluation."""

    REALISM = "realism"  # Does this feel like a real person?
    REPRESENTATIVENESS = "representativeness"  # Does this represent the target segment?
    CLARITY = "clarity"  # Is the persona clear and understandable?
    USEFULNESS = "usefulness"  # Would this be useful for design decisions?
    COMPLETENESS = "completeness"  # Does this have sufficient detail?
    BELIEVABILITY = "believability"  # Do the details seem believable?


@dataclass
class SurveyQuestion:
    """
    A single PPS survey question.

    Attributes:
        id: Unique question identifier.
        dimension: PPS dimension being evaluated.
        question_type: Type of question format.
        text: The question text.
        options: Response options (for multiple choice, ranking, etc.).
        scale_labels: Labels for scale endpoints (for Likert, semantic diff).
        persona_field: Persona field being evaluated (optional).
        notes: Additional notes or instructions.
    """

    id: str
    dimension: PpsDimension
    question_type: QuestionType
    text: str
    options: list[str] | None = None
    scale_labels: dict[str, str] | None = None
    persona_field: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        result = {
            "id": self.id,
            "dimension": self.dimension.value,
            "question_type": self.question_type.value,
            "text": self.text,
        }

        if self.options:
            result["options"] = self.options
        if self.scale_labels:
            result["scale_labels"] = self.scale_labels
        if self.persona_field:
            result["persona_field"] = self.persona_field
        if self.notes:
            result["notes"] = self.notes

        return result


# Standard PPS question templates
REALISM_QUESTIONS = [
    SurveyQuestion(
        id="realism_1",
        dimension=PpsDimension.REALISM,
        question_type=QuestionType.LIKERT_7,
        text="This persona feels like a real person I could meet.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Evaluates overall sense of authenticity",
    ),
    SurveyQuestion(
        id="realism_2",
        dimension=PpsDimension.REALISM,
        question_type=QuestionType.LIKERT_7,
        text="The details in this persona are consistent with each other.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Evaluates internal consistency",
    ),
    SurveyQuestion(
        id="realism_3",
        dimension=PpsDimension.REALISM,
        question_type=QuestionType.SEMANTIC_DIFF,
        text="This persona seems:",
        options=["Artificial", "Authentic"],
        scale_labels={"1": "Artificial", "7": "Authentic"},
        notes="Semantic differential for perceived authenticity",
    ),
]

REPRESENTATIVENESS_QUESTIONS = [
    SurveyQuestion(
        id="repr_1",
        dimension=PpsDimension.REPRESENTATIVENESS,
        question_type=QuestionType.LIKERT_7,
        text="This persona accurately represents the target user segment.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Requires knowledge of actual user segment",
    ),
    SurveyQuestion(
        id="repr_2",
        dimension=PpsDimension.REPRESENTATIVENESS,
        question_type=QuestionType.LIKERT_7,
        text="I can recognise real users I know in this persona.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Recognition-based representativeness",
    ),
]

CLARITY_QUESTIONS = [
    SurveyQuestion(
        id="clarity_1",
        dimension=PpsDimension.CLARITY,
        question_type=QuestionType.LIKERT_7,
        text="This persona is easy to understand.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Overall comprehensibility",
    ),
    SurveyQuestion(
        id="clarity_2",
        dimension=PpsDimension.CLARITY,
        question_type=QuestionType.LIKERT_7,
        text="The persona clearly communicates who this person is.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Clarity of identity",
    ),
    SurveyQuestion(
        id="clarity_3",
        dimension=PpsDimension.CLARITY,
        question_type=QuestionType.SEMANTIC_DIFF,
        text="The persona description is:",
        options=["Confusing", "Clear"],
        scale_labels={"1": "Confusing", "7": "Clear"},
        notes="Semantic differential for clarity",
    ),
]

USEFULNESS_QUESTIONS = [
    SurveyQuestion(
        id="useful_1",
        dimension=PpsDimension.USEFULNESS,
        question_type=QuestionType.LIKERT_7,
        text="This persona would be useful for making design decisions.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Practical utility for design",
    ),
    SurveyQuestion(
        id="useful_2",
        dimension=PpsDimension.USEFULNESS,
        question_type=QuestionType.LIKERT_7,
        text="This persona provides actionable insights.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Actionability of insights",
    ),
    SurveyQuestion(
        id="useful_3",
        dimension=PpsDimension.USEFULNESS,
        question_type=QuestionType.LIKERT_7,
        text="I would reference this persona when making product decisions.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Likelihood of actual use",
    ),
]

COMPLETENESS_QUESTIONS = [
    SurveyQuestion(
        id="complete_1",
        dimension=PpsDimension.COMPLETENESS,
        question_type=QuestionType.LIKERT_7,
        text="This persona has sufficient detail for my needs.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Adequate level of detail",
    ),
    SurveyQuestion(
        id="complete_2",
        dimension=PpsDimension.COMPLETENESS,
        question_type=QuestionType.LIKERT_7,
        text="Important information is missing from this persona.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        notes="Reverse-scored: missing information",
    ),
]

BELIEVABILITY_QUESTIONS = [
    SurveyQuestion(
        id="believe_1",
        dimension=PpsDimension.BELIEVABILITY,
        question_type=QuestionType.LIKERT_7,
        text="The goals described in this persona are believable.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        persona_field="goals",
        notes="Believability of specific field: goals",
    ),
    SurveyQuestion(
        id="believe_2",
        dimension=PpsDimension.BELIEVABILITY,
        question_type=QuestionType.LIKERT_7,
        text="The pain points described in this persona are believable.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        persona_field="pain_points",
        notes="Believability of specific field: pain points",
    ),
    SurveyQuestion(
        id="believe_3",
        dimension=PpsDimension.BELIEVABILITY,
        question_type=QuestionType.LIKERT_7,
        text="The behaviours described in this persona are believable.",
        scale_labels={"1": "Strongly Disagree", "7": "Strongly Agree"},
        persona_field="behaviours",
        notes="Believability of specific field: behaviours",
    ),
]

# Standard question sets by dimension
STANDARD_QUESTIONS = {
    PpsDimension.REALISM: REALISM_QUESTIONS,
    PpsDimension.REPRESENTATIVENESS: REPRESENTATIVENESS_QUESTIONS,
    PpsDimension.CLARITY: CLARITY_QUESTIONS,
    PpsDimension.USEFULNESS: USEFULNESS_QUESTIONS,
    PpsDimension.COMPLETENESS: COMPLETENESS_QUESTIONS,
    PpsDimension.BELIEVABILITY: BELIEVABILITY_QUESTIONS,
}


def get_standard_questions(
    dimensions: list[PpsDimension] | None = None,
) -> list[SurveyQuestion]:
    """
    Get standard PPS questions for specified dimensions.

    Args:
        dimensions: List of PPS dimensions to include. If None, includes all.

    Returns:
        List of survey questions.
    """
    if dimensions is None:
        dimensions = list(PpsDimension)

    questions = []
    for dimension in dimensions:
        questions.extend(STANDARD_QUESTIONS.get(dimension, []))

    return questions


def get_minimal_pps_survey() -> list[SurveyQuestion]:
    """
    Get a minimal PPS survey (one question per dimension).

    Returns:
        List of 6 survey questions.
    """
    return [
        REALISM_QUESTIONS[0],
        REPRESENTATIVENESS_QUESTIONS[0],
        CLARITY_QUESTIONS[0],
        USEFULNESS_QUESTIONS[0],
        COMPLETENESS_QUESTIONS[0],
        BELIEVABILITY_QUESTIONS[0],
    ]


def get_comprehensive_pps_survey() -> list[SurveyQuestion]:
    """
    Get a comprehensive PPS survey (all standard questions).

    Returns:
        List of all standard PPS survey questions.
    """
    return get_standard_questions()
