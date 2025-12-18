"""
Unit tests for DataAnalyser.
"""

import csv
import json

import pytest
import yaml
from persona.core.synthetic.analyser import DataAnalyser
from persona.core.synthetic.models import ColumnType


@pytest.fixture
def temp_csv(tmp_path):
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test.csv"
    data = [
        ["name", "age", "role", "active"],
        ["Alice", "25", "Engineer", "true"],
        ["Bob", "30", "Designer", "true"],
        ["Charlie", "35", "Manager", "false"],
        ["Diana", "28", "Engineer", "true"],
        ["Eve", "32", "Designer", "true"],
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    return csv_file


@pytest.fixture
def temp_json(tmp_path):
    """Create a temporary JSON file for testing."""
    json_file = tmp_path / "test.json"
    data = [
        {"name": "Alice", "age": 25, "role": "Engineer", "active": True},
        {"name": "Bob", "age": 30, "role": "Designer", "active": True},
        {"name": "Charlie", "age": 35, "role": "Manager", "active": False},
        {"name": "Diana", "age": 28, "role": "Engineer", "active": True},
        {"name": "Eve", "age": 32, "role": "Designer", "active": True},
    ]

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    return json_file


@pytest.fixture
def temp_yaml(tmp_path):
    """Create a temporary YAML file for testing."""
    yaml_file = tmp_path / "test.yaml"
    data = [
        {"name": "Alice", "age": 25, "role": "Engineer", "active": True},
        {"name": "Bob", "age": 30, "role": "Designer", "active": True},
        {"name": "Charlie", "age": 35, "role": "Manager", "active": False},
    ]

    with open(yaml_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

    return yaml_file


def test_analyser_init():
    """Test DataAnalyser initialisation."""
    analyser = DataAnalyser()
    assert analyser is not None


def test_analyse_csv_file(temp_csv):
    """Test analysing CSV file."""
    analyser = DataAnalyser()
    schema = analyser.analyse_file(temp_csv)

    assert schema.row_count == 5
    assert schema.format == "csv"
    assert len(schema.columns) == 4

    # Check column names
    col_names = schema.column_names()
    assert "name" in col_names
    assert "age" in col_names
    assert "role" in col_names
    assert "active" in col_names


def test_analyse_json_file(temp_json):
    """Test analysing JSON file."""
    analyser = DataAnalyser()
    schema = analyser.analyse_file(temp_json)

    assert schema.row_count == 5
    assert schema.format == "json"
    assert len(schema.columns) == 4


def test_analyse_yaml_file(temp_yaml):
    """Test analysing YAML file."""
    analyser = DataAnalyser()
    schema = analyser.analyse_file(temp_yaml)

    assert schema.row_count == 3
    assert schema.format == "yaml"
    assert len(schema.columns) == 4


def test_analyse_nonexistent_file():
    """Test analysing non-existent file raises error."""
    analyser = DataAnalyser()

    with pytest.raises(FileNotFoundError):
        analyser.analyse_file("nonexistent.csv")


def test_analyse_unsupported_format(tmp_path):
    """Test analysing unsupported format raises error."""
    analyser = DataAnalyser()
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("some text")

    with pytest.raises(ValueError, match="Unsupported file format"):
        analyser.analyse_file(txt_file)


def test_column_type_inference(temp_csv):
    """Test column type inference."""
    analyser = DataAnalyser()
    schema = analyser.analyse_file(temp_csv)

    # Check inferred types
    name_col = schema.get_column("name")
    assert name_col is not None
    # Name has high cardinality, should be TEXT or CATEGORICAL
    assert name_col.column_type in [ColumnType.TEXT, ColumnType.CATEGORICAL]

    age_col = schema.get_column("age")
    assert age_col is not None
    # Age is numeric (even though stored as string in CSV)
    assert age_col.column_type == ColumnType.NUMERIC

    role_col = schema.get_column("role")
    assert role_col is not None
    # Role has low cardinality, could be CATEGORICAL or TEXT depending on threshold
    assert role_col.column_type in [ColumnType.CATEGORICAL, ColumnType.TEXT]

    active_col = schema.get_column("active")
    assert active_col is not None
    # Active is boolean
    assert active_col.column_type == ColumnType.BOOLEAN


def test_categorical_distribution(temp_csv):
    """Test categorical distribution calculation."""
    analyser = DataAnalyser()
    schema = analyser.analyse_file(temp_csv)

    role_col = schema.get_column("role")
    assert role_col is not None
    assert role_col.categorical_distribution is not None

    # Check distribution
    dist = role_col.categorical_distribution
    assert "Engineer" in dist
    assert "Designer" in dist
    assert "Manager" in dist
    assert dist["Engineer"] == 2  # Alice and Diana
    assert dist["Designer"] == 2  # Bob and Eve
    assert dist["Manager"] == 1  # Charlie


def test_numeric_stats(temp_csv):
    """Test numeric statistics calculation."""
    analyser = DataAnalyser()
    schema = analyser.analyse_file(temp_csv)

    age_col = schema.get_column("age")
    assert age_col is not None
    assert age_col.numeric_stats is not None

    stats = age_col.numeric_stats
    assert "min" in stats
    assert "max" in stats
    assert "mean" in stats
    assert "std" in stats

    # Check values (25, 30, 35, 28, 32)
    assert stats["min"] == 25.0
    assert stats["max"] == 35.0
    assert stats["mean"] == 30.0  # (25+30+35+28+32)/5 = 30


def test_unique_count(temp_csv):
    """Test unique value counting."""
    analyser = DataAnalyser()
    schema = analyser.analyse_file(temp_csv)

    name_col = schema.get_column("name")
    assert name_col.unique_count == 5  # All unique

    role_col = schema.get_column("role")
    assert role_col.unique_count == 3  # Engineer, Designer, Manager

    active_col = schema.get_column("active")
    assert active_col.unique_count == 2  # true, false


def test_sample_values(temp_csv):
    """Test sample values extraction."""
    analyser = DataAnalyser()
    schema = analyser.analyse_file(temp_csv)

    age_col = schema.get_column("age")
    assert age_col is not None
    assert len(age_col.sample_values) > 0
    assert len(age_col.sample_values) <= 5  # Max 5 samples


def test_analyse_data_direct():
    """Test analysing data directly (not from file)."""
    analyser = DataAnalyser()
    data = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
        {"name": "Charlie", "age": 35},
    ]

    schema = analyser.analyse_data(data, format_type="json")

    assert schema.row_count == 3
    assert schema.format == "json"
    assert len(schema.columns) == 2


def test_analyse_empty_data():
    """Test analysing empty data raises error."""
    analyser = DataAnalyser()

    with pytest.raises(ValueError, match="No data to analyse"):
        analyser.analyse_data([], format_type="csv")
