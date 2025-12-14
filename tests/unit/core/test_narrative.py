"""
Tests for narrative text output (F-036).
"""

import pytest

from persona.core.output.narrative import (
    FirstPersonNarrativeFormatter,
    NarrativeConfig,
    NarrativeFormatter,
    Perspective,
    ThirdPersonNarrativeFormatter,
)
from persona.core.output.registry import OutputSection, SectionConfig
from persona.core.generation.parser import Persona


@pytest.fixture
def sample_persona() -> Persona:
    """Create a sample persona for testing."""
    return Persona(
        id="persona-001",
        name="Sarah Chen",
        demographics={
            "age": "32",
            "role": "Marketing Manager",
            "location": "London",
            "experience": "8 years",
        },
        goals=[
            "Streamline campaign workflows",
            "Improve team collaboration",
            "Achieve work-life balance",
        ],
        pain_points=[
            "Too many manual processes",
            "Difficulty tracking campaign performance",
            "Constant context switching",
        ],
        behaviours=[
            "Checking analytics dashboards first thing in the morning",
            "Juggling multiple campaigns simultaneously",
            "Collaborating with cross-functional teams",
        ],
        quotes=[
            "I need tools that work the way I think.",
            "Every minute spent on admin is a minute not spent on strategy.",
            "If I can't see the big picture, I can't make good decisions.",
        ],
        additional={
            "motivations": ["Recognition", "Team success", "Professional growth"],
        },
    )


@pytest.fixture
def minimal_persona() -> Persona:
    """Create a minimal persona for testing."""
    return Persona(
        id="persona-002",
        name="Alex",
        demographics={},
        goals=["Get things done"],
        pain_points=["Complexity"],
    )


class TestPerspective:
    """Tests for Perspective enum."""

    def test_perspective_values(self):
        """Test perspective enum values."""
        assert Perspective.FIRST_PERSON.value == "first_person"
        assert Perspective.THIRD_PERSON.value == "third_person"


class TestNarrativeConfig:
    """Tests for NarrativeConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = NarrativeConfig()
        assert config.perspective == Perspective.THIRD_PERSON
        assert config.include_day_in_life is True
        assert config.include_what_drives is True
        assert config.include_challenges is True
        assert config.include_quotes is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = NarrativeConfig(
            perspective=Perspective.FIRST_PERSON,
            include_day_in_life=False,
            include_quotes=False,
        )
        assert config.perspective == Perspective.FIRST_PERSON
        assert config.include_day_in_life is False
        assert config.include_quotes is False


class TestNarrativeFormatter:
    """Tests for NarrativeFormatter."""

    def test_default_perspective_is_third_person(self):
        """Test default perspective is third person."""
        formatter = NarrativeFormatter()
        assert formatter._config.perspective == Perspective.THIRD_PERSON

    def test_extension_is_md(self):
        """Test file extension is .md."""
        formatter = NarrativeFormatter()
        assert formatter.extension() == ".md"

    def test_format_returns_string(self, sample_persona):
        """Test format returns a string."""
        formatter = NarrativeFormatter()
        result = formatter.format(sample_persona)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_includes_name(self, sample_persona):
        """Test format includes persona name."""
        formatter = NarrativeFormatter()
        result = formatter.format(sample_persona)
        assert "Sarah Chen" in result

    def test_third_person_uses_meet(self, sample_persona):
        """Test third person intro uses 'Meet'."""
        formatter = NarrativeFormatter(perspective=Perspective.THIRD_PERSON)
        result = formatter.format(sample_persona)
        assert "# Meet Sarah Chen" in result

    def test_first_person_uses_im(self, sample_persona):
        """Test first person intro uses 'I'm'."""
        formatter = NarrativeFormatter(perspective=Perspective.FIRST_PERSON)
        result = formatter.format(sample_persona)
        assert "# I'm Sarah Chen" in result

    def test_third_person_demographics(self, sample_persona):
        """Test third person demographics narrative."""
        formatter = NarrativeFormatter(perspective=Perspective.THIRD_PERSON)
        result = formatter.format(sample_persona)
        assert "Sarah Chen is 32" in result
        assert "Marketing Manager" in result

    def test_first_person_demographics(self, sample_persona):
        """Test first person demographics narrative."""
        formatter = NarrativeFormatter(perspective=Perspective.FIRST_PERSON)
        result = formatter.format(sample_persona)
        assert "I'm 32 years old" in result
        assert "work as a Marketing Manager" in result

    def test_day_in_life_section(self, sample_persona):
        """Test day in life section is included."""
        formatter = NarrativeFormatter()
        result = formatter.format(sample_persona)
        assert "A Day in" in result
        assert "typical day" in result

    def test_day_in_life_can_be_disabled(self, sample_persona):
        """Test day in life can be disabled via config."""
        config = NarrativeConfig(include_day_in_life=False)
        formatter = NarrativeFormatter(config=config)
        result = formatter.format(sample_persona)
        assert "A Day in" not in result

    def test_what_drives_section(self, sample_persona):
        """Test what drives section is included."""
        formatter = NarrativeFormatter()
        result = formatter.format(sample_persona)
        assert "What Drives" in result
        assert "core" in result.lower()

    def test_challenges_section(self, sample_persona):
        """Test challenges section is included."""
        formatter = NarrativeFormatter()
        result = formatter.format(sample_persona)
        assert "Challenges" in result
        assert "manual processes" in result.lower()

    def test_quotes_section(self, sample_persona):
        """Test quotes section is included."""
        formatter = NarrativeFormatter()
        result = formatter.format(sample_persona)
        assert "Own Words" in result
        assert '> "' in result

    def test_quotes_can_be_disabled(self, sample_persona):
        """Test quotes can be disabled via config."""
        config = NarrativeConfig(include_quotes=False)
        formatter = NarrativeFormatter(config=config)
        result = formatter.format(sample_persona)
        assert "Own Words" not in result

    def test_format_minimal_persona(self, minimal_persona):
        """Test formatting works with minimal persona."""
        formatter = NarrativeFormatter()
        result = formatter.format(minimal_persona)
        assert "Alex" in result
        assert "get things done" in result.lower()

    def test_format_multiple_separates_with_divider(self, sample_persona, minimal_persona):
        """Test format_multiple separates personas with divider."""
        formatter = NarrativeFormatter()
        result = formatter.format_multiple([sample_persona, minimal_persona])
        assert "Sarah Chen" in result
        assert "Alex" in result
        assert "---" in result

    def test_section_config_respected(self, sample_persona):
        """Test section config filters output."""
        config = SectionConfig.minimal()  # Only demographics, goals, pain_points
        formatter = NarrativeFormatter(sections=config)
        result = formatter.format(sample_persona)
        # Goals and pain points should be included
        assert "streamline" in result.lower() or "workflow" in result.lower()

    def test_format_with_override_sections(self, sample_persona):
        """Test format with section override."""
        formatter = NarrativeFormatter()
        # Use minimal sections as override
        override = SectionConfig.minimal()
        result = formatter.format(sample_persona, sections=override)
        assert isinstance(result, str)


class TestNarrativeFormatterHelpers:
    """Tests for NarrativeFormatter helper methods."""

    def test_format_list_as_prose_empty(self):
        """Test format_list_as_prose with empty list."""
        formatter = NarrativeFormatter()
        result = formatter._format_list_as_prose([])
        assert result == ""

    def test_format_list_as_prose_single_item(self):
        """Test format_list_as_prose with single item."""
        formatter = NarrativeFormatter()
        result = formatter._format_list_as_prose(["First item"])
        assert result == "first item"

    def test_format_list_as_prose_two_items(self):
        """Test format_list_as_prose with two items."""
        formatter = NarrativeFormatter()
        result = formatter._format_list_as_prose(["First", "Second"])
        assert result == "first and second"

    def test_format_list_as_prose_multiple_items(self):
        """Test format_list_as_prose with multiple items uses Oxford comma."""
        formatter = NarrativeFormatter()
        result = formatter._format_list_as_prose(["First", "Second", "Third"])
        assert result == "first, second, and third"

    def test_format_introduction_third_person(self, sample_persona):
        """Test introduction formatting in third person."""
        formatter = NarrativeFormatter(perspective=Perspective.THIRD_PERSON)
        result = formatter._format_introduction(sample_persona)
        assert "Meet Sarah Chen" in result

    def test_format_introduction_first_person(self, sample_persona):
        """Test introduction formatting in first person."""
        formatter = NarrativeFormatter(perspective=Perspective.FIRST_PERSON)
        result = formatter._format_introduction(sample_persona)
        assert "I'm Sarah Chen" in result


class TestFirstPersonNarrativeFormatter:
    """Tests for FirstPersonNarrativeFormatter."""

    def test_uses_first_person(self, sample_persona):
        """Test formatter uses first person perspective."""
        formatter = FirstPersonNarrativeFormatter()
        result = formatter.format(sample_persona)
        assert "I'm Sarah Chen" in result

    def test_extension(self):
        """Test file extension."""
        formatter = FirstPersonNarrativeFormatter()
        assert formatter.extension() == ".md"


class TestThirdPersonNarrativeFormatter:
    """Tests for ThirdPersonNarrativeFormatter."""

    def test_uses_third_person(self, sample_persona):
        """Test formatter uses third person perspective."""
        formatter = ThirdPersonNarrativeFormatter()
        result = formatter.format(sample_persona)
        assert "Meet Sarah Chen" in result

    def test_extension(self):
        """Test file extension."""
        formatter = ThirdPersonNarrativeFormatter()
        assert formatter.extension() == ".md"


class TestNarrativeFormatterEdgeCases:
    """Tests for edge cases in narrative formatting."""

    def test_empty_demographics(self):
        """Test formatting with empty demographics."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Goal"],
            pain_points=[],
        )
        formatter = NarrativeFormatter()
        result = formatter.format(persona)
        assert "Test User" in result

    def test_no_behaviours(self):
        """Test formatting without behaviours."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={"age": "30"},
            goals=["Goal"],
            pain_points=[],
            behaviours=[],
        )
        formatter = NarrativeFormatter()
        result = formatter.format(persona)
        # Day in life section should be skipped
        assert "typical day" not in result.lower()

    def test_no_quotes(self):
        """Test formatting without quotes."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Goal"],
            pain_points=[],
            quotes=[],
        )
        formatter = NarrativeFormatter()
        result = formatter.format(persona)
        # Quotes section should be skipped
        assert "Own Words" not in result

    def test_no_goals_no_motivations(self):
        """Test formatting without goals or motivations."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=[],
            pain_points=["Problem"],
        )
        formatter = NarrativeFormatter()
        result = formatter.format(persona)
        # What drives section should be minimal or skipped
        assert "Test User" in result

    def test_single_goal(self):
        """Test formatting with single goal."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Achieve greatness"],
            pain_points=[],
        )
        formatter = NarrativeFormatter()
        result = formatter.format(persona)
        assert "achieve greatness" in result.lower()

    def test_two_goals(self):
        """Test formatting with two goals."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Goal one", "Goal two"],
            pain_points=[],
        )
        formatter = NarrativeFormatter()
        result = formatter.format(persona)
        assert "goal one and goal two" in result.lower()

    def test_max_three_quotes_shown(self, sample_persona):
        """Test only maximum 3 quotes are shown."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Goal"],
            pain_points=[],
            quotes=["Quote 1", "Quote 2", "Quote 3", "Quote 4", "Quote 5"],
        )
        formatter = NarrativeFormatter()
        result = formatter.format(persona)
        assert "Quote 1" in result
        assert "Quote 2" in result
        assert "Quote 3" in result
        assert "Quote 4" not in result
        assert "Quote 5" not in result


class TestNarrativeFormatterRegistration:
    """Tests for narrative formatter registration."""

    def test_narrative_format_registered(self):
        """Test narrative format is registered in registry."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        assert registry.has("narrative")

    def test_narrative_format_info(self):
        """Test narrative format info."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        info = registry.get_info("narrative")
        assert info.name == "narrative"
        assert info.extension == ".md"
        assert info.supports_sections is True

    def test_get_narrative_formatter(self):
        """Test getting narrative formatter from registry."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        formatter = registry.get("narrative")
        assert formatter is not None
        assert hasattr(formatter, "format")
