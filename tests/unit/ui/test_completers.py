"""
Tests for shell completers (F-095).
"""

from unittest.mock import MagicMock

import pytest

from persona.ui.completers import (
    complete_provider,
    complete_model,
    complete_format,
    complete_workflow,
    complete_complexity,
    complete_detail_level,
    complete_log_level,
)


class TestCompleteProvider:
    """Tests for provider completion."""

    def test_all_providers(self):
        """Test completing all providers with empty string."""
        results = list(complete_provider(""))
        assert len(results) == 3
        names = [r[0] for r in results]
        assert "anthropic" in names
        assert "openai" in names
        assert "gemini" in names

    def test_partial_match(self):
        """Test completing with partial input."""
        results = list(complete_provider("an"))
        assert len(results) == 1
        assert results[0][0] == "anthropic"

    def test_no_match(self):
        """Test completing with no match."""
        results = list(complete_provider("xyz"))
        assert len(results) == 0

    def test_returns_help_text(self):
        """Test that help text is included."""
        results = list(complete_provider(""))
        for value, help_text in results:
            assert len(help_text) > 0


class TestCompleteModel:
    """Tests for model completion."""

    def test_all_models(self):
        """Test completing all models with empty string."""
        ctx = MagicMock()
        ctx.params = {}

        results = list(complete_model(ctx, ""))
        assert len(results) > 0

    def test_anthropic_models(self):
        """Test completing Anthropic models."""
        ctx = MagicMock()
        ctx.params = {"provider": "anthropic"}

        results = list(complete_model(ctx, ""))
        names = [r[0] for r in results]

        # All should be Claude models
        assert all("claude" in name.lower() for name in names)

    def test_openai_models(self):
        """Test completing OpenAI models."""
        ctx = MagicMock()
        ctx.params = {"provider": "openai"}

        results = list(complete_model(ctx, ""))
        names = [r[0] for r in results]

        # All should be GPT models
        assert all("gpt" in name.lower() or "o1" in name.lower() for name in names)

    def test_partial_match(self):
        """Test completing with partial input."""
        ctx = MagicMock()
        ctx.params = {"provider": "anthropic"}

        results = list(complete_model(ctx, "claude-s"))
        names = [r[0] for r in results]

        assert all(name.startswith("claude-s") for name in names)

    def test_returns_help_text(self):
        """Test that help text is included."""
        ctx = MagicMock()
        ctx.params = {}

        results = list(complete_model(ctx, ""))
        for value, help_text in results:
            assert len(help_text) > 0


class TestCompleteFormat:
    """Tests for format completion."""

    def test_all_formats(self):
        """Test completing all formats with empty string."""
        results = list(complete_format(""))
        assert len(results) == 3
        names = [r[0] for r in results]
        assert "json" in names
        assert "markdown" in names
        assert "yaml" in names

    def test_partial_match(self):
        """Test completing with partial input."""
        results = list(complete_format("j"))
        assert len(results) == 1
        assert results[0][0] == "json"

    def test_returns_help_text(self):
        """Test that help text is included."""
        results = list(complete_format(""))
        for value, help_text in results:
            assert len(help_text) > 0


class TestCompleteWorkflow:
    """Tests for workflow completion."""

    def test_all_workflows(self):
        """Test completing all workflows with empty string."""
        results = list(complete_workflow(""))
        assert len(results) == 3
        names = [r[0] for r in results]
        assert "default" in names
        assert "research" in names
        assert "quick" in names

    def test_partial_match(self):
        """Test completing with partial input."""
        results = list(complete_workflow("re"))
        assert len(results) == 1
        assert results[0][0] == "research"


class TestCompleteComplexity:
    """Tests for complexity level completion."""

    def test_all_levels(self):
        """Test completing all complexity levels."""
        results = list(complete_complexity(""))
        assert len(results) == 3
        names = [r[0] for r in results]
        assert "simple" in names
        assert "moderate" in names
        assert "complex" in names

    def test_partial_match(self):
        """Test completing with partial input."""
        results = list(complete_complexity("mod"))
        assert len(results) == 1
        assert results[0][0] == "moderate"


class TestCompleteDetailLevel:
    """Tests for detail level completion."""

    def test_all_levels(self):
        """Test completing all detail levels."""
        results = list(complete_detail_level(""))
        assert len(results) == 3
        names = [r[0] for r in results]
        assert "minimal" in names
        assert "standard" in names
        assert "detailed" in names

    def test_partial_match(self):
        """Test completing with partial input."""
        results = list(complete_detail_level("de"))
        assert len(results) == 1
        assert results[0][0] == "detailed"


class TestCompleteLogLevel:
    """Tests for log level completion."""

    def test_all_levels(self):
        """Test completing all log levels."""
        results = list(complete_log_level(""))
        assert len(results) == 4
        names = [r[0] for r in results]
        assert "debug" in names
        assert "info" in names
        assert "warning" in names
        assert "error" in names

    def test_partial_match(self):
        """Test completing with partial input."""
        results = list(complete_log_level("war"))
        assert len(results) == 1
        assert results[0][0] == "warning"
