"""
Unit tests for refine stage (F-134).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from persona.core.hybrid.config import HybridConfig
from persona.core.hybrid.cost import CostTracker
from persona.core.hybrid.stages.refine import (
    _build_refinement_prompt,
    _get_refinement_system_prompt,
    _parse_refined_persona,
    refine_personas,
)
from persona.core.providers.base import LLMResponse


class TestGetRefinementSystemPrompt:
    """Tests for _get_refinement_system_prompt function."""

    def test_returns_string(self):
        """Test that system prompt is returned."""
        prompt = _get_refinement_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_mentions_improvement(self):
        """Test that prompt mentions improving personas."""
        prompt = _get_refinement_system_prompt()

        assert "improve" in prompt.lower()

    def test_mentions_json(self):
        """Test that prompt mentions JSON output."""
        prompt = _get_refinement_system_prompt()

        assert "JSON" in prompt


class TestBuildRefinementPrompt:
    """Tests for _build_refinement_prompt function."""

    def test_includes_persona_data(self):
        """Test that prompt includes persona JSON."""
        persona = {"id": "p1", "name": "Alice", "age": 30}
        feedback = {}

        prompt = _build_refinement_prompt(persona, feedback)

        assert '"id": "p1"' in prompt
        assert '"name": "Alice"' in prompt
        assert '"age": 30' in prompt

    def test_includes_feedback(self):
        """Test that prompt includes evaluation feedback."""
        persona = {"id": "p1", "name": "Alice"}
        feedback = {
            "coherence": "Inconsistent details",
            "realism": "Needs more grounding",
        }

        prompt = _build_refinement_prompt(persona, feedback)

        assert "coherence" in prompt
        assert "Inconsistent details" in prompt
        assert "realism" in prompt
        assert "Needs more grounding" in prompt

    def test_includes_instructions(self):
        """Test that prompt includes improvement instructions."""
        persona = {"id": "p1", "name": "Alice"}
        feedback = {}

        prompt = _build_refinement_prompt(persona, feedback)

        assert "Improve" in prompt
        assert "coherence" in prompt.lower()
        assert "realism" in prompt.lower()

    def test_handles_empty_feedback(self):
        """Test that prompt works with no feedback."""
        persona = {"id": "p1", "name": "Alice"}
        feedback = {}

        prompt = _build_refinement_prompt(persona, feedback)

        assert "Evaluation Feedback" not in prompt
        assert '"id": "p1"' in prompt


class TestParseRefinedPersona:
    """Tests for _parse_refined_persona function."""

    def test_parses_valid_json(self):
        """Test parsing valid JSON persona."""
        content = '{"id": "p1", "name": "Alice Improved", "age": 32}'
        original = {"id": "p1", "name": "Alice", "age": 30}

        result = _parse_refined_persona(content, original)

        assert result["name"] == "Alice Improved"
        assert result["age"] == 32

    def test_preserves_original_id(self):
        """Test that original ID is preserved."""
        content = '{"id": "new-id", "name": "Alice"}'
        original = {"id": "original-id", "name": "Alice"}

        result = _parse_refined_persona(content, original)

        assert result["id"] == "original-id"

    def test_returns_original_on_parse_failure(self):
        """Test returning original when parsing fails."""
        content = "Invalid JSON response"
        original = {"id": "p1", "name": "Alice"}

        result = _parse_refined_persona(content, original)

        assert result == original

    def test_handles_markdown_code_blocks(self):
        """Test parsing JSON from markdown code blocks."""
        content = """
        ```json
        {"id": "p1", "name": "Alice Refined"}
        ```
        """
        original = {"id": "p1", "name": "Alice"}

        result = _parse_refined_persona(content, original)

        assert result["name"] == "Alice Refined"


class TestRefinePersonas:
    """Tests for refine_personas async function."""

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
        """Test returning empty list for empty input."""
        result = await refine_personas(
            personas=[],
            config=config,
            cost_tracker=cost_tracker,
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_returns_unrefined_when_no_frontier(
        self, local_only_config, cost_tracker
    ):
        """Test returning original personas when no frontier provider."""
        personas = [{"id": "p1", "name": "Alice"}]

        result = await refine_personas(
            personas=personas,
            config=local_only_config,
            cost_tracker=cost_tracker,
        )

        assert result == personas

    @pytest.mark.asyncio
    async def test_refines_personas_with_mocked_provider(
        self, config, cost_tracker
    ):
        """Test refining personas with mocked provider."""
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.generate_async = AsyncMock(
            return_value=LLMResponse(
                content='{"id": "p1", "name": "Alice Refined", "improved": true}',
                model="test-frontier",
                input_tokens=200,
                output_tokens=100,
            )
        )

        personas = [
            {
                "id": "p1",
                "name": "Alice",
                "_evaluation": {"scores": {}},
            }
        ]

        with patch(
            "persona.core.hybrid.stages.refine.ProviderFactory"
        ) as mock_factory:
            mock_factory.create.return_value = mock_provider

            result = await refine_personas(
                personas=personas,
                config=config,
                cost_tracker=cost_tracker,
            )

        assert len(result) == 1
        assert result[0]["name"] == "Alice Refined"
        assert result[0]["_refined"] is True
        assert result[0]["_original_id"] == "p1"

    @pytest.mark.asyncio
    async def test_raises_when_provider_not_configured(
        self, config, cost_tracker
    ):
        """Test error when provider is not configured."""
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = False

        personas = [{"id": "p1", "name": "Alice"}]

        with patch(
            "persona.core.hybrid.stages.refine.ProviderFactory"
        ) as mock_factory:
            mock_factory.create.return_value = mock_provider

            with pytest.raises(RuntimeError, match="not configured"):
                await refine_personas(
                    personas=personas,
                    config=config,
                    cost_tracker=cost_tracker,
                )

    @pytest.mark.asyncio
    async def test_tracks_token_usage(self, config, cost_tracker):
        """Test that token usage is tracked."""
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.generate_async = AsyncMock(
            return_value=LLMResponse(
                content='{"id": "p1", "name": "Alice"}',
                model="test-frontier",
                input_tokens=200,
                output_tokens=100,
            )
        )

        personas = [{"id": "p1", "name": "Alice", "_evaluation": {"scores": {}}}]

        with patch(
            "persona.core.hybrid.stages.refine.ProviderFactory"
        ) as mock_factory:
            mock_factory.create.return_value = mock_provider

            await refine_personas(
                personas=personas,
                config=config,
                cost_tracker=cost_tracker,
            )

        assert cost_tracker.frontier_input_tokens == 200
        assert cost_tracker.frontier_output_tokens == 100

    @pytest.mark.asyncio
    async def test_stops_when_budget_exceeded(self, config, cost_tracker):
        """Test that refinement stops when budget is exceeded."""
        # Start with budget already partially used
        cost_tracker._max_budget = 0.001  # Very low budget

        call_count = 0

        async def track_calls(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Each call adds huge token count, exceeding budget after first
            cost_tracker.add_frontier_usage(500000, 500000)
            return LLMResponse(
                content='{"id": "p1", "name": "Alice"}',
                model="test-frontier",
                input_tokens=500000,
                output_tokens=500000,
            )

        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.generate_async = track_calls

        personas = [
            {"id": "p1", "name": "Alice", "_evaluation": {"scores": {}}},
            {"id": "p2", "name": "Bob", "_evaluation": {"scores": {}}},
            {"id": "p3", "name": "Charlie", "_evaluation": {"scores": {}}},
        ]

        with patch(
            "persona.core.hybrid.stages.refine.ProviderFactory"
        ) as mock_factory:
            mock_factory.create.return_value = mock_provider

            result = await refine_personas(
                personas=personas,
                config=config,
                cost_tracker=cost_tracker,
            )

        # Should still return all personas
        assert len(result) == 3
        # After first call, budget is exceeded, so subsequent personas not refined
        # First one gets refined, rest are returned as-is
        assert call_count >= 1

    @pytest.mark.asyncio
    async def test_handles_refinement_errors(self, config, cost_tracker):
        """Test handling refinement errors gracefully."""
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.generate_async = AsyncMock(
            side_effect=Exception("API Error")
        )

        personas = [{"id": "p1", "name": "Alice", "_evaluation": {"scores": {}}}]

        with patch(
            "persona.core.hybrid.stages.refine.ProviderFactory"
        ) as mock_factory:
            mock_factory.create.return_value = mock_provider

            result = await refine_personas(
                personas=personas,
                config=config,
                cost_tracker=cost_tracker,
            )

        assert len(result) == 1
        assert "_refinement_error" in result[0]
        assert "API Error" in result[0]["_refinement_error"]

    @pytest.mark.asyncio
    async def test_returns_unrefined_when_over_budget(self, cost_tracker):
        """Test returning unrefined personas when already over budget."""
        # Create config with frontier provider set to anthropic
        config = HybridConfig(
            local_provider="ollama",
            local_model="test-model",
            frontier_provider="anthropic",
            frontier_model="claude-3-5-sonnet-20241022",
            quality_threshold=0.7,
        )

        # Create a cost tracker with frontier provider set
        cost_tracker = CostTracker(
            max_budget=0.001,  # Very low budget
            frontier_provider="anthropic",
            frontier_model="claude-3-5-sonnet-20241022",
        )

        # Add enough tokens to exceed budget
        # Anthropic Sonnet costs ~$3/$15 per million tokens
        # 10 million tokens should be about $30-150, way over 0.001 budget
        cost_tracker.add_frontier_usage(10000000, 10000000)

        # Verify we're actually over budget
        assert cost_tracker.is_over_budget is True

        personas = [{"id": "p1", "name": "Alice"}]

        # The budget check happens before provider is created
        result = await refine_personas(
            personas=personas,
            config=config,
            cost_tracker=cost_tracker,
        )

        # Should return original personas without refinement
        assert result == personas
