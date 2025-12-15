"""
Cost estimation and tracking for hybrid pipeline.

This module provides utilities to estimate and track API costs across
local and frontier LLM providers.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


# Pricing per 1M tokens (USD)
# Sources: Provider pricing pages as of January 2025
PROVIDER_PRICING = {
    "anthropic": {
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
        "claude-3-5-haiku-20241022": {"input": 1.0, "output": 5.0},
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
    },
    "openai": {
        "gpt-4o": {"input": 2.5, "output": 10.0},
        "gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    },
    "gemini": {
        "gemini-1.5-pro": {"input": 1.25, "output": 5.0},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.3},
    },
    "ollama": {
        # Local models have zero cost
        "*": {"input": 0.0, "output": 0.0},
    },
}


def estimate_cost(
    provider: str,
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> float:
    """
    Estimate cost for API call.

    Args:
        provider: Provider name (anthropic, openai, gemini, ollama).
        model: Model identifier.
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.

    Returns:
        Estimated cost in USD.

    Example:
        cost = estimate_cost("anthropic", "claude-3-5-sonnet-20241022", 1000, 500)
        # Returns approximately 0.0105 USD
    """
    provider = provider.lower()

    # Ollama is always free
    if provider == "ollama":
        return 0.0

    # Look up pricing
    if provider not in PROVIDER_PRICING:
        # Unknown provider, return 0 but warn
        return 0.0

    provider_models = PROVIDER_PRICING[provider]
    model_pricing = None

    # Try exact match first
    if model in provider_models:
        model_pricing = provider_models[model]
    # Try wildcard match (for ollama)
    elif "*" in provider_models:
        model_pricing = provider_models["*"]
    else:
        # Unknown model, return 0 but warn
        return 0.0

    # Calculate cost per million tokens
    input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (output_tokens / 1_000_000) * model_pricing["output"]

    return input_cost + output_cost


@dataclass
class CostTracker:
    """
    Track costs across hybrid pipeline execution.

    Attributes:
        max_budget: Optional maximum budget in USD.
        local_input_tokens: Tokens used for local model input.
        local_output_tokens: Tokens used for local model output.
        frontier_input_tokens: Tokens used for frontier model input.
        frontier_output_tokens: Tokens used for frontier model output.
        judge_input_tokens: Tokens used for judge model input.
        judge_output_tokens: Tokens used for judge model output.

    Example:
        tracker = CostTracker(max_budget=5.0)
        tracker.add_local_usage(1000, 500)
        tracker.add_frontier_usage(2000, 1000)

        if tracker.is_over_budget:
            print(f"Over budget by ${tracker.budget_exceeded:.2f}")
    """

    max_budget: Optional[float] = None
    local_input_tokens: int = 0
    local_output_tokens: int = 0
    frontier_input_tokens: int = 0
    frontier_output_tokens: int = 0
    judge_input_tokens: int = 0
    judge_output_tokens: int = 0

    # Provider/model tracking
    local_provider: str = "ollama"
    local_model: str = "qwen2.5:7b"
    frontier_provider: Optional[str] = None
    frontier_model: Optional[str] = None
    judge_provider: str = "ollama"
    judge_model: str = "qwen2.5:72b"

    def add_local_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Add local model token usage."""
        self.local_input_tokens += input_tokens
        self.local_output_tokens += output_tokens

    def add_frontier_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Add frontier model token usage."""
        self.frontier_input_tokens += input_tokens
        self.frontier_output_tokens += output_tokens

    def add_judge_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Add judge model token usage."""
        self.judge_input_tokens += input_tokens
        self.judge_output_tokens += output_tokens

    @property
    def local_cost(self) -> float:
        """Calculate local model cost."""
        return estimate_cost(
            self.local_provider,
            self.local_model,
            self.local_input_tokens,
            self.local_output_tokens,
        )

    @property
    def frontier_cost(self) -> float:
        """Calculate frontier model cost."""
        if not self.frontier_provider or not self.frontier_model:
            return 0.0

        return estimate_cost(
            self.frontier_provider,
            self.frontier_model,
            self.frontier_input_tokens,
            self.frontier_output_tokens,
        )

    @property
    def judge_cost(self) -> float:
        """Calculate judge model cost."""
        return estimate_cost(
            self.judge_provider,
            self.judge_model,
            self.judge_input_tokens,
            self.judge_output_tokens,
        )

    @property
    def total_cost(self) -> float:
        """Calculate total cost across all models."""
        return self.local_cost + self.frontier_cost + self.judge_cost

    @property
    def is_over_budget(self) -> bool:
        """Check if over budget."""
        if self.max_budget is None:
            return False
        return self.total_cost > self.max_budget

    @property
    def budget_exceeded(self) -> float:
        """Return amount over budget (0 if under budget)."""
        if self.max_budget is None:
            return 0.0
        exceeded = self.total_cost - self.max_budget
        return max(0.0, exceeded)

    @property
    def budget_remaining(self) -> Optional[float]:
        """Return remaining budget (None if no budget set)."""
        if self.max_budget is None:
            return None
        return max(0.0, self.max_budget - self.total_cost)

    @property
    def total_tokens(self) -> int:
        """Return total tokens used across all models."""
        return (
            self.local_input_tokens
            + self.local_output_tokens
            + self.frontier_input_tokens
            + self.frontier_output_tokens
            + self.judge_input_tokens
            + self.judge_output_tokens
        )

    def to_dict(self) -> Dict:
        """Convert tracker to dictionary."""
        return {
            "local": {
                "input_tokens": self.local_input_tokens,
                "output_tokens": self.local_output_tokens,
                "cost": round(self.local_cost, 4),
            },
            "frontier": {
                "input_tokens": self.frontier_input_tokens,
                "output_tokens": self.frontier_output_tokens,
                "cost": round(self.frontier_cost, 4),
            },
            "judge": {
                "input_tokens": self.judge_input_tokens,
                "output_tokens": self.judge_output_tokens,
                "cost": round(self.judge_cost, 4),
            },
            "total": {
                "tokens": self.total_tokens,
                "cost": round(self.total_cost, 4),
            },
            "budget": {
                "max": self.max_budget,
                "remaining": (
                    round(self.budget_remaining, 4)
                    if self.budget_remaining is not None
                    else None
                ),
                "exceeded": round(self.budget_exceeded, 4),
            },
        }
