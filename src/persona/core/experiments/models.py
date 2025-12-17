"""
Pydantic models for experiment management.

Provides type-safe data structures for experiments, variants, and runs.
These models are used for validation, serialisation, and API contracts.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExperimentStatus(str, Enum):
    """Status of an experiment."""

    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class RunStatus(str, Enum):
    """Status of a run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VariantModel(BaseModel):
    """
    A variant represents a named set of parameters for an experiment.

    Variants allow comparing different configurations within the same
    experiment, such as different models, prompts, or settings.

    Example:
        ```python
        variant = VariantModel(
            variant_id="abc123",
            experiment_id="exp456",
            name="high-temperature",
            parameters={"temperature": 0.9, "top_p": 0.95},
            description="More creative outputs"
        )
        ```
    """

    variant_id: str = Field(..., description="Unique variant identifier")
    experiment_id: str = Field(..., description="Parent experiment ID")
    name: str = Field(..., description="Variant name (unique within experiment)")
    description: str = Field(default="", description="Optional description")
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameter overrides for this variant",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the variant was created",
    )

    model_config = ConfigDict(use_enum_values=True)


class ExperimentModel(BaseModel):
    """
    An experiment groups related generation runs.

    Experiments can be linked to a project and contain multiple variants
    (named parameter sets) and runs.

    Example:
        ```python
        experiment = ExperimentModel(
            experiment_id="exp123",
            name="user-research-2025",
            description="Generating personas from user interviews",
            hypothesis="GPT-4 will produce more detailed personas"
        )
        ```
    """

    experiment_id: str = Field(..., description="Unique experiment identifier")
    project_id: str | None = Field(
        default=None,
        description="Parent project ID (optional)",
    )
    name: str = Field(..., description="Experiment name")
    description: str = Field(default="", description="Experiment description")
    hypothesis: str | None = Field(
        default=None,
        description="Research hypothesis being tested",
    )
    status: ExperimentStatus = Field(
        default=ExperimentStatus.PLANNED,
        description="Current experiment status",
    )
    config: dict[str, Any] | None = Field(
        default=None,
        description="Default configuration for runs",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the experiment was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="When the experiment was last updated",
    )

    model_config = ConfigDict(use_enum_values=True)


class RunModel(BaseModel):
    """
    A run represents a single execution of persona generation.

    Runs track the model used, parameters, metrics, and results.

    Example:
        ```python
        run = RunModel(
            run_id="run789",
            experiment_id="exp123",
            run_number=1,
            model="claude-sonnet-4-20250514",
            provider="anthropic",
            persona_count=5,
            cost=0.0045
        )
        ```
    """

    run_id: str = Field(..., description="Unique run identifier")
    experiment_id: str = Field(..., description="Parent experiment ID")
    variant_id: str | None = Field(
        default=None,
        description="Variant used (if any)",
    )
    run_number: int = Field(..., description="Sequential run number within experiment")
    model: str = Field(..., description="Model identifier used")
    provider: str = Field(..., description="Provider name")
    status: RunStatus = Field(
        default=RunStatus.RUNNING,
        description="Current run status",
    )
    parameters: dict[str, Any] | None = Field(
        default=None,
        description="Parameters used for this run",
    )
    output_dir: str = Field(default="", description="Path to output directory")

    # Metrics
    persona_count: int = Field(default=0, description="Number of personas generated")
    input_tokens: int = Field(default=0, description="Total input tokens used")
    output_tokens: int = Field(default=0, description="Total output tokens used")
    cost: float = Field(default=0.0, description="Estimated cost in USD")
    duration_seconds: float = Field(default=0.0, description="Run duration in seconds")
    metrics: dict[str, Any] | None = Field(
        default=None,
        description="Additional metrics",
    )

    # Audit trail link
    audit_id: str | None = Field(
        default=None,
        description="Link to audit trail entry",
    )

    # Timestamps
    started_at: datetime = Field(
        default_factory=datetime.now,
        description="When the run started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the run completed",
    )

    model_config = ConfigDict(use_enum_values=True)


class ExperimentStatistics(BaseModel):
    """Aggregate statistics for an experiment."""

    total_runs: int = Field(default=0, description="Total number of runs")
    completed_runs: int = Field(default=0, description="Completed runs")
    failed_runs: int = Field(default=0, description="Failed runs")
    running_runs: int = Field(default=0, description="Currently running")
    total_personas: int = Field(default=0, description="Total personas generated")
    total_cost: float = Field(default=0.0, description="Total cost in USD")
    total_input_tokens: int = Field(default=0, description="Total input tokens")
    total_output_tokens: int = Field(default=0, description="Total output tokens")
    avg_cost_per_run: float = Field(default=0.0, description="Average cost per run")
    avg_personas_per_run: float = Field(
        default=0.0,
        description="Average personas per run",
    )
    models_used: list[str] = Field(
        default_factory=list,
        description="Models used in runs",
    )
    providers_used: list[str] = Field(
        default_factory=list,
        description="Providers used in runs",
    )


class RunComparison(BaseModel):
    """Comparison between two runs."""

    run_1: RunModel = Field(..., description="First run")
    run_2: RunModel = Field(..., description="Second run")
    differences: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Fields that differ between runs",
    )
    delta: dict[str, float] = Field(
        default_factory=dict,
        description="Numeric differences (run_2 - run_1)",
    )
