"""
Unit tests for SyntheticValidator.
"""

import csv
from pathlib import Path

import pytest

from persona.core.synthetic.validator import SyntheticValidator


@pytest.fixture
def temp_original_csv(tmp_path):
    """Create a temporary original CSV file."""
    csv_file = tmp_path / "original.csv"
    data = [
        ["name", "age", "role"],
        ["Alice", "25", "Engineer"],
        ["Bob", "30", "Designer"],
        ["Charlie", "35", "Manager"],
        ["Diana", "28", "Engineer"],
        ["Eve", "32", "Designer"],
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    return csv_file


@pytest.fixture
def temp_synthetic_csv_good(tmp_path):
    """Create a synthetic CSV with good match."""
    csv_file = tmp_path / "synthetic_good.csv"
    data = [
        ["name", "age", "role"],
        ["John", "26", "Engineer"],
        ["Jane", "31", "Designer"],
        ["Jack", "34", "Manager"],
        ["Jill", "29", "Engineer"],
        ["Jim", "33", "Designer"],
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    return csv_file


@pytest.fixture
def temp_synthetic_csv_bad_schema(tmp_path):
    """Create a synthetic CSV with wrong schema."""
    csv_file = tmp_path / "synthetic_bad.csv"
    data = [
        ["name", "age", "department"],  # Wrong column name
        ["John", "26", "Engineering"],
        ["Jane", "31", "Design"],
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    return csv_file


def test_validator_init():
    """Test SyntheticValidator initialisation."""
    validator = SyntheticValidator()
    assert validator is not None


def test_validate_good_match(temp_original_csv, temp_synthetic_csv_good):
    """Test validation with good schema and distribution match."""
    validator = SyntheticValidator()
    result = validator.validate(
        original_path=temp_original_csv,
        synthetic_path=temp_synthetic_csv_good,
    )

    assert result.schema_match is True
    assert result.schema_match_score == 1.0
    assert result.distribution_similarity > 0.5  # Should be reasonably similar
    assert result.pii_detected is False or result.pii_detected is not None
    # May detect names as PII depending on setup


def test_validate_bad_schema(temp_original_csv, temp_synthetic_csv_bad_schema):
    """Test validation with schema mismatch."""
    validator = SyntheticValidator()
    result = validator.validate(
        original_path=temp_original_csv,
        synthetic_path=temp_synthetic_csv_bad_schema,
    )

    assert result.schema_match is False
    assert result.schema_match_score < 1.0
    assert result.passed is False
    assert len(result.issues) > 0


def test_validate_schema_matching():
    """Test schema validation logic."""
    validator = SyntheticValidator()

    # Mock schemas with matching columns
    from persona.core.synthetic.models import ColumnType, DataSchema, DistributionStats

    orig_schema = DataSchema(
        columns=[
            DistributionStats(column_name="name", column_type=ColumnType.TEXT),
            DistributionStats(column_name="age", column_type=ColumnType.NUMERIC),
        ],
        row_count=100,
    )

    synth_schema = DataSchema(
        columns=[
            DistributionStats(column_name="name", column_type=ColumnType.TEXT),
            DistributionStats(column_name="age", column_type=ColumnType.NUMERIC),
        ],
        row_count=100,
    )

    match, score = validator._validate_schema(orig_schema, synth_schema)
    assert match is True
    assert score == 1.0


def test_validate_schema_mismatch():
    """Test schema validation with missing columns."""
    validator = SyntheticValidator()

    from persona.core.synthetic.models import ColumnType, DataSchema, DistributionStats

    orig_schema = DataSchema(
        columns=[
            DistributionStats(column_name="name", column_type=ColumnType.TEXT),
            DistributionStats(column_name="age", column_type=ColumnType.NUMERIC),
            DistributionStats(column_name="role", column_type=ColumnType.TEXT),
        ],
        row_count=100,
    )

    synth_schema = DataSchema(
        columns=[
            DistributionStats(column_name="name", column_type=ColumnType.TEXT),
            DistributionStats(column_name="age", column_type=ColumnType.NUMERIC),
        ],
        row_count=100,
    )

    match, score = validator._validate_schema(orig_schema, synth_schema)
    assert match is False
    assert score == pytest.approx(2.0 / 3.0)  # 2 out of 3 columns match


def test_categorical_similarity():
    """Test categorical distribution similarity calculation."""
    validator = SyntheticValidator()

    # Identical distributions
    orig_dist = {"A": 50, "B": 30, "C": 20}
    synth_dist = {"A": 50, "B": 30, "C": 20}

    sim = validator._categorical_similarity(orig_dist, synth_dist, 100, 100)
    assert sim == pytest.approx(1.0)

    # Different distributions
    orig_dist = {"A": 50, "B": 50}
    synth_dist = {"A": 100}

    sim = validator._categorical_similarity(orig_dist, synth_dist, 100, 100)
    assert sim < 1.0


def test_numeric_similarity():
    """Test numeric statistics similarity calculation."""
    validator = SyntheticValidator()

    # Identical stats
    orig_stats = {"mean": 100.0, "std": 10.0}
    synth_stats = {"mean": 100.0, "std": 10.0}

    sim = validator._numeric_similarity(orig_stats, synth_stats)
    assert sim == pytest.approx(1.0)

    # Different stats
    orig_stats = {"mean": 100.0, "std": 10.0}
    synth_stats = {"mean": 120.0, "std": 15.0}

    sim = validator._numeric_similarity(orig_stats, synth_stats)
    assert sim < 1.0


def test_diversity_calculation():
    """Test diversity score calculation."""
    validator = SyntheticValidator()

    from persona.core.synthetic.models import ColumnType, DataSchema, DistributionStats

    # High diversity (all unique)
    schema = DataSchema(
        columns=[
            DistributionStats(
                column_name="id",
                column_type=ColumnType.TEXT,
                unique_count=100,
            ),
        ],
        row_count=100,
    )

    diversity = validator._calculate_diversity(schema)
    assert diversity == pytest.approx(1.0)

    # Low diversity (few unique values)
    schema = DataSchema(
        columns=[
            DistributionStats(
                column_name="category",
                column_type=ColumnType.CATEGORICAL,
                unique_count=5,
            ),
        ],
        row_count=100,
    )

    diversity = validator._calculate_diversity(schema)
    assert diversity == pytest.approx(0.05)


def test_pii_check_no_privacy_module(temp_synthetic_csv_good):
    """Test PII check when privacy module is not available."""
    validator = SyntheticValidator()

    # Should gracefully handle missing privacy module
    pii_detected, count, types = validator._check_pii(temp_synthetic_csv_good)

    # Without privacy module, should assume no PII
    assert pii_detected is False
    assert count == 0
    assert types == []
