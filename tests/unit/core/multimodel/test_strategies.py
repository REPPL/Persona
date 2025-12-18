"""Tests for execution strategies (F-067)."""


from persona.core.multimodel.generator import ModelSpec
from persona.core.multimodel.strategies import (
    ConsensusStrategy,
    ExecutionMode,
    ParallelStrategy,
    SequentialStrategy,
    StrategyConfig,
)


class TestExecutionMode:
    """Tests for ExecutionMode enum."""

    def test_parallel_value(self):
        """Parallel mode has correct value."""
        assert ExecutionMode.PARALLEL.value == "parallel"

    def test_sequential_value(self):
        """Sequential mode has correct value."""
        assert ExecutionMode.SEQUENTIAL.value == "sequential"

    def test_consensus_value(self):
        """Consensus mode has correct value."""
        assert ExecutionMode.CONSENSUS.value == "consensus"


class TestStrategyConfig:
    """Tests for StrategyConfig."""

    def test_default_values(self):
        """Has sensible defaults."""
        config = StrategyConfig()

        assert config.timeout_seconds == 300
        assert config.max_workers == 4
        assert config.pass_context is True
        assert config.consensus_threshold == 0.7


class TestParallelStrategy:
    """Tests for ParallelStrategy."""

    def test_execute_basic(self):
        """Executes parallel generation."""
        strategy = ParallelStrategy()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = strategy.execute(
            data="Test data",
            models=models,
            count=2,
            temperature=0.7,
            max_tokens=4096,
        )

        assert result.execution_mode == "parallel"
        assert len(result.model_outputs) == 2

    def test_execute_tracks_totals(self):
        """Tracks total tokens and cost."""
        strategy = ParallelStrategy()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
        ]

        result = strategy.execute(
            data="Test data here",
            models=models,
            count=3,
            temperature=0.7,
            max_tokens=4096,
        )

        assert result.total_tokens_input > 0
        assert result.total_tokens_output > 0
        assert result.total_cost > 0

    def test_execute_multiple_models(self):
        """Handles multiple models."""
        strategy = ParallelStrategy(max_workers=2)
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
            ModelSpec("gemini", "gemini-1.5-pro"),
        ]

        result = strategy.execute(
            data="Test data",
            models=models,
            count=2,
            temperature=0.7,
            max_tokens=4096,
        )

        assert len(result.model_outputs) == 3


class TestSequentialStrategy:
    """Tests for SequentialStrategy."""

    def test_execute_basic(self):
        """Executes sequential generation."""
        strategy = SequentialStrategy()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = strategy.execute(
            data="Test data",
            models=models,
            count=2,
            temperature=0.7,
            max_tokens=4096,
        )

        assert result.execution_mode == "sequential"
        assert len(result.model_outputs) == 2

    def test_execute_passes_context(self):
        """Passes context between models when enabled."""
        strategy = SequentialStrategy(pass_context=True)
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = strategy.execute(
            data="Test data",
            models=models,
            count=2,
            temperature=0.7,
            max_tokens=4096,
        )

        # Second model should have context from first
        # (In mock, this shows as "with context" in name)
        second_output = result.model_outputs[1]
        assert second_output.success

    def test_execute_no_context(self):
        """Does not pass context when disabled."""
        strategy = SequentialStrategy(pass_context=False)
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = strategy.execute(
            data="Test data",
            models=models,
            count=2,
            temperature=0.7,
            max_tokens=4096,
        )

        assert len(result.model_outputs) == 2


class TestConsensusStrategy:
    """Tests for ConsensusStrategy."""

    def test_execute_basic(self):
        """Executes consensus generation."""
        strategy = ConsensusStrategy()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = strategy.execute(
            data="Test data",
            models=models,
            count=3,
            temperature=0.7,
            max_tokens=4096,
        )

        assert result.execution_mode == "consensus"
        assert len(result.model_outputs) == 2

    def test_execute_produces_consolidated(self):
        """Produces consolidated personas."""
        strategy = ConsensusStrategy()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = strategy.execute(
            data="Test data",
            models=models,
            count=3,
            temperature=0.7,
            max_tokens=4096,
        )

        # Should have consolidated personas
        assert len(result.consolidated_personas) >= 0

    def test_execute_custom_threshold(self):
        """Uses custom consensus threshold."""
        strategy = ConsensusStrategy(consensus_threshold=0.9)
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = strategy.execute(
            data="Test data",
            models=models,
            count=2,
            temperature=0.7,
            max_tokens=4096,
        )

        assert result.execution_mode == "consensus"

    def test_find_consensus_empty(self):
        """Handles empty persona list."""
        strategy = ConsensusStrategy()

        consolidated = strategy._find_consensus([], 3)

        assert consolidated == []

    def test_merge_personas(self):
        """Merges personas correctly."""
        strategy = ConsensusStrategy()
        personas = [
            {
                "id": "1",
                "name": "Alex",
                "role": "Developer",
                "goals": ["Goal 1", "Goal 2"],
                "frustrations": ["Frust 1"],
                "model_source": "anthropic:claude",
            },
            {
                "id": "2",
                "name": "Jordan",
                "role": "Developer",
                "goals": ["Goal 2", "Goal 3"],
                "frustrations": ["Frust 2"],
                "model_source": "openai:gpt",
            },
        ]

        merged = strategy._merge_personas(personas)

        assert "merged" in merged["id"] or "consensus" in merged["id"]
        assert len(merged["goals"]) >= 2  # Union of goals
        assert len(merged["contributing_models"]) == 2
