"""Unit tests for cost tracking."""

import pytest

from persona.core.hybrid.cost import CostTracker, estimate_cost


def test_estimate_cost_ollama():
    """Test cost estimation for Ollama (always free)."""
    cost = estimate_cost("ollama", "qwen2.5:7b", 1000, 500)
    assert cost == 0.0

    cost = estimate_cost("ollama", "llama3:70b", 10000, 5000)
    assert cost == 0.0


def test_estimate_cost_anthropic():
    """Test cost estimation for Anthropic."""
    # Claude 3.5 Sonnet: $3 per 1M input, $15 per 1M output
    cost = estimate_cost(
        "anthropic",
        "claude-3-5-sonnet-20241022",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )
    assert cost == 18.0  # $3 input + $15 output

    # Half the tokens
    cost = estimate_cost(
        "anthropic",
        "claude-3-5-sonnet-20241022",
        input_tokens=500_000,
        output_tokens=500_000,
    )
    assert cost == 9.0


def test_estimate_cost_openai():
    """Test cost estimation for OpenAI."""
    # GPT-4o: $2.5 per 1M input, $10 per 1M output
    cost = estimate_cost(
        "openai",
        "gpt-4o",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )
    assert cost == 12.5


def test_estimate_cost_unknown_provider():
    """Test cost estimation for unknown provider."""
    cost = estimate_cost("unknown", "model", 1000, 500)
    assert cost == 0.0


def test_estimate_cost_unknown_model():
    """Test cost estimation for unknown model."""
    cost = estimate_cost("anthropic", "unknown-model", 1000, 500)
    assert cost == 0.0


def test_cost_tracker_init():
    """Test CostTracker initialisation."""
    tracker = CostTracker(
        max_budget=10.0,
        local_provider="ollama",
        local_model="qwen2.5:7b",
        frontier_provider="anthropic",
        frontier_model="claude-3-5-sonnet-20241022",
    )

    assert tracker.max_budget == 10.0
    assert tracker.local_input_tokens == 0
    assert tracker.local_output_tokens == 0
    assert tracker.frontier_input_tokens == 0
    assert tracker.frontier_output_tokens == 0


def test_cost_tracker_add_usage():
    """Test adding token usage."""
    tracker = CostTracker()

    tracker.add_local_usage(1000, 500)
    assert tracker.local_input_tokens == 1000
    assert tracker.local_output_tokens == 500

    tracker.add_frontier_usage(2000, 1000)
    assert tracker.frontier_input_tokens == 2000
    assert tracker.frontier_output_tokens == 1000

    tracker.add_judge_usage(500, 250)
    assert tracker.judge_input_tokens == 500
    assert tracker.judge_output_tokens == 250


def test_cost_tracker_local_cost():
    """Test local cost calculation."""
    tracker = CostTracker(
        local_provider="ollama",
        local_model="qwen2.5:7b",
    )

    tracker.add_local_usage(1000, 500)
    assert tracker.local_cost == 0.0  # Ollama is free


def test_cost_tracker_frontier_cost():
    """Test frontier cost calculation."""
    tracker = CostTracker(
        frontier_provider="anthropic",
        frontier_model="claude-3-5-sonnet-20241022",
    )

    # 1M input, 1M output = $18
    tracker.add_frontier_usage(1_000_000, 1_000_000)
    assert tracker.frontier_cost == 18.0


def test_cost_tracker_total_cost():
    """Test total cost calculation."""
    tracker = CostTracker(
        local_provider="ollama",
        local_model="qwen2.5:7b",
        frontier_provider="anthropic",
        frontier_model="claude-3-5-sonnet-20241022",
        judge_provider="ollama",
        judge_model="qwen2.5:72b",
    )

    tracker.add_local_usage(1000, 500)  # $0
    tracker.add_frontier_usage(100_000, 50_000)  # $0.30 + $0.75 = $1.05
    tracker.add_judge_usage(500, 250)  # $0

    assert tracker.total_cost == pytest.approx(1.05, rel=0.01)


def test_cost_tracker_budget_enforcement():
    """Test budget enforcement."""
    tracker = CostTracker(
        max_budget=1.0,
        frontier_provider="anthropic",
        frontier_model="claude-3-5-sonnet-20241022",
    )

    # Under budget
    tracker.add_frontier_usage(50_000, 25_000)  # ~$0.525
    assert not tracker.is_over_budget
    assert tracker.budget_remaining == pytest.approx(0.475, rel=0.01)
    assert tracker.budget_exceeded == 0.0

    # Over budget
    tracker.add_frontier_usage(100_000, 50_000)  # +$1.05 = $1.575 total
    assert tracker.is_over_budget
    assert tracker.budget_exceeded == pytest.approx(0.575, rel=0.01)


def test_cost_tracker_no_budget():
    """Test tracker without budget limit."""
    tracker = CostTracker(max_budget=None)

    tracker.add_frontier_usage(1_000_000, 1_000_000)
    assert not tracker.is_over_budget
    assert tracker.budget_remaining is None
    assert tracker.budget_exceeded == 0.0


def test_cost_tracker_total_tokens():
    """Test total token counting."""
    tracker = CostTracker()

    tracker.add_local_usage(1000, 500)
    tracker.add_frontier_usage(2000, 1000)
    tracker.add_judge_usage(500, 250)

    assert tracker.total_tokens == 5250


def test_cost_tracker_to_dict():
    """Test conversion to dictionary."""
    tracker = CostTracker(
        max_budget=5.0,
        local_provider="ollama",
        local_model="qwen2.5:7b",
        frontier_provider="anthropic",
        frontier_model="claude-3-5-sonnet-20241022",
    )

    tracker.add_local_usage(1000, 500)
    tracker.add_frontier_usage(100_000, 50_000)

    tracker_dict = tracker.to_dict()

    assert "local" in tracker_dict
    assert "frontier" in tracker_dict
    assert "judge" in tracker_dict
    assert "total" in tracker_dict
    assert "budget" in tracker_dict

    assert tracker_dict["local"]["input_tokens"] == 1000
    assert tracker_dict["frontier"]["input_tokens"] == 100_000
    assert tracker_dict["total"]["tokens"] == 151500
    assert tracker_dict["budget"]["max"] == 5.0
