"""
Token count tracking (F-063).

Provides token counting and usage tracking for LLM calls.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TokenUsage:
    """
    Token usage for a single LLM call.

    Records input and output tokens along with metadata.
    """

    input_tokens: int
    output_tokens: int
    model: str
    timestamp: datetime = field(default_factory=datetime.now)
    step: str = ""

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "model": self.model,
            "timestamp": self.timestamp.isoformat(),
            "step": self.step,
        }


@dataclass
class TokenBreakdown:
    """
    Breakdown of token usage across steps.

    Aggregates token usage by workflow step.
    """

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    by_step: dict[str, dict] = field(default_factory=dict)
    calls: list[TokenUsage] = field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        """Total tokens across all steps."""
        return self.total_input_tokens + self.total_output_tokens

    def add_usage(self, usage: TokenUsage) -> None:
        """Add a token usage record."""
        self.calls.append(usage)
        self.total_input_tokens += usage.input_tokens
        self.total_output_tokens += usage.output_tokens

        # Update by-step breakdown
        step = usage.step or "default"
        if step not in self.by_step:
            self.by_step[step] = {"input": 0, "output": 0}
        self.by_step[step]["input"] += usage.input_tokens
        self.by_step[step]["output"] += usage.output_tokens

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "breakdown_by_step": [
                {"step": step, "input": data["input"], "output": data["output"]}
                for step, data in self.by_step.items()
            ],
        }


class TokenCounter:
    """
    Counts and tracks token usage.

    Uses provider-specific tokenisers when available, with fallback
    to estimation based on character count.

    Example:
        >>> counter = TokenCounter()
        >>> count = counter.count_tokens("Hello, world!", "gpt-4o")
        >>> print(count)
        4
    """

    # Approximate characters per token by provider
    CHARS_PER_TOKEN: dict[str, float] = {
        "anthropic": 4.0,
        "openai": 4.0,
        "gemini": 4.0,
        "default": 4.0,
    }

    def __init__(self, use_tiktoken: bool = True):
        """
        Initialise the token counter.

        Args:
            use_tiktoken: Whether to use tiktoken for OpenAI models.
        """
        self._use_tiktoken = use_tiktoken
        self._tiktoken_encodings: dict[str, Any] = {}
        self._breakdown = TokenBreakdown()

    def count_tokens(
        self,
        text: str,
        model: str = "gpt-4o",
    ) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for.
            model: Model identifier.

        Returns:
            Token count.
        """
        if not text:
            return 0

        # Try tiktoken for OpenAI models
        if self._use_tiktoken and self._is_openai_model(model):
            try:
                return self._count_tiktoken(text, model)
            except (ImportError, ValueError, UnicodeDecodeError):
                # Tiktoken unavailable or encoding error - fall back to estimation
                pass

        # Fallback to estimation
        return self._estimate_tokens(text, model)

    def count_messages(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-4o",
    ) -> int:
        """
        Count tokens in a message list.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Model identifier.

        Returns:
            Total token count.
        """
        total = 0
        for message in messages:
            # Count content
            content = message.get("content", "")
            total += self.count_tokens(content, model)
            # Add overhead for message structure
            total += 4  # Approximate overhead per message
        return total

    def record_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str,
        step: str = "",
    ) -> TokenUsage:
        """
        Record token usage from an LLM call.

        Args:
            input_tokens: Tokens sent to LLM.
            output_tokens: Tokens received from LLM.
            model: Model used.
            step: Workflow step name.

        Returns:
            TokenUsage record.
        """
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            step=step,
        )
        self._breakdown.add_usage(usage)
        return usage

    def get_breakdown(self) -> TokenBreakdown:
        """Get current token breakdown."""
        return self._breakdown

    def reset(self) -> None:
        """Reset token tracking."""
        self._breakdown = TokenBreakdown()

    def get_summary(self) -> dict:
        """
        Get token usage summary.

        Returns:
            Dictionary with usage summary.
        """
        return {
            "total_input_tokens": self._breakdown.total_input_tokens,
            "total_output_tokens": self._breakdown.total_output_tokens,
            "total_tokens": self._breakdown.total_tokens,
            "calls": len(self._breakdown.calls),
            "breakdown": self._breakdown.to_dict(),
        }

    def estimate_cost(
        self,
        input_price: float,
        output_price: float,
    ) -> float:
        """
        Estimate cost based on recorded usage.

        Args:
            input_price: Price per 1M input tokens.
            output_price: Price per 1M output tokens.

        Returns:
            Estimated cost in dollars.
        """
        input_cost = (self._breakdown.total_input_tokens / 1_000_000) * input_price
        output_cost = (self._breakdown.total_output_tokens / 1_000_000) * output_price
        return input_cost + output_cost

    def _is_openai_model(self, model: str) -> bool:
        """Check if model is an OpenAI model."""
        openai_prefixes = ("gpt-", "o1-", "text-", "davinci", "curie", "babbage", "ada")
        return any(model.startswith(p) for p in openai_prefixes)

    def _count_tiktoken(self, text: str, model: str) -> int:
        """Count tokens using tiktoken."""
        import tiktoken

        # Get or create encoding
        if model not in self._tiktoken_encodings:
            try:
                self._tiktoken_encodings[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to cl100k_base for newer models
                self._tiktoken_encodings[model] = tiktoken.get_encoding("cl100k_base")

        encoding = self._tiktoken_encodings[model]
        return len(encoding.encode(text))

    def _estimate_tokens(self, text: str, model: str) -> int:
        """Estimate tokens based on character count."""
        provider = self._detect_provider(model)
        chars_per_token = self.CHARS_PER_TOKEN.get(
            provider,
            self.CHARS_PER_TOKEN["default"],
        )
        return int(len(text) / chars_per_token)

    def _detect_provider(self, model: str) -> str:
        """Detect provider from model name."""
        if model.startswith("claude"):
            return "anthropic"
        elif model.startswith(("gpt-", "o1-", "text-")):
            return "openai"
        elif model.startswith("gemini"):
            return "gemini"
        return "default"


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Convenience function to count tokens.

    Args:
        text: Text to count.
        model: Model identifier.

    Returns:
        Token count.
    """
    counter = TokenCounter()
    return counter.count_tokens(text, model)
