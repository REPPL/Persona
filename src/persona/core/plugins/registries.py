"""
Concrete plugin registries for each extension point.

This module provides specific registry implementations for formatters,
loaders, providers, and validators.
"""


from persona.core.plugins.base import PluginRegistry, PluginType


class FormatterPluginRegistry(PluginRegistry):
    """
    Registry for output formatter plugins.

    Manages formatters that convert personas to various output formats
    (JSON, Markdown, text, etc.).
    """

    plugin_type = PluginType.FORMATTER
    entry_point_group = "persona.formatters"

    def __init__(self) -> None:
        """Initialise the formatter registry."""
        super().__init__()
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register built-in formatters."""
        from persona.core.output.formatters import (
            JSONFormatter,
            MarkdownFormatter,
            TextFormatter,
        )

        self.register(
            name="json",
            plugin_class=JSONFormatter,
            description="JSON format for programmatic use",
            builtin=True,
            extension=".json",
            supports_sections=False,
        )
        self.register(
            name="markdown",
            plugin_class=MarkdownFormatter,
            description="Markdown format for documentation",
            builtin=True,
            extension=".md",
            supports_sections=True,
        )
        self.register(
            name="text",
            plugin_class=TextFormatter,
            description="Plain text format for terminal display",
            builtin=True,
            extension=".txt",
            supports_sections=True,
        )


class LoaderPluginRegistry(PluginRegistry):
    """
    Registry for data loader plugins.

    Manages loaders that read data from various file formats
    (CSV, JSON, YAML, etc.).
    """

    plugin_type = PluginType.LOADER
    entry_point_group = "persona.loaders"

    def __init__(self) -> None:
        """Initialise the loader registry."""
        super().__init__()
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register built-in loaders."""
        from persona.core.data.formats import (
            CSVLoader,
            HTMLLoader,
            JSONLoader,
            MarkdownLoader,
            OrgLoader,
            TextLoader,
            YAMLLoader,
        )

        self.register(
            name="csv",
            plugin_class=CSVLoader,
            description="CSV file loader",
            builtin=True,
            extensions=[".csv"],
        )
        self.register(
            name="html",
            plugin_class=HTMLLoader,
            description="HTML file loader",
            builtin=True,
            extensions=[".html", ".htm"],
        )
        self.register(
            name="json",
            plugin_class=JSONLoader,
            description="JSON file loader",
            builtin=True,
            extensions=[".json"],
        )
        self.register(
            name="markdown",
            plugin_class=MarkdownLoader,
            description="Markdown file loader",
            builtin=True,
            extensions=[".md", ".markdown"],
        )
        self.register(
            name="org",
            plugin_class=OrgLoader,
            description="Org-mode file loader",
            builtin=True,
            extensions=[".org"],
        )
        self.register(
            name="text",
            plugin_class=TextLoader,
            description="Plain text file loader",
            builtin=True,
            extensions=[".txt"],
        )
        self.register(
            name="yaml",
            plugin_class=YAMLLoader,
            description="YAML file loader",
            builtin=True,
            extensions=[".yaml", ".yml"],
        )


class ProviderPluginRegistry(PluginRegistry):
    """
    Registry for LLM provider plugins.

    Manages providers that interface with various LLM services
    (OpenAI, Anthropic, Gemini, etc.).
    """

    plugin_type = PluginType.PROVIDER
    entry_point_group = "persona.providers"

    def __init__(self) -> None:
        """Initialise the provider registry."""
        super().__init__()
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register built-in providers."""
        from persona.core.providers.anthropic import AnthropicProvider
        from persona.core.providers.gemini import GeminiProvider
        from persona.core.providers.openai import OpenAIProvider

        self.register(
            name="openai",
            plugin_class=OpenAIProvider,
            description="OpenAI API provider (GPT models)",
            builtin=True,
            models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        )
        self.register(
            name="anthropic",
            plugin_class=AnthropicProvider,
            description="Anthropic API provider (Claude models)",
            builtin=True,
            models=["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022"],
        )
        self.register(
            name="gemini",
            plugin_class=GeminiProvider,
            description="Google Gemini API provider",
            builtin=True,
            models=["gemini-1.5-pro", "gemini-1.5-flash"],
        )


class ValidatorPluginRegistry(PluginRegistry):
    """
    Registry for validator plugins.

    Manages validators that check persona quality and validity.
    """

    plugin_type = PluginType.VALIDATOR
    entry_point_group = "persona.validators"

    def __init__(self) -> None:
        """Initialise the validator registry."""
        super().__init__()
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register built-in validators."""
        from persona.core.validation.validator import PersonaValidator

        self.register(
            name="persona",
            plugin_class=PersonaValidator,
            description="Default persona validator",
            builtin=True,
        )


# Global registry instances
_formatter_registry: FormatterPluginRegistry | None = None
_loader_registry: LoaderPluginRegistry | None = None
_provider_registry: ProviderPluginRegistry | None = None
_validator_registry: ValidatorPluginRegistry | None = None


def get_formatter_registry() -> FormatterPluginRegistry:
    """Get the global formatter registry."""
    global _formatter_registry
    if _formatter_registry is None:
        _formatter_registry = FormatterPluginRegistry()
    return _formatter_registry


def get_loader_registry() -> LoaderPluginRegistry:
    """Get the global loader registry."""
    global _loader_registry
    if _loader_registry is None:
        _loader_registry = LoaderPluginRegistry()
    return _loader_registry


def get_provider_registry() -> ProviderPluginRegistry:
    """Get the global provider registry."""
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = ProviderPluginRegistry()
    return _provider_registry


def get_validator_registry() -> ValidatorPluginRegistry:
    """Get the global validator registry."""
    global _validator_registry
    if _validator_registry is None:
        _validator_registry = ValidatorPluginRegistry()
    return _validator_registry
