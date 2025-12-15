"""Unit tests for hybrid configuration."""

import pytest

from persona.core.hybrid.config import HybridConfig


def test_hybrid_config_defaults():
    """Test default configuration values."""
    config = HybridConfig()

    assert config.local_provider == "ollama"
    assert config.local_model == "qwen2.5:7b"
    assert config.frontier_provider is None
    assert config.frontier_model is None
    assert config.quality_threshold == 0.7
    assert config.max_cost is None
    assert config.batch_size == 10
    assert config.enable_pii_filter is True


def test_hybrid_config_local_only():
    """Test local-only configuration."""
    config = HybridConfig(
        local_model="llama3:8b",
        frontier_provider=None,
    )

    assert config.is_local_only
    assert not config.is_hybrid_mode
    assert config.local_model == "llama3:8b"


def test_hybrid_config_full_hybrid():
    """Test full hybrid configuration."""
    config = HybridConfig(
        local_model="qwen2.5:7b",
        frontier_provider="anthropic",
        frontier_model="claude-3-5-sonnet-20241022",
        quality_threshold=0.8,
        max_cost=10.0,
    )

    assert config.is_hybrid_mode
    assert not config.is_local_only
    assert config.frontier_provider == "anthropic"
    assert config.frontier_model == "claude-3-5-sonnet-20241022"
    assert config.quality_threshold == 0.8
    assert config.max_cost == 10.0


def test_hybrid_config_validation_threshold():
    """Test validation of quality threshold."""
    # Valid thresholds
    HybridConfig(quality_threshold=0.0)
    HybridConfig(quality_threshold=0.5)
    HybridConfig(quality_threshold=1.0)

    # Invalid thresholds
    with pytest.raises(ValueError, match="quality_threshold"):
        HybridConfig(quality_threshold=-0.1)

    with pytest.raises(ValueError, match="quality_threshold"):
        HybridConfig(quality_threshold=1.1)


def test_hybrid_config_validation_cost():
    """Test validation of max cost."""
    # Valid costs
    HybridConfig(max_cost=None)
    HybridConfig(max_cost=1.0)
    HybridConfig(max_cost=100.0)

    # Invalid costs
    with pytest.raises(ValueError, match="max_cost"):
        HybridConfig(max_cost=0.0)

    with pytest.raises(ValueError, match="max_cost"):
        HybridConfig(max_cost=-1.0)


def test_hybrid_config_validation_batch_size():
    """Test validation of batch size."""
    # Valid batch sizes
    HybridConfig(batch_size=1)
    HybridConfig(batch_size=10)
    HybridConfig(batch_size=100)

    # Invalid batch sizes
    with pytest.raises(ValueError, match="batch_size"):
        HybridConfig(batch_size=0)

    with pytest.raises(ValueError, match="batch_size"):
        HybridConfig(batch_size=-1)


def test_hybrid_config_validation_frontier():
    """Test validation of frontier configuration."""
    # Valid: both provider and model
    HybridConfig(
        frontier_provider="anthropic",
        frontier_model="claude-3-5-sonnet-20241022",
    )

    # Valid: neither provider nor model
    HybridConfig(
        frontier_provider=None,
        frontier_model=None,
    )

    # Invalid: provider without model
    with pytest.raises(ValueError, match="frontier_model required"):
        HybridConfig(
            frontier_provider="anthropic",
            frontier_model=None,
        )


def test_hybrid_config_to_dict():
    """Test conversion to dictionary."""
    config = HybridConfig(
        local_model="llama3:8b",
        frontier_provider="anthropic",
        frontier_model="claude-3-5-sonnet-20241022",
        quality_threshold=0.75,
        max_cost=5.0,
    )

    config_dict = config.to_dict()

    assert config_dict["local_model"] == "llama3:8b"
    assert config_dict["frontier_provider"] == "anthropic"
    assert config_dict["frontier_model"] == "claude-3-5-sonnet-20241022"
    assert config_dict["quality_threshold"] == 0.75
    assert config_dict["max_cost"] == 5.0
    assert config_dict["is_hybrid_mode"] is True
