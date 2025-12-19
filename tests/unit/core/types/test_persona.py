"""
Tests for TypedDict persona definitions (F-131).
"""

from typing import get_type_hints

import pytest

from persona.core.types import (
    DraftPersonaDict,
    EvaluatedPersonaDict,
    PersonaDict,
    RefinedPersonaDict,
)
from persona.core.types.persona import EvaluationResultDict, EvaluationScoreDict


class TestPersonaDict:
    """Tests for base PersonaDict."""

    def test_can_create_minimal_persona(self):
        """Test creating persona with minimal fields."""
        persona: PersonaDict = {
            "id": "persona-1",
            "name": "Test User",
        }

        assert persona["id"] == "persona-1"
        assert persona["name"] == "Test User"

    def test_can_create_full_persona(self):
        """Test creating persona with all fields."""
        persona: PersonaDict = {
            "id": "persona-1",
            "name": "Jane Doe",
            "age": 35,
            "occupation": "Software Engineer",
            "background": "Experienced developer with focus on UX",
            "goals": ["Build great products", "Learn new skills"],
            "pain_points": ["Lack of time", "Complex tools"],
            "behaviours": ["Researches before buying", "Uses mobile apps"],
            "motivations": ["Career growth", "Personal satisfaction"],
            "quote": "I want tools that just work",
            "demographics": {"location": "London", "income_level": "high"},
        }

        assert persona["age"] == 35
        assert len(persona["goals"]) == 2
        assert persona["demographics"]["location"] == "London"

    def test_type_hints_are_accessible(self):
        """Test that type hints can be retrieved."""
        hints = get_type_hints(PersonaDict)

        assert "id" in hints
        assert "name" in hints
        assert "age" in hints
        assert "goals" in hints

    def test_persona_is_dict(self):
        """Test that PersonaDict is a valid dict."""
        persona: PersonaDict = {"id": "test", "name": "Test"}

        # Can use dict methods
        assert "id" in persona
        assert persona.get("age") is None
        assert len(persona) == 2


class TestDraftPersonaDict:
    """Tests for DraftPersonaDict."""

    def test_can_create_draft_persona(self):
        """Test creating draft persona with batch metadata."""
        persona: DraftPersonaDict = {
            "id": "draft-1",
            "name": "Draft User",
            "_batch_idx": 0,
            "_generation_order": 1,
        }

        assert persona["_batch_idx"] == 0
        assert persona["_generation_order"] == 1

    def test_inherits_persona_fields(self):
        """Test that DraftPersonaDict includes PersonaDict fields."""
        persona: DraftPersonaDict = {
            "id": "draft-1",
            "name": "Draft User",
            "age": 28,
            "goals": ["Goal 1"],
            "_batch_idx": 0,
        }

        assert persona["age"] == 28
        assert persona["goals"] == ["Goal 1"]


class TestEvaluationScoreDict:
    """Tests for EvaluationScoreDict."""

    def test_can_create_score(self):
        """Test creating evaluation score."""
        score: EvaluationScoreDict = {
            "score": 0.85,
            "reasoning": "Well-structured with clear goals",
        }

        assert score["score"] == 0.85
        assert "reasoning" in score

    def test_score_without_reasoning(self):
        """Test creating score without reasoning."""
        score: EvaluationScoreDict = {
            "score": 0.7,
        }

        assert score["score"] == 0.7
        assert "reasoning" not in score


class TestEvaluationResultDict:
    """Tests for EvaluationResultDict."""

    def test_can_create_result(self):
        """Test creating evaluation result."""
        result: EvaluationResultDict = {
            "overall_score": 0.8,
            "scores": {
                "coherence": {"score": 0.85, "reasoning": "Good coherence"},
                "realism": {"score": 0.75},
            },
            "feedback": "Generally good quality",
            "recommendations": ["Add more specific details"],
        }

        assert result["overall_score"] == 0.8
        assert result["scores"]["coherence"]["score"] == 0.85
        assert len(result["recommendations"]) == 1


class TestEvaluatedPersonaDict:
    """Tests for EvaluatedPersonaDict."""

    def test_can_create_evaluated_persona(self):
        """Test creating persona with evaluation."""
        persona: EvaluatedPersonaDict = {
            "id": "eval-1",
            "name": "Evaluated User",
            "_evaluation": {
                "overall_score": 0.8,
                "scores": {
                    "coherence": {"score": 0.9},
                },
            },
        }

        assert persona["_evaluation"]["overall_score"] == 0.8

    def test_can_have_evaluation_error(self):
        """Test persona with evaluation error."""
        persona: EvaluatedPersonaDict = {
            "id": "eval-2",
            "name": "Error User",
            "_evaluation_error": "Evaluation failed due to timeout",
        }

        assert persona["_evaluation_error"] == "Evaluation failed due to timeout"


class TestRefinedPersonaDict:
    """Tests for RefinedPersonaDict."""

    def test_can_create_refined_persona(self):
        """Test creating refined persona."""
        persona: RefinedPersonaDict = {
            "id": "refined-1",
            "name": "Refined User",
            "_refined": True,
            "_original_id": "draft-1",
            "quality_score": 0.9,
        }

        assert persona["_refined"] is True
        assert persona["_original_id"] == "draft-1"
        assert persona["quality_score"] == 0.9

    def test_can_have_refinement_error(self):
        """Test persona with refinement error."""
        persona: RefinedPersonaDict = {
            "id": "refined-2",
            "name": "Error User",
            "_refinement_error": "API rate limit exceeded",
        }

        assert persona["_refinement_error"] == "API rate limit exceeded"

    def test_inherits_evaluation_fields(self):
        """Test that RefinedPersonaDict includes evaluation fields."""
        persona: RefinedPersonaDict = {
            "id": "refined-3",
            "name": "Full User",
            "_evaluation": {"overall_score": 0.65},
            "_refined": True,
            "_refinement_notes": "Improved coherence and added details",
            "quality_score": 0.85,
        }

        assert persona["_evaluation"]["overall_score"] == 0.65
        assert persona["_refined"] is True
        assert "refinement_notes" not in persona  # Wrong key
        assert persona["_refinement_notes"] == "Improved coherence and added details"


class TestTypeImports:
    """Tests for type imports."""

    def test_can_import_all_types(self):
        """Test that all types are exported."""
        from persona.core.types import (
            DraftPersonaDict,
            EvaluatedPersonaDict,
            PersonaDict,
            RefinedPersonaDict,
        )

        assert PersonaDict is not None
        assert DraftPersonaDict is not None
        assert EvaluatedPersonaDict is not None
        assert RefinedPersonaDict is not None

    def test_persona_module_exports(self):
        """Test persona module __all__ exports."""
        from persona.core.types import persona

        # Check expected exports are present
        assert hasattr(persona, "PersonaDict")
        assert hasattr(persona, "DraftPersonaDict")
        assert hasattr(persona, "EvaluatedPersonaDict")
        assert hasattr(persona, "RefinedPersonaDict")
        assert hasattr(persona, "EvaluationScoreDict")
        assert hasattr(persona, "EvaluationResultDict")
