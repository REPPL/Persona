"""
Data models for LLM-based persona evaluation.

This module provides Pydantic models for representing evaluation
results from LLM judges.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from persona.core.evaluation.criteria import EvaluationCriteria


class CriterionScore(BaseModel):
    """
    Score for a single evaluation criterion.

    Attributes:
        score: Numerical score from 0.0 to 1.0.
        reasoning: LLM's explanation for the score.
    """

    score: float = Field(..., ge=0.0, le=1.0, description="Score from 0.0 to 1.0")
    reasoning: str = Field(..., description="Explanation for the score")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "score": round(self.score, 3),
            "reasoning": self.reasoning,
        }


class EvaluationResult(BaseModel):
    """
    Complete evaluation result for a single persona.

    Attributes:
        persona_id: ID of the evaluated persona.
        persona_name: Name of the evaluated persona.
        scores: Scores for each evaluated criterion.
        overall_score: Average score across all criteria.
        model: Model used for evaluation.
        provider: Provider used for evaluation.
        evaluated_at: Timestamp of evaluation.
        raw_response: Raw LLM response for debugging.
    """

    persona_id: str = Field(..., description="ID of the evaluated persona")
    persona_name: str | None = Field(None, description="Name of the evaluated persona")
    scores: dict[EvaluationCriteria, CriterionScore] = Field(
        ..., description="Scores for each criterion"
    )
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Average score")
    model: str = Field(..., description="Model used for evaluation")
    provider: str = Field(..., description="Provider used for evaluation")
    evaluated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp of evaluation",
    )
    raw_response: dict[str, Any] | None = Field(
        None, description="Raw LLM response for debugging"
    )

    def get_score(self, criterion: EvaluationCriteria) -> float | None:
        """Get score for a specific criterion."""
        criterion_score = self.scores.get(criterion)
        return criterion_score.score if criterion_score else None

    def get_reasoning(self, criterion: EvaluationCriteria) -> str | None:
        """Get reasoning for a specific criterion."""
        criterion_score = self.scores.get(criterion)
        return criterion_score.reasoning if criterion_score else None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "scores": {
                criterion.value: score.to_dict()
                for criterion, score in self.scores.items()
            },
            "overall_score": round(self.overall_score, 3),
            "model": self.model,
            "provider": self.provider,
            "evaluated_at": self.evaluated_at,
        }


class BatchEvaluationResult(BaseModel):
    """
    Evaluation results for multiple personas.

    Attributes:
        results: Individual evaluation results.
        average_overall: Mean overall score across all personas.
        average_by_criterion: Mean scores for each criterion.
        model: Model used for evaluation.
        provider: Provider used for evaluation.
        evaluated_at: Timestamp of evaluation.
    """

    results: list[EvaluationResult] = Field(..., description="Individual results")
    average_overall: float = Field(..., ge=0.0, le=1.0, description="Mean overall score")
    average_by_criterion: dict[EvaluationCriteria, float] = Field(
        ..., description="Mean scores by criterion"
    )
    model: str = Field(..., description="Model used for evaluation")
    provider: str = Field(..., description="Provider used for evaluation")
    evaluated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp of evaluation",
    )

    @property
    def persona_count(self) -> int:
        """Get number of personas evaluated."""
        return len(self.results)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_count": len(self.results),
            "average_overall": round(self.average_overall, 3),
            "average_by_criterion": {
                criterion.value: round(score, 3)
                for criterion, score in self.average_by_criterion.items()
            },
            "model": self.model,
            "provider": self.provider,
            "evaluated_at": self.evaluated_at,
            "results": [result.to_dict() for result in self.results],
        }
