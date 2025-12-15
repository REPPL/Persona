"""Unit tests for hybrid pipeline."""

import pytest

from persona.core.hybrid.config import HybridConfig
from persona.core.hybrid.pipeline import HybridPipeline, HybridResult


@pytest.fixture
def local_only_config():
    """Create local-only configuration."""
    return HybridConfig(
        local_model="qwen2.5:7b",
        frontier_provider=None,
    )


@pytest.fixture
def hybrid_config():
    """Create hybrid configuration."""
    return HybridConfig(
        local_model="qwen2.5:7b",
        frontier_provider="anthropic",
        frontier_model="claude-3-5-sonnet-20241022",
        quality_threshold=0.7,
        max_cost=5.0,
    )


def test_hybrid_pipeline_init(local_only_config):
    """Test pipeline initialisation."""
    pipeline = HybridPipeline(local_only_config)
    assert pipeline.config == local_only_config


def test_hybrid_result_properties():
    """Test HybridResult properties."""
    from persona.core.hybrid.cost import CostTracker

    config = HybridConfig()
    tracker = CostTracker()
    tracker.add_local_usage(1000, 500)

    result = HybridResult(
        personas=[
            {"id": "p1", "name": "Alice"},
            {"id": "p2", "name": "Bob"},
        ],
        draft_count=3,
        passing_count=2,
        refined_count=0,
        cost_tracker=tracker,
        config=config,
        generation_time=5.5,
    )

    assert result.persona_count == 2
    assert result.total_cost == 0.0  # Ollama is free
    assert result.total_tokens == 1500
    assert result.generation_time == 5.5


def test_hybrid_result_to_dict():
    """Test HybridResult conversion to dictionary."""
    from persona.core.hybrid.cost import CostTracker

    config = HybridConfig()
    tracker = CostTracker()

    result = HybridResult(
        personas=[{"id": "p1", "name": "Alice"}],
        draft_count=1,
        passing_count=1,
        refined_count=0,
        cost_tracker=tracker,
        config=config,
        generation_time=2.5,
        metadata={"test": "value"},
    )

    result_dict = result.to_dict()

    assert result_dict["persona_count"] == 1
    assert result_dict["draft_count"] == 1
    assert result_dict["passing_count"] == 1
    assert result_dict["refined_count"] == 0
    assert result_dict["generation_time"] == 2.5
    assert "costs" in result_dict
    assert "config" in result_dict
    assert result_dict["metadata"]["test"] == "value"


# Note: Full integration tests that actually call LLMs would be marked with
# @pytest.mark.real_api and require actual API keys/Ollama running.
# These are basic unit tests for the pipeline structure.
