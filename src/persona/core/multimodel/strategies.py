"""Execution strategies for multi-model generation (F-067).

Provides parallel, sequential, and consensus execution modes
for generating personas with multiple LLM models.
"""

import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ExecutionMode(Enum):
    """Execution mode for multi-model generation."""

    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    CONSENSUS = "consensus"


@dataclass
class StrategyConfig:
    """Configuration for execution strategy.

    Attributes:
        timeout_seconds: Timeout per model call.
        max_workers: Maximum parallel workers (for parallel mode).
        pass_context: Whether to pass context between models (sequential).
        consensus_threshold: Similarity threshold for consensus.
    """

    timeout_seconds: int = 300
    max_workers: int = 4
    pass_context: bool = True
    consensus_threshold: float = 0.7


class ExecutionStrategy(ABC):
    """Base class for execution strategies.

    Subclasses implement specific execution patterns for
    multi-model persona generation.
    """

    def __init__(self, timeout_seconds: int = 300):
        """Initialise the strategy.

        Args:
            timeout_seconds: Timeout per model call.
        """
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    def execute(
        self,
        data: str | Path,
        models: list,
        count: int,
        temperature: float,
        max_tokens: int,
    ):
        """Execute the generation strategy.

        Args:
            data: Source data for generation.
            models: List of ModelSpec objects.
            count: Number of personas per model.
            temperature: Temperature for generation.
            max_tokens: Max tokens for generation.

        Returns:
            MultiModelResult with outputs from all models.
        """
        pass

    def _generate_single(
        self,
        data: str | Path,
        model,
        count: int,
        temperature: float,
        max_tokens: int,
        context: str | None = None,
    ):
        """Generate personas using a single model.

        Args:
            data: Source data.
            model: ModelSpec object.
            count: Number of personas.
            temperature: Temperature override.
            max_tokens: Max tokens override.
            context: Optional context from previous model.

        Returns:
            ModelOutput with generation results.
        """
        from persona.core.multimodel.generator import ModelOutput

        start_time = time.time()

        try:
            # Use model-specific settings or defaults
            temp = model.temperature if model.temperature is not None else temperature
            tokens = model.max_tokens if model.max_tokens is not None else max_tokens

            # Simulate generation (in production, this calls the LLM)
            personas = self._mock_generate(data, model, count, context)

            latency_ms = (time.time() - start_time) * 1000

            # Estimate tokens
            data_str = str(data) if isinstance(data, Path) else data
            tokens_input = len(data_str.split()) * 2
            tokens_output = count * 500

            # Estimate cost
            cost = self._estimate_cost(model, tokens_input, tokens_output)

            return ModelOutput(
                model_spec=model,
                personas=personas,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                latency_ms=latency_ms,
                cost=cost,
            )
        except Exception as e:
            return ModelOutput(
                model_spec=model,
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )

    def _mock_generate(
        self,
        data: str | Path,
        model,
        count: int,
        context: str | None = None,
    ) -> list[dict[str, Any]]:
        """Mock persona generation."""
        personas = []
        context_suffix = " (with context)" if context else ""
        for i in range(count):
            personas.append(
                {
                    "id": f"persona-{i+1}",
                    "name": f"Persona {i+1} ({model.model}){context_suffix}",
                    "role": "User",
                    "goals": ["Goal 1", "Goal 2"],
                    "frustrations": ["Frustration 1"],
                    "model_source": f"{model.provider}:{model.model}",
                }
            )
        return personas

    def _estimate_cost(self, model, tokens_input: int, tokens_output: int) -> float:
        """Estimate cost for a model call."""
        pricing = {
            "anthropic": {"input": 3.0, "output": 15.0},
            "openai": {"input": 5.0, "output": 15.0},
            "gemini": {"input": 0.5, "output": 1.5},
        }
        rates = pricing.get(model.provider, {"input": 3.0, "output": 15.0})
        input_cost = (tokens_input / 1_000_000) * rates["input"]
        output_cost = (tokens_output / 1_000_000) * rates["output"]
        return round(input_cost + output_cost, 6)


class ParallelStrategy(ExecutionStrategy):
    """Parallel execution strategy.

    Runs all models simultaneously for maximum speed.
    Results are combined without modification.
    """

    def __init__(self, timeout_seconds: int = 300, max_workers: int = 4):
        """Initialise parallel strategy.

        Args:
            timeout_seconds: Timeout per model.
            max_workers: Maximum concurrent workers.
        """
        super().__init__(timeout_seconds)
        self.max_workers = max_workers

    def execute(
        self,
        data: str | Path,
        models: list,
        count: int,
        temperature: float,
        max_tokens: int,
    ):
        """Execute generation in parallel.

        All models run concurrently. Total latency is approximately
        the latency of the slowest model.
        """
        from persona.core.multimodel.generator import MultiModelResult

        start_time = time.time()
        model_outputs = []

        with ThreadPoolExecutor(
            max_workers=min(len(models), self.max_workers)
        ) as executor:
            futures = {
                executor.submit(
                    self._generate_single,
                    data,
                    model,
                    count,
                    temperature,
                    max_tokens,
                ): model
                for model in models
            }

            for future in as_completed(futures, timeout=self.timeout_seconds):
                try:
                    output = future.result()
                    model_outputs.append(output)
                except Exception as e:
                    model = futures[future]
                    from persona.core.multimodel.generator import ModelOutput

                    model_outputs.append(
                        ModelOutput(
                            model_spec=model,
                            error=str(e),
                        )
                    )

        total_latency = (time.time() - start_time) * 1000

        return MultiModelResult(
            model_outputs=model_outputs,
            execution_mode="parallel",
            total_tokens_input=sum(o.tokens_input for o in model_outputs),
            total_tokens_output=sum(o.tokens_output for o in model_outputs),
            total_cost=sum(o.cost for o in model_outputs),
            total_latency_ms=total_latency,
        )


class SequentialStrategy(ExecutionStrategy):
    """Sequential execution strategy.

    Runs models in order, passing context from each to the next.
    Useful for refinement chains.
    """

    def __init__(self, timeout_seconds: int = 300, pass_context: bool = True):
        """Initialise sequential strategy.

        Args:
            timeout_seconds: Timeout per model.
            pass_context: Whether to pass output to next model.
        """
        super().__init__(timeout_seconds)
        self.pass_context = pass_context

    def execute(
        self,
        data: str | Path,
        models: list,
        count: int,
        temperature: float,
        max_tokens: int,
    ):
        """Execute generation sequentially.

        Each model runs after the previous completes. If pass_context
        is True, output from each model is passed to the next.
        """
        from persona.core.multimodel.generator import MultiModelResult

        start_time = time.time()
        model_outputs = []
        context = None

        for model in models:
            output = self._generate_single(
                data,
                model,
                count,
                temperature,
                max_tokens,
                context=context,
            )
            model_outputs.append(output)

            # Pass context to next model if enabled
            if self.pass_context and output.success:
                context = self._format_context(output.personas)

        total_latency = (time.time() - start_time) * 1000

        return MultiModelResult(
            model_outputs=model_outputs,
            execution_mode="sequential",
            total_tokens_input=sum(o.tokens_input for o in model_outputs),
            total_tokens_output=sum(o.tokens_output for o in model_outputs),
            total_cost=sum(o.cost for o in model_outputs),
            total_latency_ms=total_latency,
        )

    def _format_context(self, personas: list[dict]) -> str:
        """Format personas as context for next model."""
        lines = ["Previous model generated these personas:"]
        for p in personas:
            lines.append(
                f"- {p.get('name', 'Unknown')}: {p.get('role', 'Unknown role')}"
            )
        return "\n".join(lines)


class ConsensusStrategy(ExecutionStrategy):
    """Consensus execution strategy.

    Runs all models independently, then finds agreement between outputs.
    Produces consolidated personas with confidence scores.
    """

    def __init__(
        self,
        timeout_seconds: int = 300,
        consensus_threshold: float = 0.7,
        max_workers: int = 4,
    ):
        """Initialise consensus strategy.

        Args:
            timeout_seconds: Timeout per model.
            consensus_threshold: Similarity threshold for merging.
            max_workers: Maximum concurrent workers.
        """
        super().__init__(timeout_seconds)
        self.consensus_threshold = consensus_threshold
        self.max_workers = max_workers

    def execute(
        self,
        data: str | Path,
        models: list,
        count: int,
        temperature: float,
        max_tokens: int,
    ):
        """Execute generation with consensus.

        Step 1: Generate independently with all models (parallel).
        Step 2: Cluster similar personas across models.
        Step 3: Create consensus personas from clusters.
        """
        from persona.core.multimodel.generator import MultiModelResult

        start_time = time.time()

        # Step 1: Parallel generation
        parallel = ParallelStrategy(self.timeout_seconds, self.max_workers)
        parallel_result = parallel.execute(data, models, count, temperature, max_tokens)

        # Step 2 & 3: Find consensus
        consolidated = self._find_consensus(parallel_result.all_personas, count)

        total_latency = (time.time() - start_time) * 1000

        return MultiModelResult(
            model_outputs=parallel_result.model_outputs,
            execution_mode="consensus",
            total_tokens_input=parallel_result.total_tokens_input,
            total_tokens_output=parallel_result.total_tokens_output,
            total_cost=parallel_result.total_cost,
            total_latency_ms=total_latency,
            consolidated_personas=consolidated,
        )

    def _find_consensus(
        self,
        all_personas: list[dict],
        target_count: int,
    ) -> list[dict]:
        """Find consensus among personas from different models.

        Uses simple role-based clustering for now. In production,
        this would use semantic similarity.
        """
        if not all_personas:
            return []

        # Group by role (simplified clustering)
        role_groups: dict[str, list[dict]] = {}
        for persona in all_personas:
            role = persona.get("role", "Unknown")
            if role not in role_groups:
                role_groups[role] = []
            role_groups[role].append(persona)

        # Create consensus personas from groups
        consolidated = []
        for role, group in sorted(role_groups.items(), key=lambda x: -len(x[1])):
            if len(consolidated) >= target_count:
                break

            # Merge personas in group
            merged = self._merge_personas(group)
            merged["consensus_count"] = len(group)
            merged["consensus_confidence"] = min(
                1.0, len(group) / len(all_personas) * 2
            )
            consolidated.append(merged)

        return consolidated

    def _merge_personas(self, personas: list[dict]) -> dict:
        """Merge multiple personas into one consensus persona."""
        if not personas:
            return {}

        # Use first persona as base
        merged = dict(personas[0])
        merged["id"] = "consensus-" + merged.get("id", "1")
        merged["name"] = merged.get("name", "Consensus Persona")

        # Track which models contributed
        sources = set()
        for p in personas:
            if "model_source" in p:
                sources.add(p["model_source"])
        merged["contributing_models"] = list(sources)

        # Merge goals (union)
        all_goals = []
        for p in personas:
            all_goals.extend(p.get("goals", []))
        merged["goals"] = list(set(all_goals))[:5]

        # Merge frustrations (union)
        all_frustrations = []
        for p in personas:
            all_frustrations.extend(p.get("frustrations", []))
        merged["frustrations"] = list(set(all_frustrations))[:3]

        return merged
