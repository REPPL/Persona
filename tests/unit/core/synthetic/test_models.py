"""
Unit tests for synthetic data models.
"""

from pathlib import Path

import pytest
from persona.core.synthetic.models import (
    ColumnType,
    DataSchema,
    DistributionStats,
    GenerationConfig,
    SyntheticResult,
    ValidationResult,
)


def test_column_type_enum():
    """Test ColumnType enum values."""
    assert ColumnType.TEXT == "text"
    assert ColumnType.NUMERIC == "numeric"
    assert ColumnType.CATEGORICAL == "categorical"
    assert ColumnType.BOOLEAN == "boolean"
    assert ColumnType.DATE == "date"
    assert ColumnType.UNKNOWN == "unknown"


def test_distribution_stats_basic():
    """Test DistributionStats model creation."""
    stats = DistributionStats(
        column_name="age",
        column_type=ColumnType.NUMERIC,
        unique_count=50,
        null_count=2,
        sample_values=[25, 30, 35],
    )

    assert stats.column_name == "age"
    assert stats.column_type == "numeric"
    assert stats.unique_count == 50
    assert stats.null_count == 2
    assert len(stats.sample_values) == 3


def test_distribution_stats_categorical():
    """Test DistributionStats with categorical distribution."""
    stats = DistributionStats(
        column_name="role",
        column_type=ColumnType.CATEGORICAL,
        unique_count=5,
        null_count=0,
        categorical_distribution={
            "Engineer": 10,
            "Designer": 8,
            "Manager": 5,
        },
    )

    assert stats.categorical_distribution is not None
    assert "Engineer" in stats.categorical_distribution
    assert stats.categorical_distribution["Engineer"] == 10


def test_distribution_stats_numeric():
    """Test DistributionStats with numeric stats."""
    stats = DistributionStats(
        column_name="salary",
        column_type=ColumnType.NUMERIC,
        unique_count=100,
        null_count=0,
        numeric_stats={
            "min": 50000.0,
            "max": 150000.0,
            "mean": 85000.0,
            "std": 25000.0,
        },
    )

    assert stats.numeric_stats is not None
    assert stats.numeric_stats["min"] == 50000.0
    assert stats.numeric_stats["max"] == 150000.0


def test_data_schema_creation():
    """Test DataSchema model creation."""
    col1 = DistributionStats(
        column_name="name",
        column_type=ColumnType.TEXT,
        unique_count=100,
    )
    col2 = DistributionStats(
        column_name="age",
        column_type=ColumnType.NUMERIC,
        unique_count=50,
    )

    schema = DataSchema(
        columns=[col1, col2],
        row_count=100,
        format="csv",
    )

    assert len(schema.columns) == 2
    assert schema.row_count == 100
    assert schema.format == "csv"


def test_data_schema_get_column():
    """Test DataSchema get_column method."""
    col1 = DistributionStats(
        column_name="name",
        column_type=ColumnType.TEXT,
        unique_count=100,
    )
    col2 = DistributionStats(
        column_name="age",
        column_type=ColumnType.NUMERIC,
        unique_count=50,
    )

    schema = DataSchema(
        columns=[col1, col2],
        row_count=100,
    )

    # Test existing column
    age_col = schema.get_column("age")
    assert age_col is not None
    assert age_col.column_name == "age"

    # Test non-existent column
    missing = schema.get_column("nonexistent")
    assert missing is None


def test_data_schema_column_names():
    """Test DataSchema column_names method."""
    col1 = DistributionStats(column_name="name", column_type=ColumnType.TEXT)
    col2 = DistributionStats(column_name="age", column_type=ColumnType.NUMERIC)
    col3 = DistributionStats(column_name="role", column_type=ColumnType.CATEGORICAL)

    schema = DataSchema(columns=[col1, col2, col3], row_count=100)

    names = schema.column_names()
    assert len(names) == 3
    assert "name" in names
    assert "age" in names
    assert "role" in names


def test_validation_result_creation():
    """Test ValidationResult model creation."""
    result = ValidationResult(
        schema_match=True,
        schema_match_score=1.0,
        distribution_similarity=0.92,
        pii_detected=False,
        pii_entity_count=0,
        passed=True,
    )

    assert result.schema_match is True
    assert result.schema_match_score == 1.0
    assert result.distribution_similarity == 0.92
    assert result.pii_detected is False
    assert result.passed is True


def test_validation_result_quality_score():
    """Test ValidationResult quality_score calculation."""
    # Perfect score
    result = ValidationResult(
        schema_match=True,
        schema_match_score=1.0,
        distribution_similarity=1.0,
        pii_detected=False,
        passed=True,
    )
    assert result.quality_score == 1.0

    # Mixed scores
    result = ValidationResult(
        schema_match=True,
        schema_match_score=0.8,
        distribution_similarity=0.9,
        pii_detected=False,
        passed=True,
    )
    # (0.8 * 0.3) + (0.9 * 0.3) + (1.0 * 0.4) = 0.24 + 0.27 + 0.4 = 0.91
    assert result.quality_score == pytest.approx(0.91, abs=0.01)

    # With PII detected (fails)
    result = ValidationResult(
        schema_match=True,
        schema_match_score=1.0,
        distribution_similarity=1.0,
        pii_detected=True,
        pii_entity_count=5,
        passed=False,
    )
    # (1.0 * 0.3) + (1.0 * 0.3) + (0.0 * 0.4) = 0.6
    assert result.quality_score == pytest.approx(0.6, abs=0.01)


def test_synthetic_result_creation():
    """Test SyntheticResult model creation."""
    schema = DataSchema(
        columns=[DistributionStats(column_name="name", column_type=ColumnType.TEXT)],
        row_count=100,
    )

    result = SyntheticResult(
        input_path=Path("input.csv"),
        output_path=Path("output.csv"),
        data_schema=schema,
        row_count=100,
        model="qwen2.5:72b",
        provider="ollama",
        generation_time=45.2,
    )

    assert result.input_path == Path("input.csv")
    assert result.output_path == Path("output.csv")
    assert result.data_schema == schema
    assert result.row_count == 100
    assert result.model == "qwen2.5:72b"
    assert result.provider == "ollama"
    assert result.generation_time == 45.2


def test_generation_config_defaults():
    """Test GenerationConfig default values."""
    config = GenerationConfig()

    assert config.provider == "ollama"
    assert config.model is None
    assert config.count == 100
    assert config.preserve_schema is True
    assert config.preserve_distribution is True
    assert config.batch_size == 10
    assert config.temperature == 0.7
    assert config.should_validate is True


def test_generation_config_custom():
    """Test GenerationConfig with custom values."""
    config = GenerationConfig(
        provider="anthropic",
        model="claude-opus-4",
        count=50,
        batch_size=5,
        temperature=0.5,
        should_validate=False,
    )

    assert config.provider == "anthropic"
    assert config.model == "claude-opus-4"
    assert config.count == 50
    assert config.batch_size == 5
    assert config.temperature == 0.5
    assert config.should_validate is False
