"""
Pydantic models for synthetic data generation.

This module defines data models used in the synthetic data generation
pipeline, including schema definitions, validation results, and
generation outputs.
"""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ColumnType(str, Enum):
    """Data type categories for columns."""

    TEXT = "text"
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    DATE = "date"
    UNKNOWN = "unknown"


class DistributionStats(BaseModel):
    """
    Statistical distribution information for a column.

    Attributes:
        column_name: Name of the column.
        column_type: Inferred data type.
        unique_count: Number of unique values.
        null_count: Number of null/empty values.
        sample_values: Sample of actual values (up to 5).
        categorical_distribution: Frequency map for categorical data.
        numeric_stats: Statistics for numeric data (min, max, mean, std).
    """

    column_name: str
    column_type: ColumnType
    unique_count: int = 0
    null_count: int = 0
    sample_values: list[Any] = Field(default_factory=list)
    categorical_distribution: dict[str, int] | None = None
    numeric_stats: dict[str, float] | None = None

    model_config = ConfigDict(use_enum_values=True)


class DataSchema(BaseModel):
    """
    Schema representation of input data.

    Attributes:
        columns: List of column distributions.
        row_count: Total number of rows in source data.
        format: Original data format (csv, json, yaml).
        relationships: Detected relationships between columns.
    """

    columns: list[DistributionStats]
    row_count: int
    format: str = "csv"
    relationships: dict[str, list[str]] = Field(default_factory=dict)

    def get_column(self, name: str) -> DistributionStats | None:
        """Get distribution stats for a specific column."""
        for col in self.columns:
            if col.column_name == name:
                return col
        return None

    def column_names(self) -> list[str]:
        """Return list of all column names."""
        return [col.column_name for col in self.columns]


class SyntheticResult(BaseModel):
    """
    Result of synthetic data generation.

    Attributes:
        input_path: Path to original input file.
        output_path: Path to generated synthetic file.
        schema: Schema of the generated data.
        row_count: Number of synthetic rows generated.
        model: LLM model used for generation.
        provider: LLM provider used.
        generation_time: Time taken for generation (seconds).
        validation: Optional validation results.
        metadata: Additional metadata.
    """

    input_path: Path
    output_path: Path
    data_schema: DataSchema  # Renamed from 'schema' to avoid shadowing
    row_count: int
    model: str
    provider: str
    generation_time: float
    validation: "ValidationResult | None" = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ValidationResult(BaseModel):
    """
    Validation result for synthetic data quality.

    Attributes:
        schema_match: Whether schema matches exactly (100%).
        schema_match_score: Percentage of schema match (0-1).
        distribution_similarity: Statistical similarity score (0-1).
        pii_detected: Whether PII was found in synthetic data.
        pii_entity_count: Number of PII entities detected.
        pii_entity_types: Types of PII entities found.
        semantic_similarity: Semantic similarity score (0-1).
        diversity_score: Diversity of generated records (0-1).
        passed: Whether validation passed all checks.
        issues: List of validation issues found.
    """

    schema_match: bool
    schema_match_score: float = Field(ge=0.0, le=1.0)
    distribution_similarity: float = Field(ge=0.0, le=1.0)
    pii_detected: bool
    pii_entity_count: int = 0
    pii_entity_types: list[str] = Field(default_factory=list)
    semantic_similarity: float | None = Field(None, ge=0.0, le=1.0)
    diversity_score: float | None = Field(None, ge=0.0, le=1.0)
    passed: bool
    issues: list[str] = Field(default_factory=list)

    @property
    def quality_score(self) -> float:
        """
        Overall quality score (0-1).

        Weighted average of all metrics where:
        - Schema match: 30%
        - Distribution similarity: 30%
        - No PII: 40%
        """
        pii_score = 0.0 if self.pii_detected else 1.0
        return (
            self.schema_match_score * 0.3
            + self.distribution_similarity * 0.3
            + pii_score * 0.4
        )


class GenerationConfig(BaseModel):
    """
    Configuration for synthetic data generation.

    Attributes:
        provider: LLM provider to use (ollama, anthropic, openai, gemini).
        model: Specific model to use.
        count: Number of synthetic records to generate.
        preserve_schema: Whether to match original schema exactly.
        preserve_distribution: Whether to preserve statistical distribution.
        batch_size: Number of records to generate per API call.
        temperature: Temperature for LLM generation.
        validate: Whether to validate output after generation.
    """

    provider: str = "ollama"
    model: str | None = None
    count: int = 100
    preserve_schema: bool = True
    preserve_distribution: bool = True
    batch_size: int = 10
    temperature: float = 0.7
    should_validate: bool = True  # Renamed from 'validate' to avoid shadowing
