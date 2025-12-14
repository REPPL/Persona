"""
Tests for persona generation pipeline (F-004).
"""

import pytest
from pathlib import Path

from persona.core.generation import GenerationPipeline, PersonaParser, Persona
from persona.core.generation.pipeline import GenerationConfig, GenerationResult
from persona.core.generation.parser import ParseResult


class TestPersona:
    """Tests for Persona dataclass."""

    def test_create_persona(self):
        """Test creating a persona."""
        persona = Persona(
            id="persona-001",
            name="Alice",
            demographics={"age_range": "25-34"},
            goals=["Goal 1"],
            pain_points=["Pain 1"],
        )

        assert persona.id == "persona-001"
        assert persona.name == "Alice"
        assert persona.goals == ["Goal 1"]

    def test_from_dict(self):
        """Test creating persona from dictionary."""
        data = {
            "id": "p001",
            "name": "Bob",
            "demographics": {"occupation": "Developer"},
            "goals": ["Build things"],
            "pain_points": ["Bugs"],
            "behaviours": ["Codes daily"],
            "quotes": ["It works on my machine"],
        }

        persona = Persona.from_dict(data)

        assert persona.id == "p001"
        assert persona.name == "Bob"
        assert persona.demographics["occupation"] == "Developer"
        assert "Build things" in persona.goals

    def test_from_dict_alternate_fields(self):
        """Test handling of alternate field names."""
        data = {
            "id": "p001",
            "name": "Carol",
            "painPoints": ["Issue 1"],  # camelCase
            "behaviors": ["Action 1"],  # American spelling
        }

        persona = Persona.from_dict(data)

        assert "Issue 1" in persona.pain_points
        assert "Action 1" in persona.behaviours

    def test_from_dict_additional_fields(self):
        """Test handling of additional unknown fields."""
        data = {
            "id": "p001",
            "name": "Dave",
            "custom_field": "custom_value",
            "another_field": 123,
        }

        persona = Persona.from_dict(data)

        assert "custom_field" in persona.additional
        assert persona.additional["custom_field"] == "custom_value"

    def test_to_dict(self):
        """Test converting persona to dictionary."""
        persona = Persona(
            id="p001",
            name="Eve",
            goals=["Goal 1"],
            additional={"extra": "value"},
        )

        data = persona.to_dict()

        assert data["id"] == "p001"
        assert data["name"] == "Eve"
        assert data["goals"] == ["Goal 1"]
        assert data["extra"] == "value"


class TestPersonaParser:
    """Tests for PersonaParser class."""

    def test_parse_simple_json(self):
        """Test parsing simple JSON response."""
        response = '''
        {
            "personas": [
                {
                    "id": "persona-001",
                    "name": "Test User",
                    "goals": ["Goal 1"]
                }
            ]
        }
        '''

        parser = PersonaParser()
        result = parser.parse(response)

        assert len(result.personas) == 1
        assert result.personas[0].name == "Test User"

    def test_parse_with_output_tags(self):
        """Test parsing response with output tags."""
        response = '''
        Here is my analysis.

        <output>
        {
            "personas": [
                {"id": "p1", "name": "Alice", "goals": ["Learn"]}
            ]
        }
        </output>
        '''

        parser = PersonaParser()
        result = parser.parse(response)

        assert len(result.personas) == 1
        assert result.personas[0].name == "Alice"

    def test_parse_with_reasoning(self):
        """Test parsing response with reasoning tags."""
        response = '''
        <reasoning>
        I analyzed the data and found patterns.
        </reasoning>

        <output>
        {"personas": [{"id": "p1", "name": "Bob", "goals": []}]}
        </output>
        '''

        parser = PersonaParser()
        result = parser.parse(response)

        assert result.reasoning is not None
        assert "patterns" in result.reasoning
        assert len(result.personas) == 1

    def test_parse_json_in_code_block(self):
        """Test parsing JSON in code block."""
        response = '''
        Here are the personas:

        ```json
        {
            "personas": [
                {"id": "p1", "name": "Carol", "goals": ["Succeed"]}
            ]
        }
        ```
        '''

        parser = PersonaParser()
        result = parser.parse(response)

        assert len(result.personas) == 1
        assert result.personas[0].name == "Carol"

    def test_parse_array_of_personas(self):
        """Test parsing array of personas (not wrapped in object)."""
        response = '''
        [
            {"id": "p1", "name": "Dave", "goals": []},
            {"id": "p2", "name": "Eve", "goals": []}
        ]
        '''

        parser = PersonaParser()
        result = parser.parse(response)

        assert len(result.personas) == 2
        assert result.personas[0].name == "Dave"
        assert result.personas[1].name == "Eve"

    def test_parse_empty_response(self):
        """Test parsing empty response."""
        parser = PersonaParser()
        result = parser.parse("")

        assert len(result.personas) == 0

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON gracefully."""
        response = "This is not JSON at all"

        parser = PersonaParser()
        result = parser.parse(response)

        assert len(result.personas) == 0


class TestGenerationConfig:
    """Tests for GenerationConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = GenerationConfig(data_path="./data")

        assert config.count == 3
        assert config.provider == "anthropic"
        assert config.workflow == "default"
        assert config.complexity == "moderate"
        assert config.detail_level == "standard"

    def test_custom_values(self):
        """Test custom configuration values."""
        config = GenerationConfig(
            data_path="./interviews",
            count=5,
            provider="openai",
            model="gpt-4o",
            complexity="complex",
        )

        assert config.count == 5
        assert config.provider == "openai"
        assert config.model == "gpt-4o"


class TestGenerationResult:
    """Tests for GenerationResult dataclass."""

    def test_create_result(self):
        """Test creating a generation result."""
        personas = [Persona(id="p1", name="Test")]
        result = GenerationResult(
            personas=personas,
            input_tokens=100,
            output_tokens=200,
            model="test-model",
            provider="test-provider",
        )

        assert len(result.personas) == 1
        assert result.input_tokens == 100
        assert result.output_tokens == 200


class TestGenerationPipeline:
    """Tests for GenerationPipeline class."""

    def test_create_pipeline(self):
        """Test creating a pipeline."""
        pipeline = GenerationPipeline()
        assert pipeline is not None

    def test_progress_callback(self):
        """Test progress callback."""
        messages = []

        pipeline = GenerationPipeline()
        pipeline.set_progress_callback(lambda msg: messages.append(msg))
        pipeline._progress("Test message")

        assert "Test message" in messages

    def test_load_workflow_builtin(self):
        """Test loading built-in workflow."""
        pipeline = GenerationPipeline()
        workflow = pipeline._load_workflow("default")

        assert workflow is not None
        assert workflow.name == "default"

    def test_load_workflow_fallback(self):
        """Test fallback to default workflow."""
        pipeline = GenerationPipeline()
        workflow = pipeline._load_workflow("nonexistent")

        assert workflow is not None
        assert workflow.name == "default"
