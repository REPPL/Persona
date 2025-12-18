"""Tests for token count tracking (F-063)."""


import pytest
from persona.core.batch.tokens import (
    TokenBreakdown,
    TokenCounter,
    TokenUsage,
    count_tokens,
)


class TestTokenUsage:
    """Tests for TokenUsage."""

    def test_total_tokens(self):
        """Calculates total tokens."""
        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            model="gpt-4o",
        )

        assert usage.total_tokens == 1500

    def test_to_dict(self):
        """Converts to dictionary."""
        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            model="gpt-4o",
            step="generation",
        )
        data = usage.to_dict()

        assert data["input_tokens"] == 1000
        assert data["output_tokens"] == 500
        assert data["total_tokens"] == 1500
        assert data["model"] == "gpt-4o"
        assert data["step"] == "generation"
        assert "timestamp" in data


class TestTokenBreakdown:
    """Tests for TokenBreakdown."""

    def test_add_usage(self):
        """Adds usage correctly."""
        breakdown = TokenBreakdown()

        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            model="gpt-4o",
            step="generation",
        )
        breakdown.add_usage(usage)

        assert breakdown.total_input_tokens == 1000
        assert breakdown.total_output_tokens == 500
        assert len(breakdown.calls) == 1

    def test_total_tokens(self):
        """Calculates total across all usage."""
        breakdown = TokenBreakdown()

        breakdown.add_usage(TokenUsage(1000, 500, "gpt-4o", step="step1"))
        breakdown.add_usage(TokenUsage(2000, 1000, "gpt-4o", step="step2"))

        assert breakdown.total_tokens == 4500

    def test_by_step_breakdown(self):
        """Tracks by-step breakdown."""
        breakdown = TokenBreakdown()

        breakdown.add_usage(TokenUsage(1000, 500, "gpt-4o", step="generation"))
        breakdown.add_usage(TokenUsage(500, 200, "gpt-4o", step="validation"))

        assert "generation" in breakdown.by_step
        assert breakdown.by_step["generation"]["input"] == 1000
        assert breakdown.by_step["validation"]["input"] == 500

    def test_to_dict(self):
        """Converts to dictionary."""
        breakdown = TokenBreakdown()
        breakdown.add_usage(TokenUsage(1000, 500, "gpt-4o", step="test"))

        data = breakdown.to_dict()

        assert "total_input_tokens" in data
        assert "total_output_tokens" in data
        assert "total_tokens" in data
        assert "breakdown_by_step" in data


class TestTokenCounter:
    """Tests for TokenCounter."""

    def test_count_tokens_empty(self):
        """Returns 0 for empty string."""
        counter = TokenCounter(use_tiktoken=False)
        count = counter.count_tokens("")

        assert count == 0

    def test_count_tokens_estimation(self):
        """Estimates tokens without tiktoken."""
        counter = TokenCounter(use_tiktoken=False)
        # 40 characters / 4 chars per token = 10 tokens
        text = "a" * 40
        count = counter.count_tokens(text, model="claude-sonnet-4-20250514")

        assert count == 10

    def test_count_tokens_tiktoken_openai(self):
        """Uses tiktoken for OpenAI models when available."""
        counter = TokenCounter(use_tiktoken=True)
        # May or may not have tiktoken installed
        count = counter.count_tokens("Hello, world!", model="gpt-4o")

        assert count > 0

    def test_count_messages(self):
        """Counts tokens in message list."""
        counter = TokenCounter(use_tiktoken=False)
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello!"},
        ]

        count = counter.count_messages(messages, model="gpt-4o")

        assert count > 0

    def test_record_usage(self):
        """Records usage and updates breakdown."""
        counter = TokenCounter()

        usage = counter.record_usage(
            input_tokens=1000,
            output_tokens=500,
            model="gpt-4o",
            step="generation",
        )

        assert usage.input_tokens == 1000
        breakdown = counter.get_breakdown()
        assert breakdown.total_tokens == 1500

    def test_reset(self):
        """Resets token tracking."""
        counter = TokenCounter()
        counter.record_usage(1000, 500, "gpt-4o")

        counter.reset()

        assert counter.get_breakdown().total_tokens == 0

    def test_get_summary(self):
        """Gets usage summary."""
        counter = TokenCounter()
        counter.record_usage(1000, 500, "gpt-4o")

        summary = counter.get_summary()

        assert summary["total_input_tokens"] == 1000
        assert summary["total_output_tokens"] == 500
        assert summary["calls"] == 1

    def test_estimate_cost(self):
        """Estimates cost from usage."""
        counter = TokenCounter()
        counter.record_usage(1000000, 500000, "gpt-4o")

        # $3 per 1M input, $15 per 1M output
        cost = counter.estimate_cost(input_price=3.0, output_price=15.0)

        assert cost == pytest.approx(10.5, rel=0.01)

    def test_detect_provider_anthropic(self):
        """Detects Anthropic provider."""
        counter = TokenCounter(use_tiktoken=False)
        provider = counter._detect_provider("claude-sonnet-4-20250514")

        assert provider == "anthropic"

    def test_detect_provider_openai(self):
        """Detects OpenAI provider."""
        counter = TokenCounter(use_tiktoken=False)
        provider = counter._detect_provider("gpt-4o")

        assert provider == "openai"

    def test_detect_provider_gemini(self):
        """Detects Gemini provider."""
        counter = TokenCounter(use_tiktoken=False)
        provider = counter._detect_provider("gemini-1.5-pro")

        assert provider == "gemini"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_count_tokens(self):
        """count_tokens convenience function works."""
        count = count_tokens("Hello, world!", model="gpt-4o")

        assert count > 0
