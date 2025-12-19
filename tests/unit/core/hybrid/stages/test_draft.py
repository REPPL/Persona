"""
Unit tests for draft stage (F-134).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from persona.core.hybrid.config import HybridConfig
from persona.core.hybrid.cost import CostTracker
from persona.core.hybrid.stages.draft import (
    _build_draft_prompt,
    _get_system_prompt,
    _parse_personas,
    draft_personas,
)
from persona.core.providers.base import LLMResponse


class TestBuildDraftPrompt:
    """Tests for _build_draft_prompt function."""

    def test_includes_input_data(self):
        """Test that prompt includes input data."""
        prompt = _build_draft_prompt("User research data here", 5)

        assert "User research data here" in prompt
        assert "Research Data" in prompt

    def test_includes_count(self):
        """Test that prompt includes requested count."""
        prompt = _build_draft_prompt("data", 10)

        assert "10" in prompt
        assert "distinct user personas" in prompt

    def test_includes_json_format(self):
        """Test that prompt includes JSON format instructions."""
        prompt = _build_draft_prompt("data", 3)

        assert "JSON array" in prompt
        assert '"id"' in prompt
        assert '"name"' in prompt
        assert '"goals"' in prompt


class TestGetSystemPrompt:
    """Tests for _get_system_prompt function."""

    def test_returns_string(self):
        """Test that system prompt is returned."""
        prompt = _get_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_mentions_json(self):
        """Test that system prompt mentions JSON output."""
        prompt = _get_system_prompt()

        assert "JSON" in prompt

    def test_mentions_personas(self):
        """Test that system prompt mentions personas."""
        prompt = _get_system_prompt()

        assert "persona" in prompt.lower()


class TestParsePersonas:
    """Tests for _parse_personas function."""

    def test_parses_valid_json_array(self):
        """Test parsing valid JSON array."""
        content = """
        [
            {"id": "p1", "name": "Alice", "age": 30},
            {"id": "p2", "name": "Bob", "age": 25}
        ]
        """

        personas = _parse_personas(content)

        assert len(personas) == 2
        assert personas[0]["name"] == "Alice"
        assert personas[1]["name"] == "Bob"

    def test_handles_markdown_code_blocks(self):
        """Test parsing JSON from markdown code blocks."""
        content = """
        ```json
        [
            {"id": "p1", "name": "Alice"}
        ]
        ```
        """

        personas = _parse_personas(content)

        assert len(personas) == 1
        assert personas[0]["name"] == "Alice"

    def test_adds_missing_id(self):
        """Test that missing ID is added."""
        content = '[{"name": "Alice"}]'

        personas = _parse_personas(content, batch_idx=2)

        assert personas[0]["id"] == "persona-2-1"

    def test_adds_missing_name(self):
        """Test that missing name is added."""
        content = '[{"id": "p1"}]'

        personas = _parse_personas(content)

        assert personas[0]["name"] == "User 1"

    def test_handles_empty_response(self):
        """Test handling empty or invalid response."""
        content = ""

        personas = _parse_personas(content)

        assert personas == []

    def test_skips_non_dict_items(self):
        """Test that non-dict items are skipped."""
        content = '[{"id": "p1", "name": "Alice"}, "invalid", 123]'

        personas = _parse_personas(content)

        assert len(personas) == 1
        assert personas[0]["name"] == "Alice"


class TestDraftPersonas:
    """Tests for draft_personas async function."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        return HybridConfig(
            local_provider="ollama",
            local_model="test-model",
            batch_size=5,
        )

    @pytest.fixture
    def cost_tracker(self):
        """Create test cost tracker."""
        return CostTracker(max_budget=10.0)

    @pytest.mark.asyncio
    async def test_generates_personas_with_mocked_provider(
        self, config, cost_tracker
    ):
        """Test persona generation with mocked provider."""
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.generate_async = AsyncMock(
            return_value=LLMResponse(
                content='[{"id": "p1", "name": "Test User"}]',
                model="test-model",
                input_tokens=100,
                output_tokens=50,
            )
        )

        with patch(
            "persona.core.hybrid.stages.draft.ProviderFactory"
        ) as mock_factory:
            mock_factory.create.return_value = mock_provider

            personas = await draft_personas(
                input_data="Test data",
                config=config,
                count=1,
                cost_tracker=cost_tracker,
            )

        assert len(personas) == 1
        assert personas[0]["name"] == "Test User"

    @pytest.mark.asyncio
    async def test_raises_when_provider_not_configured(
        self, config, cost_tracker
    ):
        """Test error when provider is not configured."""
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = False

        with patch(
            "persona.core.hybrid.stages.draft.ProviderFactory"
        ) as mock_factory:
            mock_factory.create.return_value = mock_provider

            with pytest.raises(RuntimeError, match="not configured"):
                await draft_personas(
                    input_data="Test data",
                    config=config,
                    count=1,
                    cost_tracker=cost_tracker,
                )

    @pytest.mark.asyncio
    async def test_respects_batch_size(self, config, cost_tracker):
        """Test that generation respects batch size."""
        config.batch_size = 2

        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.generate_async = AsyncMock(
            return_value=LLMResponse(
                content='[{"id": "p1", "name": "User 1"}, {"id": "p2", "name": "User 2"}]',
                model="test-model",
                input_tokens=100,
                output_tokens=100,
            )
        )

        with patch(
            "persona.core.hybrid.stages.draft.ProviderFactory"
        ) as mock_factory:
            mock_factory.create.return_value = mock_provider

            personas = await draft_personas(
                input_data="Test data",
                config=config,
                count=5,
                cost_tracker=cost_tracker,
            )

        # Should have made multiple calls for batches
        assert mock_provider.generate_async.call_count >= 2

    @pytest.mark.asyncio
    async def test_tracks_token_usage(self, config, cost_tracker):
        """Test that token usage is tracked."""
        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.generate_async = AsyncMock(
            return_value=LLMResponse(
                content='[{"id": "p1", "name": "Test"}]',
                model="test-model",
                input_tokens=100,
                output_tokens=50,
            )
        )

        with patch(
            "persona.core.hybrid.stages.draft.ProviderFactory"
        ) as mock_factory:
            mock_factory.create.return_value = mock_provider

            await draft_personas(
                input_data="Test data",
                config=config,
                count=1,
                cost_tracker=cost_tracker,
            )

        # Check that tokens were tracked
        assert cost_tracker.local_input_tokens > 0
        assert cost_tracker.local_output_tokens > 0

    @pytest.mark.asyncio
    async def test_stops_when_budget_exceeded(self, config, cost_tracker):
        """Test that generation stops when budget is exceeded."""
        cost_tracker._max_budget = 0.0001  # Very low budget

        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.generate_async = AsyncMock(
            return_value=LLMResponse(
                content='[{"id": "p1", "name": "User"}]',
                model="test-model",
                input_tokens=1000000,  # High token count
                output_tokens=1000000,
            )
        )

        with patch(
            "persona.core.hybrid.stages.draft.ProviderFactory"
        ) as mock_factory:
            mock_factory.create.return_value = mock_provider

            personas = await draft_personas(
                input_data="Test data",
                config=config,
                count=100,  # Request many
                cost_tracker=cost_tracker,
            )

        # Should have stopped early due to budget
        assert len(personas) < 100
