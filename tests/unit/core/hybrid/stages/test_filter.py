"""
Unit tests for filter stage (F-134).
"""

from unittest.mock import MagicMock, patch

import pytest

from persona.core.hybrid.config import HybridConfig
from persona.core.hybrid.cost import CostTracker
from persona.core.hybrid.stages.filter import (
    filter_personas,
    get_evaluation_feedback,
    get_evaluation_score,
)


class TestGetEvaluationScore:
    """Tests for get_evaluation_score function."""

    def test_returns_score_when_present(self):
        """Test returning evaluation score."""
        persona = {
            "id": "p1",
            "name": "Alice",
            "_evaluation": {"overall_score": 0.85},
        }

        score = get_evaluation_score(persona)
        assert score == 0.85

    def test_returns_zero_when_no_evaluation(self):
        """Test returning 0.0 when no evaluation."""
        persona = {"id": "p1", "name": "Alice"}

        score = get_evaluation_score(persona)
        assert score == 0.0

    def test_returns_zero_when_no_overall_score(self):
        """Test returning 0.0 when no overall_score in evaluation."""
        persona = {
            "id": "p1",
            "name": "Alice",
            "_evaluation": {"scores": {}},
        }

        score = get_evaluation_score(persona)
        assert score == 0.0


class TestGetEvaluationFeedback:
    """Tests for get_evaluation_feedback function."""

    def test_extracts_feedback_from_scores(self):
        """Test extracting feedback from score reasoning."""
        persona = {
            "id": "p1",
            "_evaluation": {
                "scores": {
                    "coherence": {
                        "score": 0.8,
                        "reasoning": "Good logical flow",
                    },
                    "realism": {
                        "score": 0.6,
                        "reasoning": "Needs more detail",
                    },
                },
            },
        }

        feedback = get_evaluation_feedback(persona)

        assert feedback["coherence"] == "Good logical flow"
        assert feedback["realism"] == "Needs more detail"

    def test_returns_empty_when_no_evaluation(self):
        """Test returning empty dict when no evaluation."""
        persona = {"id": "p1"}

        feedback = get_evaluation_feedback(persona)
        assert feedback == {}

    def test_returns_empty_when_no_scores(self):
        """Test returning empty dict when no scores."""
        persona = {"id": "p1", "_evaluation": {}}

        feedback = get_evaluation_feedback(persona)
        assert feedback == {}

    def test_skips_scores_without_reasoning(self):
        """Test that scores without reasoning are skipped."""
        persona = {
            "id": "p1",
            "_evaluation": {
                "scores": {
                    "coherence": {"score": 0.8},  # No reasoning
                    "realism": {"score": 0.6, "reasoning": "Needs work"},
                },
            },
        }

        feedback = get_evaluation_feedback(persona)

        assert "coherence" not in feedback
        assert feedback["realism"] == "Needs work"

    def test_handles_non_dict_score_data(self):
        """Test handling non-dict score data."""
        persona = {
            "id": "p1",
            "_evaluation": {
                "scores": {
                    "coherence": 0.8,  # Just a number, not a dict
                    "realism": {"score": 0.6, "reasoning": "Needs work"},
                },
            },
        }

        feedback = get_evaluation_feedback(persona)

        assert "coherence" not in feedback
        assert feedback["realism"] == "Needs work"


class TestFilterPersonas:
    """Tests for filter_personas async function."""

    @pytest.fixture
    def config(self):
        """Create test config with hybrid mode."""
        return HybridConfig(
            local_provider="ollama",
            local_model="test-model",
            frontier_provider="anthropic",
            frontier_model="test-frontier",
            quality_threshold=0.7,
        )

    @pytest.fixture
    def local_only_config(self):
        """Create test config without hybrid mode."""
        return HybridConfig(
            local_provider="ollama",
            local_model="test-model",
            frontier_provider=None,
            frontier_model=None,
        )

    @pytest.fixture
    def cost_tracker(self):
        """Create test cost tracker."""
        return CostTracker(max_budget=10.0)

    @pytest.mark.asyncio
    async def test_returns_empty_for_empty_input(self, config, cost_tracker):
        """Test returning empty lists for empty input."""
        passing, needs_work = await filter_personas(
            personas=[],
            config=config,
            cost_tracker=cost_tracker,
        )

        assert passing == []
        assert needs_work == []

    @pytest.mark.asyncio
    async def test_all_pass_in_local_only_mode(
        self, local_only_config, cost_tracker
    ):
        """Test that all personas pass in local-only mode."""
        personas = [
            {"id": "p1", "name": "Alice"},
            {"id": "p2", "name": "Bob"},
        ]

        passing, needs_work = await filter_personas(
            personas=personas,
            config=local_only_config,
            cost_tracker=cost_tracker,
        )

        assert len(passing) == 2
        assert len(needs_work) == 0

    @pytest.mark.asyncio
    async def test_separates_by_quality_threshold(self, config, cost_tracker):
        """Test separating personas by quality threshold."""
        mock_result = MagicMock()
        mock_result.overall_score = 0.8
        mock_result.raw_response = True
        mock_result.to_dict.return_value = {"overall_score": 0.8}

        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = mock_result

        personas = [
            {"id": "p1", "name": "Alice"},
            {"id": "p2", "name": "Bob"},
        ]

        with patch(
            "persona.core.hybrid.stages.filter.PersonaJudge",
            return_value=mock_judge,
        ):
            # First persona passes, second fails
            mock_judge.evaluate.side_effect = [
                MagicMock(
                    overall_score=0.8,
                    raw_response=True,
                    to_dict=lambda: {"overall_score": 0.8},
                ),
                MagicMock(
                    overall_score=0.5,
                    raw_response=True,
                    to_dict=lambda: {"overall_score": 0.5},
                ),
            ]

            passing, needs_work = await filter_personas(
                personas=personas,
                config=config,
                cost_tracker=cost_tracker,
            )

        assert len(passing) == 1
        assert len(needs_work) == 1
        assert passing[0]["id"] == "p1"
        assert needs_work[0]["id"] == "p2"

    @pytest.mark.asyncio
    async def test_adds_evaluation_to_personas(self, config, cost_tracker):
        """Test that evaluation results are added to personas."""
        mock_result = MagicMock()
        mock_result.overall_score = 0.8
        mock_result.raw_response = True
        mock_result.to_dict.return_value = {
            "overall_score": 0.8,
            "scores": {},
        }

        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = mock_result

        personas = [{"id": "p1", "name": "Alice"}]

        with patch(
            "persona.core.hybrid.stages.filter.PersonaJudge",
            return_value=mock_judge,
        ):
            passing, needs_work = await filter_personas(
                personas=personas,
                config=config,
                cost_tracker=cost_tracker,
            )

        assert "_evaluation" in passing[0]
        assert passing[0]["_evaluation"]["overall_score"] == 0.8

    @pytest.mark.asyncio
    async def test_handles_evaluation_errors(self, config, cost_tracker):
        """Test handling evaluation errors gracefully."""
        mock_judge = MagicMock()
        mock_judge.evaluate.side_effect = Exception("API Error")

        personas = [{"id": "p1", "name": "Alice"}]

        with patch(
            "persona.core.hybrid.stages.filter.PersonaJudge",
            return_value=mock_judge,
        ):
            passing, needs_work = await filter_personas(
                personas=personas,
                config=config,
                cost_tracker=cost_tracker,
            )

        # On error, persona should go to needs_work
        assert len(passing) == 0
        assert len(needs_work) == 1
        assert "_evaluation_error" in needs_work[0]

    @pytest.mark.asyncio
    async def test_tracks_token_usage(self, config, cost_tracker):
        """Test that token usage is tracked."""
        mock_result = MagicMock()
        mock_result.overall_score = 0.8
        mock_result.raw_response = True
        mock_result.to_dict.return_value = {"overall_score": 0.8}

        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = mock_result

        personas = [{"id": "p1", "name": "Alice"}]

        with patch(
            "persona.core.hybrid.stages.filter.PersonaJudge",
            return_value=mock_judge,
        ):
            await filter_personas(
                personas=personas,
                config=config,
                cost_tracker=cost_tracker,
            )

        # Check that judge tokens were tracked
        assert cost_tracker.judge_input_tokens > 0 or cost_tracker.judge_output_tokens > 0
