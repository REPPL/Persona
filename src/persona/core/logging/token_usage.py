"""Token usage logging (F-077).

Tracks token usage per LLM call with breakdown by component
and aggregation for analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import json


@dataclass
class TokenBreakdown:
    """Breakdown of token usage by component.

    Attributes:
        system: System prompt tokens.
        data: Data context tokens.
        instructions: Instruction tokens.
        output: Output tokens.
        other: Other/unclassified tokens.
    """
    system: int = 0
    data: int = 0
    instructions: int = 0
    output: int = 0
    other: int = 0

    @property
    def total_input(self) -> int:
        """Get total input tokens."""
        return self.system + self.data + self.instructions + self.other

    @property
    def total(self) -> int:
        """Get total tokens."""
        return self.total_input + self.output

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "system": self.system,
            "data": self.data,
            "instructions": self.instructions,
            "output": self.output,
            "other": self.other,
            "total_input": self.total_input,
            "total": self.total,
        }


@dataclass
class TokenUsage:
    """Token usage for a single LLM call.

    Attributes:
        timestamp: When the call occurred.
        run_id: Associated run ID.
        step: Workflow step.
        model: Model used.
        provider: Provider used.
        input_tokens: Total input tokens.
        output_tokens: Total output tokens.
        breakdown: Detailed breakdown.
        cost_usd: Cost in USD.
        latency_ms: Call latency in milliseconds.
    """
    timestamp: str
    run_id: str
    step: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    breakdown: TokenBreakdown = field(default_factory=TokenBreakdown)
    cost_usd: float = 0.0
    latency_ms: float = 0.0

    @property
    def total_tokens(self) -> int:
        """Get total tokens."""
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "event": "llm_call",
            "run_id": self.run_id,
            "step": self.step,
            "model": self.model,
            "provider": self.provider,
            "tokens": {
                "input": self.input_tokens,
                "output": self.output_tokens,
                "total": self.total_tokens,
            },
            "prompt_breakdown": self.breakdown.to_dict(),
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class TokenUsageSummary:
    """Aggregated token usage summary.

    Attributes:
        total_input: Total input tokens.
        total_output: Total output tokens.
        total_cost_usd: Total cost.
        call_count: Number of LLM calls.
        by_step: Usage by workflow step.
        by_model: Usage by model.
        breakdown: Aggregate breakdown.
    """
    total_input: int = 0
    total_output: int = 0
    total_cost_usd: float = 0.0
    call_count: int = 0
    by_step: dict[str, dict[str, Any]] = field(default_factory=dict)
    by_model: dict[str, dict[str, Any]] = field(default_factory=dict)
    breakdown: TokenBreakdown = field(default_factory=TokenBreakdown)

    @property
    def total_tokens(self) -> int:
        """Get total tokens."""
        return self.total_input + self.total_output

    @property
    def output_input_ratio(self) -> float:
        """Get output to input ratio."""
        if self.total_input == 0:
            return 0.0
        return self.total_output / self.total_input

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_input": self.total_input,
            "total_output": self.total_output,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
            "call_count": self.call_count,
            "output_input_ratio": self.output_input_ratio,
            "by_step": self.by_step,
            "by_model": self.by_model,
            "breakdown": self.breakdown.to_dict(),
        }

    def to_display(self) -> str:
        """Generate human-readable display."""
        lines = [
            "Token Usage Report",
            "=" * 54,
            "",
            "By Step:",
            "┌─────────────────────────┬────────┬────────┬───────┐",
            "│ Step                    │ Input  │ Output │ Cost  │",
            "├─────────────────────────┼────────┼────────┼───────┤",
        ]

        for step, data in self.by_step.items():
            lines.append(
                f"│ {step:<23} │ {data['input']:>6,} │ "
                f"{data['output']:>6,} │ ${data['cost']:>5.2f} │"
            )

        lines.extend([
            "└─────────────────────────┴────────┴────────┴───────┘",
            f"Total:                     {self.total_input:>6,}   "
            f"{self.total_output:>6,}   ${self.total_cost_usd:>5.2f}",
            "",
            "By Prompt Component:",
        ])

        if self.total_tokens > 0:
            bd = self.breakdown
            lines.extend([
                f"  System prompt:    {bd.system:>6,} tokens ({100*bd.system/self.total_tokens:.1f}%)",
                f"  Data context:     {bd.data:>6,} tokens ({100*bd.data/self.total_tokens:.1f}%)",
                f"  Instructions:     {bd.instructions:>6,} tokens ({100*bd.instructions/self.total_tokens:.1f}%)",
                f"  Output:           {bd.output:>6,} tokens ({100*bd.output/self.total_tokens:.1f}%)",
            ])

        lines.extend([
            "",
            "Efficiency Metrics:",
            f"  Output/Input ratio: {self.output_input_ratio:.1%}",
            f"  Total calls: {self.call_count}",
        ])

        return "\n".join(lines)


class TokenUsageLogger:
    """Logger for token usage tracking.

    Tracks token usage per LLM call and provides
    aggregation and reporting capabilities.

    Example:
        >>> logger = TokenUsageLogger(run_id="run-abc123")
        >>> logger.log(
        ...     step="persona_generation",
        ...     model="claude-sonnet-4",
        ...     input_tokens=42000,
        ...     output_tokens=7500,
        ...     cost_usd=0.24
        ... )
        >>> summary = logger.get_summary()
    """

    def __init__(
        self,
        run_id: str = "",
        experiment_id: str = "",
    ):
        """Initialise the logger.

        Args:
            run_id: Associated run ID.
            experiment_id: Associated experiment ID.
        """
        self.run_id = run_id
        self.experiment_id = experiment_id
        self._usage_records: list[TokenUsage] = []

    def log(
        self,
        step: str,
        model: str,
        provider: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
        latency_ms: float = 0.0,
        breakdown: TokenBreakdown | None = None,
        run_id: str | None = None,
    ) -> TokenUsage:
        """Log token usage for an LLM call.

        Args:
            step: Workflow step name.
            model: Model identifier.
            provider: Provider name.
            input_tokens: Input token count.
            output_tokens: Output token count.
            cost_usd: Cost in USD.
            latency_ms: Latency in milliseconds.
            breakdown: Detailed token breakdown.
            run_id: Override run ID.

        Returns:
            Created TokenUsage record.
        """
        usage = TokenUsage(
            timestamp=datetime.now(timezone.utc).isoformat(),
            run_id=run_id or self.run_id,
            step=step,
            model=model,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            breakdown=breakdown or TokenBreakdown(output=output_tokens),
            cost_usd=cost_usd,
            latency_ms=latency_ms,
        )
        self._usage_records.append(usage)
        return usage

    def get_records(self) -> list[TokenUsage]:
        """Get all usage records."""
        return list(self._usage_records)

    def get_summary(self) -> TokenUsageSummary:
        """Get aggregated usage summary.

        Returns:
            TokenUsageSummary with aggregated data.
        """
        summary = TokenUsageSummary()

        for usage in self._usage_records:
            summary.total_input += usage.input_tokens
            summary.total_output += usage.output_tokens
            summary.total_cost_usd += usage.cost_usd
            summary.call_count += 1

            # Aggregate by step
            if usage.step not in summary.by_step:
                summary.by_step[usage.step] = {
                    "input": 0, "output": 0, "cost": 0.0
                }
            summary.by_step[usage.step]["input"] += usage.input_tokens
            summary.by_step[usage.step]["output"] += usage.output_tokens
            summary.by_step[usage.step]["cost"] += usage.cost_usd

            # Aggregate by model
            if usage.model not in summary.by_model:
                summary.by_model[usage.model] = {
                    "input": 0, "output": 0, "cost": 0.0
                }
            summary.by_model[usage.model]["input"] += usage.input_tokens
            summary.by_model[usage.model]["output"] += usage.output_tokens
            summary.by_model[usage.model]["cost"] += usage.cost_usd

            # Aggregate breakdown
            summary.breakdown.system += usage.breakdown.system
            summary.breakdown.data += usage.breakdown.data
            summary.breakdown.instructions += usage.breakdown.instructions
            summary.breakdown.output += usage.breakdown.output
            summary.breakdown.other += usage.breakdown.other

        return summary

    def to_jsonl(self) -> str:
        """Export to JSON Lines format.

        Returns:
            JSON Lines string.
        """
        return "\n".join(r.to_json() for r in self._usage_records)

    def to_csv(self) -> str:
        """Export to CSV format.

        Returns:
            CSV string.
        """
        lines = [
            "timestamp,run_id,step,model,provider,input_tokens,output_tokens,cost_usd,latency_ms"
        ]
        for r in self._usage_records:
            lines.append(
                f"{r.timestamp},{r.run_id},{r.step},{r.model},{r.provider},"
                f"{r.input_tokens},{r.output_tokens},{r.cost_usd},{r.latency_ms}"
            )
        return "\n".join(lines)


def log_token_usage(
    step: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float = 0.0,
) -> TokenUsage:
    """Convenience function to create a token usage record.

    Args:
        step: Workflow step.
        model: Model identifier.
        input_tokens: Input tokens.
        output_tokens: Output tokens.
        cost_usd: Cost in USD.

    Returns:
        TokenUsage record.
    """
    return TokenUsage(
        timestamp=datetime.now(timezone.utc).isoformat(),
        run_id="",
        step=step,
        model=model,
        provider="",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost_usd,
    )
