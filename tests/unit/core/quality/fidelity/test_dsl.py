"""
Tests for DSL parser.

Tests ConstraintParser for YAML constraint file parsing.
"""

import tempfile
from pathlib import Path

import pytest
import yaml
from persona.core.quality.fidelity.dsl import ConstraintParser
from persona.core.quality.fidelity.models import PromptConstraints


class TestConstraintParser:
    """Test ConstraintParser."""

    def test_parse_simple_yaml(self):
        """Test parsing simple YAML constraints."""
        yaml_content = """
name: Test Constraints
constraints:
  structure:
    required_fields:
      - name
      - age
  limits:
    age_range: [25, 45]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            parser = ConstraintParser()
            constraints = parser.parse_file(temp_path)

            assert "name" in constraints.required_fields
            assert "age" in constraints.required_fields
            assert constraints.age_range == (25, 45)
        finally:
            Path(temp_path).unlink()

    def test_parse_full_yaml(self):
        """Test parsing comprehensive YAML constraints."""
        yaml_content = """
name: Full Constraints
constraints:
  structure:
    required_fields:
      - name
      - age
      - goals
    field_types:
      age: integer
      goals: list

  content:
    occupation_keywords:
      - developer
      - engineer
    goal_themes:
      - productivity
      - learning

  limits:
    age_range: [25, 55]
    goal_count: [3, 6]
    pain_point_count: [2, 5]

  style:
    tone: professional
    detail_level: detailed
    custom_rules:
      - Use technical terminology
      - Be concise
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            parser = ConstraintParser()
            constraints = parser.parse_file(temp_path)

            assert constraints.required_fields == ["name", "age", "goals"]
            assert constraints.field_types == {"age": "integer", "goals": "list"}
            assert constraints.occupation_keywords == ["developer", "engineer"]
            assert constraints.goal_themes == ["productivity", "learning"]
            assert constraints.age_range == (25, 55)
            assert constraints.goal_count == (3, 6)
            assert constraints.style == "professional"
            assert constraints.complexity == "detailed"
            assert len(constraints.custom_rules) == 2
        finally:
            Path(temp_path).unlink()

    def test_parse_range_formats(self):
        """Test parsing different range formats."""
        yaml_content = """
name: Range Tests
constraints:
  limits:
    age_range: [25, 45]
    goal_count:
      min: 3
      max: 5
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            parser = ConstraintParser()
            constraints = parser.parse_file(temp_path)

            assert constraints.age_range == (25, 45)
            assert constraints.goal_count == (3, 5)
        finally:
            Path(temp_path).unlink()

    def test_parse_dict(self):
        """Test parsing from dictionary."""
        data = {
            "name": "Test",
            "constraints": {
                "structure": {"required_fields": ["name", "age"]},
                "limits": {"age_range": [20, 30]},
            },
        }

        parser = ConstraintParser()
        constraints = parser.parse_dict(data)

        assert constraints.required_fields == ["name", "age"]
        assert constraints.age_range == (20, 30)

    def test_parse_file_not_found(self):
        """Test handling of non-existent file."""
        parser = ConstraintParser()

        with pytest.raises(FileNotFoundError):
            parser.parse_file("nonexistent.yaml")

    def test_invalid_yaml(self):
        """Test handling of invalid YAML."""
        yaml_content = "not: valid: yaml::"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            parser = ConstraintParser()
            with pytest.raises(Exception):  # YAML parsing error
                parser.parse_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_to_yaml(self):
        """Test converting constraints to YAML."""
        constraints = PromptConstraints(
            required_fields=["name", "age"],
            age_range=(25, 45),
            goal_count=(3, 5),
            style="professional",
        )

        parser = ConstraintParser()
        yaml_str = parser.to_yaml(constraints)

        # Verify it's valid YAML
        data = yaml.safe_load(yaml_str)
        assert "constraints" in data
        assert data["constraints"]["structure"]["required_fields"] == ["name", "age"]
        assert data["constraints"]["limits"]["age_range"] == [25, 45]

    def test_roundtrip(self):
        """Test parsing and converting back to YAML."""
        original_constraints = PromptConstraints(
            required_fields=["name", "age"],
            age_range=(25, 45),
            occupation_keywords=["developer"],
        )

        parser = ConstraintParser()

        # Convert to YAML
        yaml_str = parser.to_yaml(original_constraints)

        # Parse back
        data = yaml.safe_load(yaml_str)
        parsed_constraints = parser.parse_dict(data)

        # Verify roundtrip
        assert (
            parsed_constraints.required_fields == original_constraints.required_fields
        )
        assert parsed_constraints.age_range == original_constraints.age_range
        assert (
            parsed_constraints.occupation_keywords
            == original_constraints.occupation_keywords
        )
