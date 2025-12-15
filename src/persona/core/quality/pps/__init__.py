"""
PPS (Persona Perceived Similarity) survey tools.

This package provides tools for generating human evaluation surveys to
assess how well personas align with perceived user segments.

Example:
    from persona.core.quality.pps import generate_pps_survey

    survey = generate_pps_survey(
        persona=my_persona,
        survey_type="minimal",
    )
    print(f"Survey has {survey.question_count} questions")
"""

from persona.core.quality.pps.survey import (
    PpsSurvey,
    PpsSurveyGenerator,
    generate_pps_survey,
)
from persona.core.quality.pps.templates import (
    PpsDimension,
    QuestionType,
    SurveyQuestion,
    get_comprehensive_pps_survey,
    get_minimal_pps_survey,
    get_standard_questions,
)

__all__ = [
    # Survey generation
    "PpsSurvey",
    "PpsSurveyGenerator",
    "generate_pps_survey",
    # Templates
    "SurveyQuestion",
    "PpsDimension",
    "QuestionType",
    "get_standard_questions",
    "get_minimal_pps_survey",
    "get_comprehensive_pps_survey",
]
