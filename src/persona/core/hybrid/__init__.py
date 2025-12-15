"""
Hybrid local/frontier pipeline for cost-efficient persona generation.

This module provides a hybrid pipeline that uses local Ollama models for
initial draft generation and optional frontier models (Anthropic/OpenAI)
for quality refinement based on automated quality thresholds.

Example:
    from persona.core.hybrid import HybridPipeline, HybridConfig

    config = HybridConfig(
        local_model="qwen2.5:7b",
        frontier_provider="anthropic",
        frontier_model="claude-3-5-sonnet-20241022",
        quality_threshold=0.7
    )

    pipeline = HybridPipeline(config)
    result = await pipeline.generate(input_data=data, count=10)
"""

from persona.core.hybrid.config import HybridConfig
from persona.core.hybrid.pipeline import HybridPipeline, HybridResult

__all__ = [
    "HybridConfig",
    "HybridPipeline",
    "HybridResult",
]
