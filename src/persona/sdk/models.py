"""
Pydantic models for the Persona SDK.

This module defines all input/output models with full validation.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ComplexityLevel(str, Enum):
    """Persona generation complexity levels."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class DetailLevel(str, Enum):
    """Output detail levels."""

    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"


class PersonaConfig(BaseModel):
    """
    Configuration for persona generation.

    Example:
        config = PersonaConfig(
            count=5,
            complexity=ComplexityLevel.COMPLEX,
            detail_level=DetailLevel.DETAILED,
        )
    """

    count: int = Field(default=3, ge=1, le=20, description="Number of personas to generate")
    complexity: ComplexityLevel = Field(
        default=ComplexityLevel.MODERATE,
        description="Generation complexity level",
    )
    detail_level: DetailLevel = Field(
        default=DetailLevel.STANDARD,
        description="Output detail level",
    )
    include_reasoning: bool = Field(
        default=False,
        description="Include LLM reasoning in output",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )
    max_tokens: int = Field(
        default=4096,
        ge=100,
        le=100000,
        description="Maximum tokens to generate",
    )
    workflow: str = Field(
        default="default",
        description="Workflow name or path",
    )

    model_config = ConfigDict(use_enum_values=True)


class ExperimentConfig(BaseModel):
    """
    Configuration for creating an experiment.

    Example:
        config = ExperimentConfig(
            name="user-research-2024",
            description="Q4 user research study",
            provider="anthropic",
        )
    """

    name: str = Field(..., min_length=1, max_length=100, description="Experiment name")
    description: str = Field(default="", description="Optional description")
    provider: str = Field(default="anthropic", description="Default LLM provider")
    model: str | None = Field(default=None, description="Model identifier")
    workflow: str = Field(default="default", description="Default workflow")
    count: int = Field(default=3, ge=1, le=20, description="Default persona count")
    complexity: ComplexityLevel = Field(
        default=ComplexityLevel.MODERATE,
        description="Default complexity",
    )
    detail_level: DetailLevel = Field(
        default=DetailLevel.STANDARD,
        description="Default detail level",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate experiment name."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()

    model_config = ConfigDict(use_enum_values=True)


class PersonaModel(BaseModel):
    """
    A generated persona.

    This model represents the output of persona generation,
    with all fields accessible as typed attributes.
    """

    id: str = Field(..., description="Unique persona identifier")
    name: str = Field(..., description="Persona name")
    title: str = Field(default="", description="Persona title or role")
    goals: list[str] = Field(default_factory=list, description="Persona goals")
    pain_points: list[str] = Field(default_factory=list, description="Pain points")
    behaviours: list[str] = Field(default_factory=list, description="Observed behaviours")
    quotes: list[str] = Field(default_factory=list, description="Representative quotes")
    demographics: dict[str, Any] = Field(
        default_factory=dict,
        description="Demographic information",
    )
    additional: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom fields",
    )

    @classmethod
    def from_core_persona(cls, persona: Any) -> "PersonaModel":
        """
        Create PersonaModel from core Persona dataclass.

        Args:
            persona: Core Persona instance.

        Returns:
            PersonaModel instance.
        """
        return cls(
            id=persona.id,
            name=persona.name,
            title=getattr(persona, "title", ""),
            goals=persona.goals or [],
            pain_points=persona.pain_points or [],
            behaviours=persona.behaviours or [],
            quotes=persona.quotes or [],
            demographics=persona.demographics or {},
            additional=persona.additional or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)


class TokenUsageModel(BaseModel):
    """Token usage information."""

    input_tokens: int = Field(default=0, ge=0, description="Input tokens used")
    output_tokens: int = Field(default=0, ge=0, description="Output tokens generated")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens")

    @model_validator(mode="after")
    def compute_total(self) -> "TokenUsageModel":
        """Compute total tokens if not provided."""
        if self.total_tokens == 0:
            object.__setattr__(
                self, "total_tokens", self.input_tokens + self.output_tokens
            )
        return self


class GenerationResultModel(BaseModel):
    """
    Result of persona generation.

    Contains generated personas along with metadata about
    the generation process.
    """

    personas: list[PersonaModel] = Field(
        default_factory=list,
        description="Generated personas",
    )
    reasoning: str | None = Field(
        default=None,
        description="LLM reasoning (if requested)",
    )
    token_usage: TokenUsageModel = Field(
        default_factory=TokenUsageModel,
        description="Token usage statistics",
    )
    model: str = Field(default="", description="Model used for generation")
    provider: str = Field(default="", description="Provider used")
    source_files: list[str] = Field(
        default_factory=list,
        description="Input files processed",
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Generation timestamp",
    )

    @classmethod
    def from_core_result(cls, result: Any) -> "GenerationResultModel":
        """
        Create GenerationResultModel from core GenerationResult.

        Args:
            result: Core GenerationResult instance.

        Returns:
            GenerationResultModel instance.
        """
        return cls(
            personas=[PersonaModel.from_core_persona(p) for p in result.personas],
            reasoning=result.reasoning,
            token_usage=TokenUsageModel(
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
            ),
            model=result.model,
            provider=result.provider,
            source_files=[str(f) for f in result.source_files],
        )

    def to_json(self, output_dir: str | Path) -> Path:
        """
        Save result to JSON file.

        Args:
            output_dir: Output directory path.

        Returns:
            Path to the saved file.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        file_path = output_path / "generation_result.json"
        file_path.write_text(self.model_dump_json(indent=2), encoding="utf-8")
        return file_path

    def to_markdown(self, output_dir: str | Path) -> list[Path]:
        """
        Save personas to Markdown files.

        Args:
            output_dir: Output directory path.

        Returns:
            List of paths to saved files.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        paths = []
        for persona in self.personas:
            file_path = output_path / f"{persona.id}.md"
            content = self._persona_to_markdown(persona)
            file_path.write_text(content, encoding="utf-8")
            paths.append(file_path)

        return paths

    def _persona_to_markdown(self, persona: PersonaModel) -> str:
        """Convert persona to Markdown format."""
        lines = [
            f"# {persona.name}",
            "",
        ]

        if persona.title:
            lines.append(f"**{persona.title}**")
            lines.append("")

        if persona.demographics:
            lines.append("## Demographics")
            for key, value in persona.demographics.items():
                lines.append(f"- **{key.title()}**: {value}")
            lines.append("")

        if persona.goals:
            lines.append("## Goals")
            for goal in persona.goals:
                lines.append(f"- {goal}")
            lines.append("")

        if persona.pain_points:
            lines.append("## Pain Points")
            for pain in persona.pain_points:
                lines.append(f"- {pain}")
            lines.append("")

        if persona.behaviours:
            lines.append("## Behaviours")
            for behaviour in persona.behaviours:
                lines.append(f"- {behaviour}")
            lines.append("")

        if persona.quotes:
            lines.append("## Quotes")
            for quote in persona.quotes:
                lines.append(f"> \"{quote}\"")
                lines.append("")

        return "\n".join(lines)


class ExperimentModel(BaseModel):
    """
    An experiment with its configuration and metadata.
    """

    name: str = Field(..., description="Experiment name")
    path: str = Field(..., description="Path to experiment directory")
    description: str = Field(default="", description="Experiment description")
    provider: str = Field(default="anthropic", description="Default provider")
    model: str | None = Field(default=None, description="Default model")
    workflow: str = Field(default="default", description="Default workflow")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp",
    )
    run_count: int = Field(default=0, ge=0, description="Number of generation runs")

    @classmethod
    def from_core_experiment(cls, experiment: Any) -> "ExperimentModel":
        """
        Create ExperimentModel from core Experiment.

        Args:
            experiment: Core Experiment instance.

        Returns:
            ExperimentModel instance.
        """
        return cls(
            name=experiment.name,
            path=str(experiment.path),
            description=experiment.config.description,
            provider=experiment.config.provider,
            model=experiment.config.model,
            workflow=experiment.config.workflow,
            created_at=experiment.created_at,
            run_count=len(experiment.list_outputs()),
        )

    @property
    def data_dir(self) -> Path:
        """Return path to data directory."""
        return Path(self.path) / "data"

    @property
    def outputs_dir(self) -> Path:
        """Return path to outputs directory."""
        return Path(self.path) / "outputs"
