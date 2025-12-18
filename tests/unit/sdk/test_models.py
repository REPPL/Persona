"""Tests for SDK Pydantic models."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from persona.sdk.models import (
    ComplexityLevel,
    DetailLevel,
    ExperimentConfig,
    ExperimentModel,
    GenerationResultModel,
    PersonaConfig,
    PersonaModel,
    TokenUsageModel,
)
from pydantic import ValidationError as PydanticValidationError


class TestComplexityLevel:
    """Tests for ComplexityLevel enum."""

    def test_enum_values(self):
        """Test enum value strings."""
        assert ComplexityLevel.SIMPLE.value == "simple"
        assert ComplexityLevel.MODERATE.value == "moderate"
        assert ComplexityLevel.COMPLEX.value == "complex"

    def test_string_conversion(self):
        """Test string to enum conversion."""
        assert ComplexityLevel("simple") == ComplexityLevel.SIMPLE
        assert ComplexityLevel("moderate") == ComplexityLevel.MODERATE
        assert ComplexityLevel("complex") == ComplexityLevel.COMPLEX


class TestDetailLevel:
    """Tests for DetailLevel enum."""

    def test_enum_values(self):
        """Test enum value strings."""
        assert DetailLevel.MINIMAL.value == "minimal"
        assert DetailLevel.STANDARD.value == "standard"
        assert DetailLevel.DETAILED.value == "detailed"


class TestPersonaConfig:
    """Tests for PersonaConfig model."""

    def test_default_values(self):
        """Test default configuration values."""
        config = PersonaConfig()
        assert config.count == 3
        assert config.complexity == "moderate"
        assert config.detail_level == "standard"
        assert config.include_reasoning is False
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.workflow == "default"

    def test_custom_values(self):
        """Test custom configuration values."""
        config = PersonaConfig(
            count=5,
            complexity=ComplexityLevel.COMPLEX,
            detail_level=DetailLevel.DETAILED,
            include_reasoning=True,
            temperature=0.9,
            max_tokens=8000,
            workflow="custom",
        )
        assert config.count == 5
        assert config.complexity == "complex"
        assert config.detail_level == "detailed"
        assert config.include_reasoning is True
        assert config.temperature == 0.9
        assert config.max_tokens == 8000
        assert config.workflow == "custom"

    def test_count_validation_min(self):
        """Test count minimum validation."""
        with pytest.raises(PydanticValidationError):
            PersonaConfig(count=0)

    def test_count_validation_max(self):
        """Test count maximum validation."""
        with pytest.raises(PydanticValidationError):
            PersonaConfig(count=21)

    def test_temperature_validation_min(self):
        """Test temperature minimum validation."""
        with pytest.raises(PydanticValidationError):
            PersonaConfig(temperature=-0.1)

    def test_temperature_validation_max(self):
        """Test temperature maximum validation."""
        with pytest.raises(PydanticValidationError):
            PersonaConfig(temperature=2.1)

    def test_max_tokens_validation_min(self):
        """Test max_tokens minimum validation."""
        with pytest.raises(PydanticValidationError):
            PersonaConfig(max_tokens=50)

    def test_string_complexity_accepted(self):
        """Test that string complexity values work."""
        config = PersonaConfig(complexity="simple")
        assert config.complexity == "simple"


class TestExperimentConfig:
    """Tests for ExperimentConfig model."""

    def test_required_name(self):
        """Test that name is required."""
        with pytest.raises(PydanticValidationError):
            ExperimentConfig()

    def test_default_values(self):
        """Test default values with required name."""
        config = ExperimentConfig(name="test-experiment")
        assert config.name == "test-experiment"
        assert config.description == ""
        assert config.provider == "anthropic"
        assert config.model is None
        assert config.workflow == "default"
        assert config.count == 3

    def test_custom_values(self):
        """Test custom values."""
        config = ExperimentConfig(
            name="my-experiment",
            description="Test description",
            provider="openai",
            model="gpt-4",
            workflow="custom",
            count=5,
        )
        assert config.name == "my-experiment"
        assert config.description == "Test description"
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.workflow == "custom"
        assert config.count == 5

    def test_name_validation_empty(self):
        """Test that empty name is rejected."""
        with pytest.raises(PydanticValidationError):
            ExperimentConfig(name="")

    def test_name_validation_whitespace(self):
        """Test that whitespace-only name is rejected."""
        with pytest.raises(PydanticValidationError):
            ExperimentConfig(name="   ")

    def test_name_stripped(self):
        """Test that name is stripped."""
        config = ExperimentConfig(name="  my-experiment  ")
        assert config.name == "my-experiment"


class TestPersonaModel:
    """Tests for PersonaModel."""

    def test_required_fields(self):
        """Test required fields."""
        with pytest.raises(PydanticValidationError):
            PersonaModel()

    def test_minimal_persona(self):
        """Test persona with minimal fields."""
        persona = PersonaModel(id="p-001", name="Test User")
        assert persona.id == "p-001"
        assert persona.name == "Test User"
        assert persona.title == ""
        assert persona.goals == []
        assert persona.pain_points == []
        assert persona.behaviours == []
        assert persona.quotes == []
        assert persona.demographics == {}
        assert persona.additional == {}

    def test_full_persona(self):
        """Test persona with all fields."""
        persona = PersonaModel(
            id="p-001",
            name="Sarah Chen",
            title="Senior Developer",
            goals=["Ship faster", "Learn new tech"],
            pain_points=["Slow builds", "Too many meetings"],
            behaviours=["Uses keyboard shortcuts", "Reviews code daily"],
            quotes=["I wish the build was faster"],
            demographics={"age": "32", "role": "developer"},
            additional={"custom_field": "value"},
        )
        assert persona.name == "Sarah Chen"
        assert persona.title == "Senior Developer"
        assert len(persona.goals) == 2
        assert len(persona.pain_points) == 2
        assert persona.demographics["age"] == "32"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        persona = PersonaModel(
            id="p-001",
            name="Test",
            goals=["Goal 1"],
        )
        d = persona.to_dict()
        assert d["id"] == "p-001"
        assert d["name"] == "Test"
        assert d["goals"] == ["Goal 1"]

    def test_to_json(self):
        """Test conversion to JSON."""
        persona = PersonaModel(id="p-001", name="Test")
        json_str = persona.to_json()
        parsed = json.loads(json_str)
        assert parsed["id"] == "p-001"
        assert parsed["name"] == "Test"


class TestTokenUsageModel:
    """Tests for TokenUsageModel."""

    def test_default_values(self):
        """Test default zero values."""
        usage = TokenUsageModel()
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0
        assert usage.total_tokens == 0

    def test_custom_values(self):
        """Test custom values."""
        usage = TokenUsageModel(input_tokens=100, output_tokens=50)
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50

    def test_total_computed(self):
        """Test that total is computed from input/output."""
        usage = TokenUsageModel(input_tokens=100, output_tokens=50)
        assert usage.total_tokens == 150

    def test_explicit_total(self):
        """Test explicit total value."""
        usage = TokenUsageModel(input_tokens=100, output_tokens=50, total_tokens=200)
        # When total_tokens is explicitly set and non-zero, it should be preserved
        # But our validator sets it if zero, so explicit non-zero should work
        assert usage.total_tokens == 200

    def test_negative_validation(self):
        """Test that negative values are rejected."""
        with pytest.raises(PydanticValidationError):
            TokenUsageModel(input_tokens=-1)


class TestGenerationResultModel:
    """Tests for GenerationResultModel."""

    def test_default_values(self):
        """Test default values."""
        result = GenerationResultModel()
        assert result.personas == []
        assert result.reasoning is None
        assert result.model == ""
        assert result.provider == ""
        assert result.source_files == []
        assert isinstance(result.generated_at, datetime)

    def test_with_personas(self):
        """Test result with personas."""
        personas = [
            PersonaModel(id="p-001", name="Alice"),
            PersonaModel(id="p-002", name="Bob"),
        ]
        result = GenerationResultModel(personas=personas)
        assert len(result.personas) == 2
        assert result.personas[0].name == "Alice"
        assert result.personas[1].name == "Bob"

    def test_with_token_usage(self):
        """Test result with token usage."""
        result = GenerationResultModel(
            token_usage=TokenUsageModel(input_tokens=1000, output_tokens=500)
        )
        assert result.token_usage.input_tokens == 1000
        assert result.token_usage.output_tokens == 500
        assert result.token_usage.total_tokens == 1500

    def test_to_json_creates_file(self):
        """Test to_json creates file."""
        result = GenerationResultModel(
            personas=[PersonaModel(id="p-001", name="Test")],
            model="test-model",
            provider="test-provider",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = result.to_json(tmpdir)
            assert path.exists()
            assert path.name == "generation_result.json"

            content = json.loads(path.read_text())
            assert len(content["personas"]) == 1
            assert content["model"] == "test-model"

    def test_to_markdown_creates_files(self):
        """Test to_markdown creates files."""
        result = GenerationResultModel(
            personas=[
                PersonaModel(
                    id="p-001",
                    name="Alice",
                    title="Developer",
                    goals=["Ship faster"],
                    pain_points=["Slow builds"],
                ),
                PersonaModel(id="p-002", name="Bob"),
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = result.to_markdown(tmpdir)
            assert len(paths) == 2

            alice_path = Path(tmpdir) / "p-001.md"
            assert alice_path.exists()
            content = alice_path.read_text()
            assert "# Alice" in content
            assert "Developer" in content
            assert "Ship faster" in content


class TestExperimentModel:
    """Tests for ExperimentModel."""

    def test_required_fields(self):
        """Test required fields."""
        with pytest.raises(PydanticValidationError):
            ExperimentModel()

    def test_minimal_experiment(self):
        """Test minimal experiment."""
        exp = ExperimentModel(name="test", path="/path/to/exp")
        assert exp.name == "test"
        assert exp.path == "/path/to/exp"
        assert exp.description == ""
        assert exp.provider == "anthropic"
        assert exp.model is None
        assert exp.run_count == 0

    def test_full_experiment(self):
        """Test full experiment."""
        exp = ExperimentModel(
            name="my-experiment",
            path="/experiments/my-experiment",
            description="Test experiment",
            provider="openai",
            model="gpt-4",
            workflow="custom",
            run_count=5,
        )
        assert exp.name == "my-experiment"
        assert exp.description == "Test experiment"
        assert exp.run_count == 5

    def test_data_dir_property(self):
        """Test data_dir property."""
        exp = ExperimentModel(name="test", path="/experiments/test")
        assert exp.data_dir == Path("/experiments/test/data")

    def test_outputs_dir_property(self):
        """Test outputs_dir property."""
        exp = ExperimentModel(name="test", path="/experiments/test")
        assert exp.outputs_dir == Path("/experiments/test/outputs")

    def test_run_count_validation(self):
        """Test run_count cannot be negative."""
        with pytest.raises(PydanticValidationError):
            ExperimentModel(name="test", path="/path", run_count=-1)


class TestModelInteroperability:
    """Tests for model conversion and interoperability."""

    def test_persona_config_to_core(self):
        """Test PersonaConfig can be used to create core config."""
        config = PersonaConfig(
            count=5,
            complexity="complex",
            temperature=0.9,
        )
        # These values should be usable with core GenerationConfig
        assert config.count == 5
        assert config.complexity == "complex"
        assert config.temperature == 0.9

    def test_json_round_trip(self):
        """Test JSON serialisation round trip."""
        persona = PersonaModel(
            id="p-001",
            name="Test",
            goals=["Goal 1", "Goal 2"],
            demographics={"age": "30"},
        )

        json_str = persona.to_json()
        parsed = json.loads(json_str)
        restored = PersonaModel(**parsed)

        assert restored.id == persona.id
        assert restored.name == persona.name
        assert restored.goals == persona.goals
        assert restored.demographics == persona.demographics
