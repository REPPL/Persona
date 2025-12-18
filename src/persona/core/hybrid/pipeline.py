"""
Hybrid local/frontier pipeline for persona generation.

This module provides the HybridPipeline class that orchestrates the
complete workflow of generating personas using local models and
optionally refining them with frontier models.
"""

import time
from dataclasses import dataclass, field
from typing import Any

from persona.core.hybrid.config import HybridConfig
from persona.core.hybrid.cost import CostTracker
from persona.core.hybrid.stages import draft_personas, filter_personas, refine_personas


@dataclass
class HybridResult:
    """
    Result from hybrid pipeline execution.

    Attributes:
        personas: Final list of generated personas.
        draft_count: Number of personas initially drafted.
        passing_count: Number of personas that passed quality threshold.
        refined_count: Number of personas refined by frontier model.
        cost_tracker: Cost and token tracking information.
        config: Configuration used for generation.
        generation_time: Total time in seconds.
        metadata: Additional execution metadata.
    """

    personas: list[dict[str, Any]]
    draft_count: int
    passing_count: int
    refined_count: int
    cost_tracker: CostTracker
    config: HybridConfig
    generation_time: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def persona_count(self) -> int:
        """Return total number of personas."""
        return len(self.personas)

    @property
    def total_cost(self) -> float:
        """Return total cost in USD."""
        return self.cost_tracker.total_cost

    @property
    def total_tokens(self) -> int:
        """Return total tokens used."""
        return self.cost_tracker.total_tokens

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "persona_count": self.persona_count,
            "draft_count": self.draft_count,
            "passing_count": self.passing_count,
            "refined_count": self.refined_count,
            "generation_time": round(self.generation_time, 2),
            "costs": self.cost_tracker.to_dict(),
            "config": self.config.to_dict(),
            "metadata": self.metadata,
        }


class HybridPipeline:
    """
    Hybrid local/frontier persona generation pipeline.

    Orchestrates the complete workflow:
    1. Draft: Generate initial personas using local Ollama models
    2. Filter: Evaluate quality using PersonaJudge
    3. Refine: Improve low-quality personas using frontier models (optional)

    Example:
        # Local-only mode
        config = HybridConfig(
            local_model="qwen2.5:7b",
            frontier_provider=None
        )
        pipeline = HybridPipeline(config)
        result = await pipeline.generate(input_data=data, count=10)

        # Full hybrid mode
        config = HybridConfig(
            local_model="qwen2.5:7b",
            frontier_provider="anthropic",
            frontier_model="claude-3-5-sonnet-20241022",
            quality_threshold=0.7,
            max_cost=5.0
        )
        pipeline = HybridPipeline(config)
        result = await pipeline.generate(input_data=data, count=10)
    """

    def __init__(self, config: HybridConfig) -> None:
        """
        Initialise hybrid pipeline.

        Args:
            config: Pipeline configuration.
        """
        self.config = config

    async def generate(
        self,
        input_data: str | list[dict[str, Any]],
        count: int,
    ) -> HybridResult:
        """
        Generate personas using hybrid pipeline.

        Args:
            input_data: Raw input data (text or structured data).
            count: Number of personas to generate.

        Returns:
            HybridResult with generated personas and execution metadata.

        Raises:
            RuntimeError: If providers are not configured or generation fails.
            ValueError: If configuration is invalid.

        Example:
            result = await pipeline.generate(
                input_data="User interview transcripts...",
                count=10
            )

            print(f"Generated {result.persona_count} personas")
            print(f"Cost: ${result.total_cost:.4f}")
            print(f"Refined: {result.refined_count}/{result.draft_count}")
        """
        start_time = time.time()

        # Convert input_data to string if needed
        if isinstance(input_data, list):
            import json

            input_data = json.dumps(input_data, indent=2)

        # Initialise cost tracker
        cost_tracker = CostTracker(
            max_budget=self.config.max_cost,
            local_provider=self.config.local_provider,
            local_model=self.config.local_model,
            frontier_provider=self.config.frontier_provider,
            frontier_model=self.config.frontier_model,
            judge_provider=self.config.judge_provider,
            judge_model=self.config.judge_model,
        )

        # Stage 1: Draft personas with local model
        draft_personas_list = await draft_personas(
            input_data=input_data,
            config=self.config,
            count=count,
            cost_tracker=cost_tracker,
        )

        draft_count = len(draft_personas_list)

        # Stage 2: Filter personas by quality
        passing_personas, needs_refinement = await filter_personas(
            personas=draft_personas_list,
            config=self.config,
            cost_tracker=cost_tracker,
        )

        passing_count = len(passing_personas)

        # Stage 3: Refine low-quality personas with frontier model
        refined_personas = []
        if needs_refinement and self.config.is_hybrid_mode:
            refined_personas = await refine_personas(
                personas=needs_refinement,
                config=self.config,
                cost_tracker=cost_tracker,
            )

        refined_count = len([p for p in refined_personas if p.get("_refined", False)])

        # Combine all personas
        final_personas = passing_personas + refined_personas

        # Sort by ID for consistency
        final_personas.sort(key=lambda p: p.get("id", ""))

        generation_time = time.time() - start_time

        # Build metadata
        metadata = {
            "pipeline_mode": "hybrid" if self.config.is_hybrid_mode else "local_only",
            "quality_threshold": self.config.quality_threshold,
            "needs_refinement_count": len(needs_refinement),
            "budget_exceeded": cost_tracker.is_over_budget,
        }

        return HybridResult(
            personas=final_personas,
            draft_count=draft_count,
            passing_count=passing_count,
            refined_count=refined_count,
            cost_tracker=cost_tracker,
            config=self.config,
            generation_time=generation_time,
            metadata=metadata,
        )

    def generate_sync(
        self,
        input_data: str | list[dict[str, Any]],
        count: int,
    ) -> HybridResult:
        """
        Synchronous wrapper for generate().

        This is a convenience method for non-async contexts.

        Args:
            input_data: Raw input data (text or structured data).
            count: Number of personas to generate.

        Returns:
            HybridResult with generated personas and execution metadata.
        """
        import asyncio

        # Try to get existing event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No loop running, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.generate(input_data, count))
            loop.close()
            return result
        else:
            # Loop already running, create task
            return loop.create_task(self.generate(input_data, count))
