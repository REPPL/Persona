"""Tests for token usage logging (F-077)."""

import json
from datetime import UTC, datetime

from persona.core.logging.token_usage import (
    TokenBreakdown,
    TokenUsage,
    TokenUsageLogger,
    TokenUsageSummary,
    log_token_usage,
)


class TestTokenBreakdown:
    """Tests for TokenBreakdown dataclass."""

    def test_create_breakdown(self) -> None:
        """Can create a token breakdown."""
        breakdown = TokenBreakdown(
            system=1000,
            data=5000,
            instructions=500,
            output=2000,
            other=100,
        )

        assert breakdown.system == 1000
        assert breakdown.data == 5000
        assert breakdown.instructions == 500
        assert breakdown.output == 2000
        assert breakdown.other == 100

    def test_defaults_to_zero(self) -> None:
        """All fields default to 0."""
        breakdown = TokenBreakdown()

        assert breakdown.system == 0
        assert breakdown.data == 0
        assert breakdown.instructions == 0
        assert breakdown.output == 0
        assert breakdown.other == 0

    def test_total_input_property(self) -> None:
        """total_input sums input components."""
        breakdown = TokenBreakdown(
            system=1000,
            data=2000,
            instructions=500,
            other=100,
            output=3000,
        )

        assert breakdown.total_input == 3600  # 1000 + 2000 + 500 + 100

    def test_total_property(self) -> None:
        """total sums all components."""
        breakdown = TokenBreakdown(
            system=1000,
            data=2000,
            instructions=500,
            other=100,
            output=3000,
        )

        assert breakdown.total == 6600  # 3600 input + 3000 output

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        breakdown = TokenBreakdown(
            system=100,
            data=200,
            output=300,
        )

        result = breakdown.to_dict()

        assert result["system"] == 100
        assert result["data"] == 200
        assert result["output"] == 300
        assert result["total_input"] == 300  # 100 + 200 + 0 + 0
        assert result["total"] == 600


class TestTokenUsage:
    """Tests for TokenUsage dataclass."""

    def test_create_token_usage(self) -> None:
        """Can create token usage record."""
        usage = TokenUsage(
            timestamp="2025-01-01T00:00:00+00:00",
            run_id="run-123",
            step="persona_generation",
            model="claude-sonnet-4",
            provider="anthropic",
            input_tokens=10000,
            output_tokens=2000,
        )

        assert usage.timestamp == "2025-01-01T00:00:00+00:00"
        assert usage.run_id == "run-123"
        assert usage.step == "persona_generation"
        assert usage.model == "claude-sonnet-4"
        assert usage.input_tokens == 10000
        assert usage.output_tokens == 2000

    def test_defaults(self) -> None:
        """Has sensible defaults."""
        usage = TokenUsage(
            timestamp="2025-01-01T00:00:00+00:00",
            run_id="run-123",
            step="test",
            model="test-model",
            provider="test-provider",
            input_tokens=100,
            output_tokens=50,
        )

        assert isinstance(usage.breakdown, TokenBreakdown)
        assert usage.cost_usd == 0.0
        assert usage.latency_ms == 0.0

    def test_total_tokens_property(self) -> None:
        """total_tokens sums input and output."""
        usage = TokenUsage(
            timestamp="2025-01-01T00:00:00+00:00",
            run_id="run-123",
            step="test",
            model="test-model",
            provider="test-provider",
            input_tokens=8000,
            output_tokens=2000,
        )

        assert usage.total_tokens == 10000

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        usage = TokenUsage(
            timestamp="2025-01-01T00:00:00+00:00",
            run_id="run-123",
            step="generation",
            model="claude",
            provider="anthropic",
            input_tokens=5000,
            output_tokens=1000,
            cost_usd=0.05,
            latency_ms=1500,
        )

        result = usage.to_dict()

        assert result["timestamp"] == "2025-01-01T00:00:00+00:00"
        assert result["event"] == "llm_call"
        assert result["run_id"] == "run-123"
        assert result["step"] == "generation"
        assert result["model"] == "claude"
        assert result["tokens"]["input"] == 5000
        assert result["tokens"]["output"] == 1000
        assert result["tokens"]["total"] == 6000
        assert result["cost_usd"] == 0.05
        assert result["latency_ms"] == 1500

    def test_to_json(self) -> None:
        """Can serialize to JSON."""
        usage = TokenUsage(
            timestamp="2025-01-01T00:00:00+00:00",
            run_id="run-123",
            step="test",
            model="test-model",
            provider="test-provider",
            input_tokens=100,
            output_tokens=50,
        )

        json_str = usage.to_json()
        parsed = json.loads(json_str)

        assert parsed["tokens"]["total"] == 150


class TestTokenUsageSummary:
    """Tests for TokenUsageSummary dataclass."""

    def test_create_summary(self) -> None:
        """Can create a summary."""
        summary = TokenUsageSummary(
            total_input=50000,
            total_output=10000,
            total_cost_usd=0.75,
            call_count=5,
        )

        assert summary.total_input == 50000
        assert summary.total_output == 10000
        assert summary.total_cost_usd == 0.75
        assert summary.call_count == 5

    def test_defaults(self) -> None:
        """Has sensible defaults."""
        summary = TokenUsageSummary()

        assert summary.total_input == 0
        assert summary.total_output == 0
        assert summary.total_cost_usd == 0.0
        assert summary.call_count == 0
        assert summary.by_step == {}
        assert summary.by_model == {}

    def test_total_tokens_property(self) -> None:
        """total_tokens sums input and output."""
        summary = TokenUsageSummary(
            total_input=30000,
            total_output=5000,
        )

        assert summary.total_tokens == 35000

    def test_output_input_ratio(self) -> None:
        """Calculates output to input ratio."""
        summary = TokenUsageSummary(
            total_input=10000,
            total_output=2000,
        )

        assert summary.output_input_ratio == 0.2

    def test_output_input_ratio_zero_input(self) -> None:
        """Ratio is 0 when no input."""
        summary = TokenUsageSummary(
            total_input=0,
            total_output=100,
        )

        assert summary.output_input_ratio == 0.0

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        summary = TokenUsageSummary(
            total_input=10000,
            total_output=2000,
            total_cost_usd=0.15,
            call_count=3,
        )

        result = summary.to_dict()

        assert result["total_input"] == 10000
        assert result["total_output"] == 2000
        assert result["total_tokens"] == 12000
        assert result["total_cost_usd"] == 0.15
        assert result["call_count"] == 3
        assert result["output_input_ratio"] == 0.2

    def test_to_display(self) -> None:
        """Can generate display output."""
        summary = TokenUsageSummary(
            total_input=10000,
            total_output=2000,
            total_cost_usd=0.15,
            call_count=3,
            by_step={
                "generation": {"input": 8000, "output": 1500, "cost": 0.12},
                "validation": {"input": 2000, "output": 500, "cost": 0.03},
            },
            breakdown=TokenBreakdown(
                system=1000,
                data=5000,
                instructions=2000,
                output=2000,
                other=2000,
            ),
        )

        display = summary.to_display()

        assert "Token Usage Report" in display
        assert "generation" in display
        assert "validation" in display
        assert "Output/Input ratio" in display


class TestTokenUsageLogger:
    """Tests for TokenUsageLogger class."""

    def test_create_logger(self) -> None:
        """Can create a token usage logger."""
        logger = TokenUsageLogger(
            run_id="run-123",
            experiment_id="exp-456",
        )

        assert logger.run_id == "run-123"
        assert logger.experiment_id == "exp-456"

    def test_log_usage(self) -> None:
        """Can log token usage."""
        logger = TokenUsageLogger(run_id="run-123")

        usage = logger.log(
            step="generation",
            model="claude-sonnet-4",
            provider="anthropic",
            input_tokens=10000,
            output_tokens=2000,
            cost_usd=0.15,
            latency_ms=2500,
        )

        assert usage.step == "generation"
        assert usage.model == "claude-sonnet-4"
        assert usage.input_tokens == 10000
        assert usage.output_tokens == 2000
        assert usage.cost_usd == 0.15
        assert usage.run_id == "run-123"

    def test_log_with_breakdown(self) -> None:
        """Can log with detailed breakdown."""
        logger = TokenUsageLogger()

        breakdown = TokenBreakdown(
            system=1000,
            data=5000,
            instructions=500,
        )

        usage = logger.log(
            step="test",
            model="test-model",
            input_tokens=6500,
            output_tokens=1000,
            breakdown=breakdown,
        )

        assert usage.breakdown.system == 1000
        assert usage.breakdown.data == 5000

    def test_log_with_run_id_override(self) -> None:
        """Can override run_id per log call."""
        logger = TokenUsageLogger(run_id="default-run")

        usage = logger.log(
            step="test",
            model="test-model",
            input_tokens=100,
            output_tokens=50,
            run_id="override-run",
        )

        assert usage.run_id == "override-run"

    def test_get_records(self) -> None:
        """Can retrieve all logged records."""
        logger = TokenUsageLogger()

        logger.log(step="step1", model="model1", input_tokens=100, output_tokens=50)
        logger.log(step="step2", model="model2", input_tokens=200, output_tokens=100)
        logger.log(step="step3", model="model1", input_tokens=150, output_tokens=75)

        records = logger.get_records()

        assert len(records) == 3

    def test_get_summary(self) -> None:
        """Can get aggregated summary."""
        logger = TokenUsageLogger()

        logger.log(
            step="generation",
            model="claude",
            input_tokens=10000,
            output_tokens=2000,
            cost_usd=0.15,
        )
        logger.log(
            step="validation",
            model="claude",
            input_tokens=5000,
            output_tokens=500,
            cost_usd=0.05,
        )
        logger.log(
            step="generation",
            model="gpt-4",
            input_tokens=8000,
            output_tokens=1500,
            cost_usd=0.12,
        )

        summary = logger.get_summary()

        assert summary.total_input == 23000
        assert summary.total_output == 4000
        assert summary.total_cost_usd == 0.32
        assert summary.call_count == 3

    def test_get_summary_by_step(self) -> None:
        """Summary aggregates by step."""
        logger = TokenUsageLogger()

        logger.log(
            step="generation",
            model="claude",
            input_tokens=10000,
            output_tokens=2000,
            cost_usd=0.15,
        )
        logger.log(
            step="generation",
            model="claude",
            input_tokens=10000,
            output_tokens=2000,
            cost_usd=0.15,
        )
        logger.log(
            step="validation",
            model="claude",
            input_tokens=5000,
            output_tokens=500,
            cost_usd=0.05,
        )

        summary = logger.get_summary()

        assert "generation" in summary.by_step
        assert "validation" in summary.by_step
        assert summary.by_step["generation"]["input"] == 20000
        assert summary.by_step["validation"]["input"] == 5000

    def test_get_summary_by_model(self) -> None:
        """Summary aggregates by model."""
        logger = TokenUsageLogger()

        logger.log(
            step="test",
            model="claude",
            input_tokens=10000,
            output_tokens=2000,
            cost_usd=0.15,
        )
        logger.log(
            step="test",
            model="gpt-4",
            input_tokens=8000,
            output_tokens=1500,
            cost_usd=0.12,
        )
        logger.log(
            step="test",
            model="claude",
            input_tokens=5000,
            output_tokens=1000,
            cost_usd=0.08,
        )

        summary = logger.get_summary()

        assert "claude" in summary.by_model
        assert "gpt-4" in summary.by_model
        assert summary.by_model["claude"]["input"] == 15000
        assert summary.by_model["gpt-4"]["input"] == 8000

    def test_get_summary_aggregates_breakdown(self) -> None:
        """Summary aggregates token breakdown."""
        logger = TokenUsageLogger()

        logger.log(
            step="test",
            model="test",
            input_tokens=6500,
            output_tokens=1000,
            breakdown=TokenBreakdown(system=1000, data=5000, instructions=500),
        )
        logger.log(
            step="test",
            model="test",
            input_tokens=3000,
            output_tokens=500,
            breakdown=TokenBreakdown(system=500, data=2000, instructions=500),
        )

        summary = logger.get_summary()

        assert summary.breakdown.system == 1500
        assert summary.breakdown.data == 7000

    def test_to_jsonl(self) -> None:
        """Can export to JSON Lines format."""
        logger = TokenUsageLogger()

        logger.log(step="step1", model="model1", input_tokens=100, output_tokens=50)
        logger.log(step="step2", model="model2", input_tokens=200, output_tokens=100)

        jsonl = logger.to_jsonl()
        lines = jsonl.strip().split("\n")

        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "tokens" in parsed

    def test_to_csv(self) -> None:
        """Can export to CSV format."""
        logger = TokenUsageLogger()

        logger.log(
            step="step1",
            model="model1",
            provider="provider1",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
        )
        logger.log(
            step="step2",
            model="model2",
            provider="provider2",
            input_tokens=200,
            output_tokens=100,
            cost_usd=0.02,
        )

        csv = logger.to_csv()
        lines = csv.strip().split("\n")

        assert len(lines) == 3  # header + 2 data rows
        assert "timestamp" in lines[0]
        assert "input_tokens" in lines[0]
        assert "model1" in lines[1]
        assert "model2" in lines[2]


class TestLogTokenUsageConvenience:
    """Tests for log_token_usage convenience function."""

    def test_creates_token_usage(self) -> None:
        """log_token_usage creates a TokenUsage record."""
        usage = log_token_usage(
            step="test_step",
            model="test-model",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.05,
        )

        assert isinstance(usage, TokenUsage)
        assert usage.step == "test_step"
        assert usage.model == "test-model"
        assert usage.input_tokens == 1000
        assert usage.output_tokens == 500
        assert usage.cost_usd == 0.05

    def test_timestamp_is_generated(self) -> None:
        """Timestamp is automatically generated."""
        usage = log_token_usage(
            step="test",
            model="model",
            input_tokens=100,
            output_tokens=50,
        )

        # Verify timestamp is recent (within last minute)
        timestamp = datetime.fromisoformat(usage.timestamp.replace("Z", "+00:00"))
        now = datetime.now(UTC)
        diff = (now - timestamp).total_seconds()
        assert diff < 60
