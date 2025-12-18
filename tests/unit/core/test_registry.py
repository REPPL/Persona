"""
Tests for formatter registry (F-039).
"""

import pytest
from persona.core.generation.parser import Persona
from persona.core.output.registry import (
    BaseFormatterV2,
    FormatterInfo,
    FormatterRegistry,
    OutputSection,
    SectionConfig,
    get_registry,
    register,
)


class TestOutputSection:
    """Tests for OutputSection enum."""

    def test_all_sections_defined(self):
        """Test all expected sections exist."""
        expected = {
            "demographics",
            "goals",
            "pain_points",
            "behaviours",
            "motivations",
            "quotes",
            "evidence",
            "reasoning",
            "metadata",
            "additional",
        }
        actual = {s.value for s in OutputSection}
        assert actual == expected

    def test_section_values_are_strings(self):
        """Test section values are lowercase strings."""
        for section in OutputSection:
            assert isinstance(section.value, str)
            assert section.value == section.value.lower()


class TestSectionConfig:
    """Tests for SectionConfig."""

    def test_default_includes_design_sections(self):
        """Test default config includes design-relevant sections."""
        config = SectionConfig()
        assert OutputSection.DEMOGRAPHICS in config.include
        assert OutputSection.GOALS in config.include
        assert OutputSection.PAIN_POINTS in config.include
        assert OutputSection.BEHAVIOURS in config.include
        assert OutputSection.QUOTES in config.include
        # Not included by default
        assert OutputSection.EVIDENCE not in config.include
        assert OutputSection.REASONING not in config.include
        assert OutputSection.METADATA not in config.include

    def test_default_no_excludes(self):
        """Test default config has no exclusions."""
        config = SectionConfig()
        assert len(config.exclude) == 0

    def test_minimal_preset(self):
        """Test minimal preset includes core sections only."""
        config = SectionConfig.minimal()
        assert config.include == {
            OutputSection.DEMOGRAPHICS,
            OutputSection.GOALS,
            OutputSection.PAIN_POINTS,
        }

    def test_design_preset(self):
        """Test design preset includes design-focused sections."""
        config = SectionConfig.design()
        assert OutputSection.DEMOGRAPHICS in config.include
        assert OutputSection.BEHAVIOURS in config.include
        assert OutputSection.QUOTES in config.include
        assert OutputSection.EVIDENCE not in config.include

    def test_research_preset(self):
        """Test research preset includes evidence and reasoning."""
        config = SectionConfig.research()
        assert OutputSection.EVIDENCE in config.include
        assert OutputSection.REASONING in config.include
        assert OutputSection.QUOTES in config.include

    def test_full_preset(self):
        """Test full preset includes all sections."""
        config = SectionConfig.full()
        assert config.include == set(OutputSection)

    def test_should_include_returns_true_for_included(self):
        """Test should_include returns True for included sections."""
        config = SectionConfig(include={OutputSection.GOALS})
        assert config.should_include(OutputSection.GOALS) is True

    def test_should_include_returns_false_for_not_included(self):
        """Test should_include returns False for non-included sections."""
        config = SectionConfig(include={OutputSection.GOALS})
        assert config.should_include(OutputSection.BEHAVIOURS) is False

    def test_exclude_overrides_include(self):
        """Test excluded sections are not included even if in include set."""
        config = SectionConfig(
            include={OutputSection.GOALS, OutputSection.BEHAVIOURS},
            exclude={OutputSection.BEHAVIOURS},
        )
        assert config.should_include(OutputSection.GOALS) is True
        assert config.should_include(OutputSection.BEHAVIOURS) is False


class TestFormatterInfo:
    """Tests for FormatterInfo dataclass."""

    def test_creation(self):
        """Test FormatterInfo creation."""

        class DummyFormatter:
            pass

        info = FormatterInfo(
            name="test",
            description="Test formatter",
            extension=".test",
            formatter_class=DummyFormatter,
        )
        assert info.name == "test"
        assert info.description == "Test formatter"
        assert info.extension == ".test"
        assert info.formatter_class == DummyFormatter
        assert info.supports_sections is True
        assert info.supports_comparison is False

    def test_optional_fields(self):
        """Test FormatterInfo with optional fields."""

        class DummyFormatter:
            pass

        info = FormatterInfo(
            name="test",
            description="Test",
            extension=".test",
            formatter_class=DummyFormatter,
            supports_sections=False,
            supports_comparison=True,
        )
        assert info.supports_sections is False
        assert info.supports_comparison is True


class TestFormatterRegistry:
    """Tests for FormatterRegistry."""

    def test_builtin_formatters_registered(self):
        """Test built-in formatters are registered on creation."""
        registry = FormatterRegistry()
        assert registry.has("json")
        assert registry.has("markdown")
        assert registry.has("text")

    def test_register_new_formatter(self):
        """Test registering a new formatter."""
        registry = FormatterRegistry()

        class CustomFormatter:
            def format(self, persona):
                return "custom"

            def extension(self):
                return ".custom"

        registry.register(
            name="custom",
            formatter_class=CustomFormatter,
            description="Custom formatter",
            extension=".custom",
        )

        assert registry.has("custom")

    def test_register_duplicate_raises_error(self):
        """Test registering duplicate name raises ValueError."""
        registry = FormatterRegistry()

        class CustomFormatter:
            pass

        registry.register(
            name="custom",
            formatter_class=CustomFormatter,
            description="Custom",
            extension=".custom",
        )

        with pytest.raises(ValueError, match="already registered"):
            registry.register(
                name="custom",
                formatter_class=CustomFormatter,
                description="Another",
                extension=".custom2",
            )

    def test_unregister_removes_formatter(self):
        """Test unregistering removes formatter."""
        registry = FormatterRegistry()

        class CustomFormatter:
            pass

        registry.register(
            name="custom",
            formatter_class=CustomFormatter,
            description="Custom",
            extension=".custom",
        )

        assert registry.has("custom")
        registry.unregister("custom")
        assert not registry.has("custom")

    def test_unregister_nonexistent_raises_error(self):
        """Test unregistering non-existent formatter raises KeyError."""
        registry = FormatterRegistry()
        with pytest.raises(KeyError, match="not found"):
            registry.unregister("nonexistent")

    def test_get_returns_formatter_instance(self):
        """Test get returns formatter instance."""
        registry = FormatterRegistry()
        formatter = registry.get("json")
        assert formatter is not None
        assert hasattr(formatter, "format")

    def test_get_nonexistent_raises_error(self):
        """Test get for non-existent formatter raises KeyError."""
        registry = FormatterRegistry()
        with pytest.raises(KeyError, match="not found"):
            registry.get("nonexistent")

    def test_get_passes_kwargs_to_constructor(self):
        """Test get passes kwargs to formatter constructor."""
        registry = FormatterRegistry()
        formatter = registry.get("json", indent=4)
        # JSONFormatter stores indent in _indent
        assert formatter._indent == 4

    def test_get_info_returns_formatter_info(self):
        """Test get_info returns FormatterInfo."""
        registry = FormatterRegistry()
        info = registry.get_info("json")
        assert isinstance(info, FormatterInfo)
        assert info.name == "json"
        assert info.extension == ".json"

    def test_get_info_nonexistent_raises_error(self):
        """Test get_info for non-existent formatter raises KeyError."""
        registry = FormatterRegistry()
        with pytest.raises(KeyError, match="not found"):
            registry.get_info("nonexistent")

    def test_list_names_returns_sorted_list(self):
        """Test list_names returns sorted list of names."""
        registry = FormatterRegistry()
        names = registry.list_names()
        assert isinstance(names, list)
        assert names == sorted(names)
        assert "json" in names
        assert "markdown" in names
        assert "text" in names

    def test_list_all_returns_formatter_info_list(self):
        """Test list_all returns list of FormatterInfo."""
        registry = FormatterRegistry()
        all_formatters = registry.list_all()
        assert isinstance(all_formatters, list)
        assert all(isinstance(f, FormatterInfo) for f in all_formatters)
        assert len(all_formatters) >= 3  # At least builtins

    def test_has_returns_true_for_registered(self):
        """Test has returns True for registered formatter."""
        registry = FormatterRegistry()
        assert registry.has("json") is True

    def test_has_returns_false_for_unregistered(self):
        """Test has returns False for unregistered formatter."""
        registry = FormatterRegistry()
        assert registry.has("nonexistent") is False


class TestGlobalRegistry:
    """Tests for global registry functions."""

    def test_get_registry_returns_singleton(self):
        """Test get_registry returns same instance."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2

    def test_global_registry_has_builtins(self):
        """Test global registry has built-in formatters."""
        registry = get_registry()
        assert registry.has("json")
        assert registry.has("markdown")
        assert registry.has("text")


class TestRegisterDecorator:
    """Tests for @register decorator."""

    def test_decorator_registers_class(self):
        """Test @register decorator registers the class."""
        registry = get_registry()
        initial_count = len(registry.list_names())

        @register("test-decorator", "Test decorator formatter", ".dec")
        class DecoratorTestFormatter(BaseFormatterV2):
            def format(self, persona, sections=None):
                return "decorated"

            def extension(self):
                return ".dec"

        assert registry.has("test-decorator")
        assert len(registry.list_names()) == initial_count + 1

        # Cleanup
        registry.unregister("test-decorator")

    def test_decorator_returns_original_class(self):
        """Test @register decorator returns the original class."""
        registry = get_registry()

        @register("test-decorator-return", "Test", ".ret")
        class OriginalClass(BaseFormatterV2):
            def format(self, persona, sections=None):
                return "original"

            def extension(self):
                return ".ret"

        # Class should still be usable
        instance = OriginalClass()
        assert instance.format(None) == "original"

        # Cleanup
        registry.unregister("test-decorator-return")


class TestBaseFormatterV2:
    """Tests for BaseFormatterV2 abstract base class."""

    def test_default_section_config(self):
        """Test default section config is design preset."""

        class TestFormatter(BaseFormatterV2):
            def format(self, persona, sections=None):
                return "test"

            def extension(self):
                return ".test"

        formatter = TestFormatter()
        # Design preset is default
        assert formatter._sections.should_include(OutputSection.DEMOGRAPHICS)
        assert formatter._sections.should_include(OutputSection.BEHAVIOURS)
        assert not formatter._sections.should_include(OutputSection.EVIDENCE)

    def test_custom_section_config(self):
        """Test custom section config is respected."""

        class TestFormatter(BaseFormatterV2):
            def format(self, persona, sections=None):
                return "test"

            def extension(self):
                return ".test"

        config = SectionConfig.research()
        formatter = TestFormatter(sections=config)
        assert formatter._sections.should_include(OutputSection.EVIDENCE)
        assert formatter._sections.should_include(OutputSection.REASONING)

    def test_format_multiple_concatenates(self):
        """Test format_multiple concatenates individual formats."""

        class TestFormatter(BaseFormatterV2):
            def format(self, persona, sections=None):
                return f"Persona: {persona.name}"

            def extension(self):
                return ".test"

        formatter = TestFormatter()
        personas = [
            Persona(id="1", name="Alice", demographics={}, goals=[], pain_points=[]),
            Persona(id="2", name="Bob", demographics={}, goals=[], pain_points=[]),
        ]

        result = formatter.format_multiple(personas)
        assert "Persona: Alice" in result
        assert "Persona: Bob" in result
        assert "---" in result  # Separator

    def test_get_sections_returns_override(self):
        """Test _get_sections returns override when provided."""

        class TestFormatter(BaseFormatterV2):
            def format(self, persona, sections=None):
                return "test"

            def extension(self):
                return ".test"

        formatter = TestFormatter()
        override = SectionConfig.minimal()

        result = formatter._get_sections(override)
        assert result is override

    def test_get_sections_returns_default_when_no_override(self):
        """Test _get_sections returns default when no override."""

        class TestFormatter(BaseFormatterV2):
            def format(self, persona, sections=None):
                return "test"

            def extension(self):
                return ".test"

        config = SectionConfig.research()
        formatter = TestFormatter(sections=config)

        result = formatter._get_sections(None)
        assert result is config
