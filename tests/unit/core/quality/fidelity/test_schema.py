"""
Tests for schema validator.

Tests SchemaValidator for structural fidelity checks.
"""


from persona.core.generation.parser import Persona
from persona.core.quality.fidelity.models import PromptConstraints, Severity
from persona.core.quality.fidelity.schema import SchemaValidator


class TestSchemaValidator:
    """Test SchemaValidator."""

    def test_valid_persona(self):
        """Test validation of valid persona."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 30},
            goals=["Goal 1", "Goal 2"],
        )

        constraints = PromptConstraints(
            required_fields=["name", "goals"],
            field_types={"goals": "list"},
        )

        validator = SchemaValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_missing_required_field(self):
        """Test detection of missing required field."""
        persona = Persona(id="p1", name="Test User")

        constraints = PromptConstraints(required_fields=["name", "age", "goals"])

        validator = SchemaValidator()
        score, violations = validator.validate(persona, constraints)

        assert score < 1.0
        assert len(violations) > 0
        assert any(v.field == "age" for v in violations)
        assert any(v.severity == Severity.CRITICAL for v in violations)

    def test_empty_required_field(self):
        """Test detection of empty required field."""
        persona = Persona(id="p1", name="", goals=[])

        constraints = PromptConstraints(required_fields=["name", "goals"])

        validator = SchemaValidator()
        score, violations = validator.validate(persona, constraints)

        assert len(violations) > 0
        assert any(v.field == "name" for v in violations)
        assert any(v.severity == Severity.HIGH for v in violations)

    def test_wrong_field_type(self):
        """Test detection of wrong field type."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": "thirty"},  # Should be int
            goals=["Goal"],
        )

        constraints = PromptConstraints(
            required_fields=["name"],
            field_types={"demographics.age": "integer"},
        )

        validator = SchemaValidator()
        score, violations = validator.validate(persona, constraints)

        assert len(violations) > 0
        assert any("age" in str(v.description) for v in violations)

    def test_nested_field_access(self):
        """Test accessing nested fields like demographics.age."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 30, "occupation": "Developer"},
        )

        constraints = PromptConstraints(
            required_fields=["demographics.age"],
            field_types={"demographics.age": "integer"},
        )

        validator = SchemaValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_type_checking_variations(self):
        """Test various type checking scenarios."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 30, "active": True},
            goals=["Goal 1"],
        )

        constraints = PromptConstraints(
            field_types={
                "name": "string",
                "demographics.age": "integer",
                "demographics.active": "boolean",
                "goals": "list",
            }
        )

        validator = SchemaValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_no_constraints(self):
        """Test validation with no constraints."""
        persona = Persona(id="p1", name="Test User")
        constraints = PromptConstraints()

        validator = SchemaValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_type_aliases(self):
        """Test type alias recognition (e.g., 'str' vs 'string')."""
        persona = Persona(
            id="p1",
            name="Test",
            demographics={"age": 30},
            goals=["Goal"],
        )

        constraints = PromptConstraints(
            field_types={
                "name": "str",  # Alias for string
                "demographics.age": "int",  # Alias for integer
                "goals": "array",  # Alias for list
            }
        )

        validator = SchemaValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0
