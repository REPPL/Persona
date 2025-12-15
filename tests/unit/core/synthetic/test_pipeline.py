"""
Unit tests for SyntheticPipeline.
"""

import csv
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from persona.core.synthetic.pipeline import SyntheticPipeline


@pytest.fixture
def temp_csv_input(tmp_path):
    """Create a temporary input CSV file."""
    csv_file = tmp_path / "input.csv"
    data = [
        ["name", "age", "role"],
        ["Alice", "25", "Engineer"],
        ["Bob", "30", "Designer"],
        ["Charlie", "35", "Manager"],
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    return csv_file


@pytest.fixture
def mock_provider():
    """Create a mock LLM provider."""
    mock = MagicMock()
    mock.default_model = "test-model"

    # Mock response
    mock_response = MagicMock()
    mock_response.content = json.dumps([
        {"name": "John", "age": "26", "role": "Engineer"},
        {"name": "Jane", "age": "31", "role": "Designer"},
        {"name": "Jack", "age": "34", "role": "Manager"},
    ])
    mock.generate.return_value = mock_response

    return mock


def test_pipeline_init():
    """Test SyntheticPipeline initialisation."""
    with patch("persona.core.synthetic.pipeline.ProviderFactory.create") as mock_factory:
        mock_provider = MagicMock()
        mock_provider.default_model = "test-model"
        mock_factory.return_value = mock_provider

        pipeline = SyntheticPipeline(provider="ollama")

        assert pipeline.provider_name == "ollama"
        assert pipeline.model_name == "test-model"
        mock_factory.assert_called_once_with("ollama")


def test_pipeline_init_with_model():
    """Test SyntheticPipeline with custom model."""
    with patch("persona.core.synthetic.pipeline.ProviderFactory.create") as mock_factory:
        mock_provider = MagicMock()
        mock_provider.default_model = "default-model"
        mock_factory.return_value = mock_provider

        pipeline = SyntheticPipeline(provider="ollama", model="custom-model")

        assert pipeline.model_name == "custom-model"


def test_synthesise_basic(temp_csv_input, tmp_path, mock_provider):
    """Test basic synthetic data generation."""
    output_path = tmp_path / "output.csv"

    with patch("persona.core.synthetic.pipeline.ProviderFactory.create") as mock_factory:
        mock_factory.return_value = mock_provider

        pipeline = SyntheticPipeline(provider="ollama")

        # Mock validator to skip validation
        with patch.object(pipeline, "validator") as mock_validator:
            mock_validator.validate.return_value = None

            result = pipeline.synthesise(
                input_path=temp_csv_input,
                output_path=output_path,
                count=3,
                validate=False,
            )

    assert result is not None
    assert result.input_path == temp_csv_input
    assert result.output_path == output_path
    assert result.row_count > 0
    assert result.model == "test-model"
    assert result.provider == "ollama"
    assert result.generation_time > 0

    # Check output file exists
    assert output_path.exists()


def test_build_generation_prompt():
    """Test prompt generation."""
    with patch("persona.core.synthetic.pipeline.ProviderFactory.create") as mock_factory:
        mock_provider = MagicMock()
        mock_provider.default_model = "test-model"
        mock_factory.return_value = mock_provider

        pipeline = SyntheticPipeline(provider="ollama")

        from persona.core.synthetic.models import (
            ColumnType,
            DataSchema,
            DistributionStats,
        )

        schema = DataSchema(
            columns=[
                DistributionStats(
                    column_name="name",
                    column_type=ColumnType.TEXT,
                    unique_count=10,
                    sample_values=["Alice", "Bob"],
                ),
                DistributionStats(
                    column_name="age",
                    column_type=ColumnType.NUMERIC,
                    unique_count=5,
                    numeric_stats={
                        "min": 25.0,
                        "max": 35.0,
                        "mean": 30.0,
                        "std": 3.5,
                    },
                ),
            ],
            row_count=10,
        )

        prompt = pipeline._build_generation_prompt(
            schema=schema,
            count=5,
            preserve_distribution=True,
        )

        assert "Generate synthetic data" in prompt
        assert "name" in prompt
        assert "age" in prompt
        assert "CRITICAL REQUIREMENTS" in prompt
        assert "PII" in prompt


def test_parse_llm_response():
    """Test parsing LLM responses."""
    with patch("persona.core.synthetic.pipeline.ProviderFactory.create") as mock_factory:
        mock_provider = MagicMock()
        mock_provider.default_model = "test-model"
        mock_factory.return_value = mock_provider

        pipeline = SyntheticPipeline(provider="ollama")

        from persona.core.synthetic.models import (
            ColumnType,
            DataSchema,
            DistributionStats,
        )

        schema = DataSchema(
            columns=[
                DistributionStats(column_name="name", column_type=ColumnType.TEXT),
                DistributionStats(column_name="age", column_type=ColumnType.NUMERIC),
            ],
            row_count=2,
        )

        # Test plain JSON
        response = '[{"name": "John", "age": 25}, {"name": "Jane", "age": 30}]'
        records = pipeline._parse_llm_response(response, schema)

        assert len(records) == 2
        assert records[0]["name"] == "John"
        assert records[1]["name"] == "Jane"

        # Test JSON with markdown code blocks
        response = '```json\n[{"name": "John", "age": 25}]\n```'
        records = pipeline._parse_llm_response(response, schema)

        assert len(records) == 1
        assert records[0]["name"] == "John"


def test_save_data_csv(tmp_path):
    """Test saving data as CSV."""
    with patch("persona.core.synthetic.pipeline.ProviderFactory.create") as mock_factory:
        mock_provider = MagicMock()
        mock_provider.default_model = "test-model"
        mock_factory.return_value = mock_provider

        pipeline = SyntheticPipeline(provider="ollama")

        data = [
            {"name": "John", "age": 25},
            {"name": "Jane", "age": 30},
        ]

        output_path = tmp_path / "output.csv"
        pipeline._save_data(data, output_path, "csv")

        assert output_path.exists()

        # Read and verify
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["name"] == "John"
        assert rows[1]["age"] == "30"


def test_save_data_json(tmp_path):
    """Test saving data as JSON."""
    with patch("persona.core.synthetic.pipeline.ProviderFactory.create") as mock_factory:
        mock_provider = MagicMock()
        mock_provider.default_model = "test-model"
        mock_factory.return_value = mock_provider

        pipeline = SyntheticPipeline(provider="ollama")

        data = [
            {"name": "John", "age": 25},
            {"name": "Jane", "age": 30},
        ]

        output_path = tmp_path / "output.json"
        pipeline._save_data(data, output_path, "json")

        assert output_path.exists()

        # Read and verify
        with open(output_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert len(loaded_data) == 2
        assert loaded_data[0]["name"] == "John"
