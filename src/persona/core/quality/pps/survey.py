"""
PPS (Persona Perceived Similarity) survey generator.

This module provides tools to generate human evaluation surveys for
assessing how well personas align with perceived user segments.
"""

from dataclasses import dataclass, field
from typing import Any

from persona.core.generation.parser import Persona
from persona.core.quality.pps.templates import (
    PpsDimension,
    QuestionType,
    SurveyQuestion,
    get_comprehensive_pps_survey,
    get_minimal_pps_survey,
    get_standard_questions,
)


@dataclass
class PpsSurvey:
    """
    A complete PPS survey for persona evaluation.

    Attributes:
        persona_id: ID of the persona being evaluated.
        persona_name: Name of the persona being evaluated.
        questions: List of survey questions.
        instructions: Survey instructions for participants.
        estimated_time_minutes: Estimated completion time.
        metadata: Additional survey metadata.
    """

    persona_id: str
    persona_name: str
    questions: list[SurveyQuestion]
    instructions: str = ""
    estimated_time_minutes: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set default instructions if not provided."""
        if not self.instructions:
            self.instructions = self._generate_default_instructions()

        # Calculate estimated time (1 minute per 2 questions)
        if self.estimated_time_minutes == 5:  # Default not changed
            self.estimated_time_minutes = max(3, len(self.questions) // 2)

    def _generate_default_instructions(self) -> str:
        """Generate default survey instructions."""
        return f"""
Please evaluate the following persona: {self.persona_name}

Read the persona carefully and answer each question based on your impression.
There are no right or wrong answers - we want your honest assessment.

This survey will take approximately {self.estimated_time_minutes} minutes to complete.
""".strip()

    @property
    def question_count(self) -> int:
        """Get total number of questions."""
        return len(self.questions)

    def get_questions_by_dimension(
        self, dimension: PpsDimension
    ) -> list[SurveyQuestion]:
        """
        Get all questions for a specific dimension.

        Args:
            dimension: The PPS dimension to filter by.

        Returns:
            List of questions for that dimension.
        """
        return [q for q in self.questions if q.dimension == dimension]

    def get_questions_by_type(
        self, question_type: QuestionType
    ) -> list[SurveyQuestion]:
        """
        Get all questions of a specific type.

        Args:
            question_type: The question type to filter by.

        Returns:
            List of questions of that type.
        """
        return [q for q in self.questions if q.question_type == question_type]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "question_count": self.question_count,
            "estimated_time_minutes": self.estimated_time_minutes,
            "instructions": self.instructions,
            "questions": [q.to_dict() for q in self.questions],
            "metadata": self.metadata,
        }


class PpsSurveyGenerator:
    """
    Generator for PPS surveys.

    Creates customised surveys for evaluating personas with human participants.

    Example:
        generator = PpsSurveyGenerator()
        survey = generator.generate_for_persona(
            persona=my_persona,
            survey_type="minimal",
        )
        print(f"Survey has {survey.question_count} questions")
    """

    def generate_for_persona(
        self,
        persona: Persona,
        survey_type: str = "comprehensive",
        dimensions: list[PpsDimension] | None = None,
        custom_questions: list[SurveyQuestion] | None = None,
        instructions: str | None = None,
    ) -> PpsSurvey:
        """
        Generate a PPS survey for a persona.

        Args:
            persona: The persona to create a survey for.
            survey_type: Type of survey - "minimal", "comprehensive", or "custom".
            dimensions: Specific dimensions to include (for custom surveys).
            custom_questions: Additional custom questions to include.
            instructions: Custom survey instructions.

        Returns:
            PpsSurvey ready to deploy.

        Raises:
            ValueError: If survey_type is invalid or required parameters missing.
        """
        # Select questions based on survey type
        if survey_type == "minimal":
            questions = get_minimal_pps_survey()
        elif survey_type == "comprehensive":
            questions = get_comprehensive_pps_survey()
        elif survey_type == "custom":
            if not dimensions and not custom_questions:
                raise ValueError(
                    "Custom survey requires either dimensions or custom_questions"
                )
            questions = get_standard_questions(dimensions) if dimensions else []
        else:
            raise ValueError(
                f"Invalid survey_type: {survey_type}. "
                f"Must be 'minimal', 'comprehensive', or 'custom'"
            )

        # Add custom questions if provided
        if custom_questions:
            questions.extend(custom_questions)

        # Create survey
        return PpsSurvey(
            persona_id=persona.id,
            persona_name=persona.name,
            questions=questions,
            instructions=instructions or "",
            metadata={
                "survey_type": survey_type,
                "generated_for_persona": persona.id,
            },
        )

    def generate_for_personas(
        self,
        personas: list[Persona],
        survey_type: str = "comprehensive",
        dimensions: list[PpsDimension] | None = None,
        custom_questions: list[SurveyQuestion] | None = None,
        instructions: str | None = None,
    ) -> list[PpsSurvey]:
        """
        Generate PPS surveys for multiple personas.

        Args:
            personas: List of personas to create surveys for.
            survey_type: Type of survey.
            dimensions: Specific dimensions to include.
            custom_questions: Additional custom questions.
            instructions: Custom survey instructions.

        Returns:
            List of PpsSurvey objects, one per persona.
        """
        return [
            self.generate_for_persona(
                persona=persona,
                survey_type=survey_type,
                dimensions=dimensions,
                custom_questions=custom_questions,
                instructions=instructions,
            )
            for persona in personas
        ]


def generate_pps_survey(
    persona: Persona, survey_type: str = "comprehensive", **kwargs: Any
) -> PpsSurvey:
    """
    Convenience function to generate a PPS survey.

    Args:
        persona: The persona to create a survey for.
        survey_type: Type of survey - "minimal", "comprehensive", or "custom".
        **kwargs: Additional parameters passed to PpsSurveyGenerator.

    Returns:
        PpsSurvey ready to deploy.
    """
    generator = PpsSurveyGenerator()
    return generator.generate_for_persona(persona, survey_type, **kwargs)
