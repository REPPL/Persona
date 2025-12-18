"""Unit tests for hybrid pipeline stages."""


from persona.core.hybrid.stages.filter import (
    get_evaluation_feedback,
    get_evaluation_score,
)


def test_get_evaluation_score_with_evaluation():
    """Test getting evaluation score from persona with evaluation."""
    persona = {
        "id": "p1",
        "name": "Alice",
        "_evaluation": {
            "overall_score": 0.85,
            "scores": {},
        },
    }

    score = get_evaluation_score(persona)
    assert score == 0.85


def test_get_evaluation_score_without_evaluation():
    """Test getting evaluation score from persona without evaluation."""
    persona = {
        "id": "p1",
        "name": "Alice",
    }

    score = get_evaluation_score(persona)
    assert score == 0.0


def test_get_evaluation_feedback_with_feedback():
    """Test getting evaluation feedback from persona."""
    persona = {
        "id": "p1",
        "name": "Alice",
        "_evaluation": {
            "scores": {
                "coherence": {
                    "score": 0.8,
                    "reasoning": "Good consistency",
                },
                "realism": {
                    "score": 0.7,
                    "reasoning": "Could be more realistic",
                },
            },
        },
    }

    feedback = get_evaluation_feedback(persona)

    assert "coherence" in feedback
    assert feedback["coherence"] == "Good consistency"
    assert "realism" in feedback
    assert feedback["realism"] == "Could be more realistic"


def test_get_evaluation_feedback_without_evaluation():
    """Test getting feedback from persona without evaluation."""
    persona = {
        "id": "p1",
        "name": "Alice",
    }

    feedback = get_evaluation_feedback(persona)
    assert feedback == {}


def test_get_evaluation_feedback_empty_scores():
    """Test getting feedback with empty scores."""
    persona = {
        "id": "p1",
        "name": "Alice",
        "_evaluation": {
            "scores": {},
        },
    }

    feedback = get_evaluation_feedback(persona)
    assert feedback == {}


# Note: Full tests for draft_personas, filter_personas, and refine_personas
# would require mocking LLM providers or running against real APIs.
# These are marked with @pytest.mark.real_api in the test suite.
