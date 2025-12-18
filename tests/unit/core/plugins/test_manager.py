"""Tests for the PluginManager."""

import pytest
from persona.core.plugins.base import PluginType
from persona.core.plugins.exceptions import PluginNotFoundError
from persona.core.plugins.manager import PluginManager, get_plugin_manager


class TestPluginManager:
    """Tests for the PluginManager class."""

    @pytest.fixture
    def manager(self) -> PluginManager:
        """Get the global plugin manager."""
        return get_plugin_manager()

    def test_get_plugin_manager_returns_same_instance(self) -> None:
        """Should return the same instance."""
        manager1 = get_plugin_manager()
        manager2 = get_plugin_manager()
        assert manager1 is manager2

    def test_list_plugins(self, manager: PluginManager) -> None:
        """Should list all plugins."""
        plugins = manager.list_plugins()
        assert len(plugins) > 0

    def test_list_plugins_by_type(self, manager: PluginManager) -> None:
        """Should filter plugins by type."""
        formatters = manager.list_plugins(plugin_type=PluginType.FORMATTER)
        assert len(formatters) > 0
        assert all(p.plugin_type == PluginType.FORMATTER for p in formatters)

    def test_list_plugins_builtin_only(self, manager: PluginManager) -> None:
        """Should filter to builtin only."""
        builtins = manager.list_plugins(builtin_only=True)
        assert len(builtins) > 0
        assert all(p.builtin for p in builtins)

    def test_get_plugin(self, manager: PluginManager) -> None:
        """Should get a plugin instance."""
        formatter = manager.get_plugin(PluginType.FORMATTER, "json")
        assert formatter is not None

    def test_get_plugin_not_found(self, manager: PluginManager) -> None:
        """Should raise error for non-existent plugin."""
        with pytest.raises(PluginNotFoundError):
            manager.get_plugin(PluginType.FORMATTER, "nonexistent")

    def test_get_plugin_info(self, manager: PluginManager) -> None:
        """Should get plugin info."""
        info = manager.get_plugin_info(PluginType.FORMATTER, "json")
        assert info.name == "json"
        assert info.plugin_type == PluginType.FORMATTER

    def test_has_plugin(self, manager: PluginManager) -> None:
        """Should check if plugin exists."""
        assert manager.has_plugin(PluginType.FORMATTER, "json")
        assert not manager.has_plugin(PluginType.FORMATTER, "nonexistent")

    def test_count_plugins(self, manager: PluginManager) -> None:
        """Should count plugins."""
        total = manager.count_plugins()
        assert total > 0

        formatter_count = manager.count_plugins(PluginType.FORMATTER)
        assert formatter_count > 0
        assert formatter_count <= total

    def test_get_summary(self, manager: PluginManager) -> None:
        """Should return plugin summary."""
        summary = manager.get_summary()

        assert "total" in summary
        assert "enabled" in summary
        assert "disabled" in summary
        assert "builtin" in summary
        assert "external" in summary
        assert "by_type" in summary

        assert summary["total"] > 0
        assert summary["total"] == summary["enabled"] + summary["disabled"]

    def test_get_summary_by_type(self, manager: PluginManager) -> None:
        """Should include breakdown by type."""
        summary = manager.get_summary()

        assert "formatter" in summary["by_type"]
        assert "loader" in summary["by_type"]
        assert "provider" in summary["by_type"]
        assert "validator" in summary["by_type"]

        for type_summary in summary["by_type"].values():
            assert "total" in type_summary
            assert "enabled" in type_summary
            assert "builtin" in type_summary
            assert "external" in type_summary


class TestPluginManagerRegistries:
    """Tests for registry management in PluginManager."""

    @pytest.fixture
    def manager(self) -> PluginManager:
        """Get the global plugin manager."""
        return get_plugin_manager()

    def test_has_formatter_registry(self, manager: PluginManager) -> None:
        """Should have formatter registry."""
        registry = manager.get_registry(PluginType.FORMATTER)
        assert registry is not None
        assert registry.plugin_type == PluginType.FORMATTER

    def test_has_loader_registry(self, manager: PluginManager) -> None:
        """Should have loader registry."""
        registry = manager.get_registry(PluginType.LOADER)
        assert registry is not None
        assert registry.plugin_type == PluginType.LOADER

    def test_has_provider_registry(self, manager: PluginManager) -> None:
        """Should have provider registry."""
        registry = manager.get_registry(PluginType.PROVIDER)
        assert registry is not None
        assert registry.plugin_type == PluginType.PROVIDER

    def test_has_validator_registry(self, manager: PluginManager) -> None:
        """Should have validator registry."""
        registry = manager.get_registry(PluginType.VALIDATOR)
        assert registry is not None
        assert registry.plugin_type == PluginType.VALIDATOR

    def test_get_registry_not_found(self, manager: PluginManager) -> None:
        """Should raise error for non-existent registry type."""
        # Create a fresh manager without registries
        fresh_manager = PluginManager()
        with pytest.raises(KeyError, match="No registry"):
            fresh_manager.get_registry(PluginType.WORKFLOW)


class TestBuiltinPlugins:
    """Tests verifying built-in plugins are registered."""

    @pytest.fixture
    def manager(self) -> PluginManager:
        """Get the global plugin manager."""
        return get_plugin_manager()

    def test_builtin_formatters(self, manager: PluginManager) -> None:
        """Should have built-in formatters."""
        formatters = manager.list_plugins(
            plugin_type=PluginType.FORMATTER,
            builtin_only=True,
        )
        names = [p.name for p in formatters]

        assert "json" in names
        assert "markdown" in names
        assert "text" in names

    def test_builtin_loaders(self, manager: PluginManager) -> None:
        """Should have built-in loaders."""
        loaders = manager.list_plugins(
            plugin_type=PluginType.LOADER,
            builtin_only=True,
        )
        names = [p.name for p in loaders]

        assert "csv" in names
        assert "json" in names
        assert "yaml" in names
        assert "markdown" in names
        assert "text" in names

    def test_builtin_providers(self, manager: PluginManager) -> None:
        """Should have built-in providers."""
        providers = manager.list_plugins(
            plugin_type=PluginType.PROVIDER,
            builtin_only=True,
        )
        names = [p.name for p in providers]

        assert "openai" in names
        assert "anthropic" in names
        assert "gemini" in names

    def test_builtin_validators(self, manager: PluginManager) -> None:
        """Should have built-in validators."""
        validators = manager.list_plugins(
            plugin_type=PluginType.VALIDATOR,
            builtin_only=True,
        )
        names = [p.name for p in validators]

        assert "persona" in names
