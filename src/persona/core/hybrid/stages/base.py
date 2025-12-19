"""
Pipeline stage abstractions for the hybrid pipeline.

This module provides the base classes and data structures for
building composable pipeline stages.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StageInput:
    """
    Input data for a pipeline stage.

    Attributes:
        personas: Current list of persona dictionaries.
        raw_data: Original input data (for draft stage).
        config: Pipeline configuration reference.
        count: Number of personas to generate (for draft stage).
        threshold: Quality threshold (for filter stage).
    """

    personas: list[dict[str, Any]] = field(default_factory=list)
    raw_data: str = ""
    config: Any = None  # HybridConfig
    count: int = 0
    threshold: float = 0.0


@dataclass
class StageOutput:
    """
    Output data from a pipeline stage.

    Attributes:
        personas: Resulting persona dictionaries.
        passed: Personas that passed filtering (filter stage).
        failed: Personas that need refinement (filter stage).
        metrics: Stage-specific metrics.
        tokens_used: Token usage statistics.
    """

    personas: list[dict[str, Any]] = field(default_factory=list)
    passed: list[dict[str, Any]] = field(default_factory=list)
    failed: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    tokens_used: dict[str, int] = field(default_factory=dict)


@dataclass
class PipelineContext:
    """
    Shared context for pipeline execution.

    Carries state across stages and provides access to
    shared resources like cost tracking.

    Attributes:
        cost_tracker: Cost tracking instance.
        progress_callback: Optional callback for progress updates.
        stage_results: Results from each stage by name.
        metadata: Additional metadata.
    """

    cost_tracker: Any = None  # CostTracker
    progress_callback: Any = None  # Callable
    stage_results: dict[str, StageOutput] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def record_stage_result(self, stage_name: str, output: StageOutput) -> None:
        """Record the output of a stage for later reference."""
        self.stage_results[stage_name] = output


class PipelineStage(ABC):
    """
    Abstract base class for hybrid pipeline stages.

    All pipeline stages must implement this interface to ensure
    consistent behaviour and enable stage composition.

    Example:
        class MyCustomStage(PipelineStage):
            @property
            def name(self) -> str:
                return "my_custom_stage"

            async def execute(
                self,
                input_data: StageInput,
                context: PipelineContext,
            ) -> StageOutput:
                # Process personas
                processed = self._process(input_data.personas)
                return StageOutput(personas=processed)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the stage name for logging and identification.

        Returns:
            Human-readable stage name.
        """
        ...

    @abstractmethod
    async def execute(
        self,
        input_data: StageInput,
        context: PipelineContext,
    ) -> StageOutput:
        """
        Execute the stage with the provided input and context.

        Args:
            input_data: Input data for this stage.
            context: Shared pipeline context.

        Returns:
            StageOutput with processing results.
        """
        ...

    def should_skip(
        self,
        input_data: StageInput,
        context: PipelineContext,
    ) -> bool:
        """
        Determine if this stage should be skipped.

        Override to implement conditional skipping based on
        input data or context.

        Args:
            input_data: Input data for this stage.
            context: Shared pipeline context.

        Returns:
            True if stage should be skipped.
        """
        return False

    async def pre_execute(
        self,
        input_data: StageInput,
        context: PipelineContext,
    ) -> None:
        """
        Hook called before stage execution.

        Override to perform setup or validation.

        Args:
            input_data: Input data for this stage.
            context: Shared pipeline context.
        """
        pass

    async def post_execute(
        self,
        output: StageOutput,
        context: PipelineContext,
    ) -> None:
        """
        Hook called after stage execution.

        Override to perform cleanup or logging.

        Args:
            output: Output from stage execution.
            context: Shared pipeline context.
        """
        pass
