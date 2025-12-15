"""
Unit tests for evaluation models.
"""

import pytest
from datetime import datetime

from persona.core.evaluation.criteria import EvaluationCriteria
from persona.core.evaluation.models import (
    CriterionScore,
    EvaluationResult,
    BatchEvaluationResult,
)


class TestCriterionScore:
    """Test CriterionScore model."""

    def test_create_criterion_score(self):
        """Test creating a criterion score."""
        score = CriterionScore(score=0.85, reasoning="Good coherence")

        assert score.score == 0.85
        assert score.reasoning == "Good coherence"

    def test_score_validation(self):
        """Test score validation (0.0 to 1.0)."""
        # Valid scores
        CriterionScore(score=0.0, reasoning="Minimum")
        CriterionScore(score=1.0, reasoning="Maximum")
        CriterionScore(score=0.5, reasoning="Middle")

        # Invalid scores
        with pytest.raises(Exception):  # Pydantic validation error
            CriterionScore(score=-0.1, reasoning="Below minimum")

        with pytest.raises(Exception):
            CriterionScore(score=1.1, reasoning="Above maximum")

    def test_to_dict(self):
        """Test conversion to dictionary."""
        score = CriterionScore(score=0.856, reasoning="Test reasoning")
        data = score.to_dict()

        assert data["score"] == 0.856
        assert data["reasoning"] == "Test reasoning"


class TestEvaluationResult:
    """Test EvaluationResult model."""

    def test_create_evaluation_result(self):
        """Test creating an evaluation result."""
        scores = {
            EvaluationCriteria.COHERENCE: CriterionScore(
                score=0.85, reasoning="Good coherence"
            ),
            EvaluationCriteria.REALISM: CriterionScore(
                score=0.78, reasoning="Believable"
            ),
        }

        result = EvaluationResult(
            persona_id="p1",
            persona_name="Test Persona",
            scores=scores,
            overall_score=0.815,
            model="qwen2.5:72b",
            provider="ollama",
        )

        assert result.persona_id == "p1"
        assert result.persona_name == "Test Persona"
        assert len(result.scores) == 2
        assert result.overall_score == 0.815
        assert result.model == "qwen2.5:72b"
        assert result.provider == "ollama"
        assert result.evaluated_at  # Should be auto-generated

    def test_get_score(self):
        """Test getting score for specific criterion."""
        scores = {
            EvaluationCriteria.COHERENCE: CriterionScore(
                score=0.85, reasoning="Good"
            ),
        }

        result = EvaluationResult(
            persona_id="p1",
            scores=scores,
            overall_score=0.85,
            model="test",
            provider="test",
        )

        assert result.get_score(EvaluationCriteria.COHERENCE) == 0.85
        assert result.get_score(EvaluationCriteria.REALISM) is None

    def test_get_reasoning(self):
        """Test getting reasoning for specific criterion."""
        scores = {
            EvaluationCriteria.COHERENCE: CriterionScore(
                score=0.85, reasoning="Good coherence"
            ),
        }

        result = EvaluationResult(
            persona_id="p1",
            scores=scores,
            overall_score=0.85,
            model="test",
            provider="test",
        )

        assert result.get_reasoning(EvaluationCriteria.COHERENCE) == "Good coherence"
        assert result.get_reasoning(EvaluationCriteria.REALISM) is None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        scores = {
            EvaluationCriteria.COHERENCE: CriterionScore(
                score=0.85, reasoning="Good"
            ),
        }

        result = EvaluationResult(
            persona_id="p1",
            persona_name="Test",
            scores=scores,
            overall_score=0.85,
            model="test",
            provider="test",
        )

        data = result.to_dict()

        assert data["persona_id"] == "p1"
        assert data["persona_name"] == "Test"
        assert "coherence" in data["scores"]
        assert data["overall_score"] == 0.85
        assert data["model"] == "test"
        assert data["provider"] == "test"


class TestBatchEvaluationResult:
    """Test BatchEvaluationResult model."""

    def test_create_batch_result(self):
        """Test creating a batch evaluation result."""
        result1 = EvaluationResult(
            persona_id="p1",
            scores={
                EvaluationCriteria.COHERENCE: CriterionScore(
                    score=0.85, reasoning="Good"
                )
            },
            overall_score=0.85,
            model="test",
            provider="test",
        )

        result2 = EvaluationResult(
            persona_id="p2",
            scores={
                EvaluationCriteria.COHERENCE: CriterionScore(
                    score=0.75, reasoning="OK"
                )
            },
            overall_score=0.75,
            model="test",
            provider="test",
        )

        batch = BatchEvaluationResult(
            results=[result1, result2],
            average_overall=0.80,
            average_by_criterion={EvaluationCriteria.COHERENCE: 0.80},
            model="test",
            provider="test",
        )

        assert batch.persona_count == 2
        assert len(batch.results) == 2
        assert batch.average_overall == 0.80
        assert batch.average_by_criterion[EvaluationCriteria.COHERENCE] == 0.80

    def test_persona_count(self):
        """Test persona_count property."""
        batch = BatchEvaluationResult(
            results=[],
            average_overall=0.0,
            average_by_criterion={},
            model="test",
            provider="test",
        )
        assert batch.persona_count == 0

        result = EvaluationResult(
            persona_id="p1",
            scores={},
            overall_score=0.8,
            model="test",
            provider="test",
        )
        batch = BatchEvaluationResult(
            results=[result],
            average_overall=0.8,
            average_by_criterion={},
            model="test",
            provider="test",
        )
        assert batch.persona_count == 1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = EvaluationResult(
            persona_id="p1",
            scores={
                EvaluationCriteria.COHERENCE: CriterionScore(
                    score=0.85, reasoning="Good"
                )
            },
            overall_score=0.85,
            model="test",
            provider="test",
        )

        batch = BatchEvaluationResult(
            results=[result],
            average_overall=0.85,
            average_by_criterion={EvaluationCriteria.COHERENCE: 0.85},
            model="test",
            provider="test",
        )

        data = batch.to_dict()

        assert data["persona_count"] == 1
        assert data["average_overall"] == 0.85
        assert "coherence" in data["average_by_criterion"]
        assert len(data["results"]) == 1
