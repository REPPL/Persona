"""Tests for plugin base classes."""

import pytest

from persona.core.plugins.base import PluginInfo, PluginRegistry, PluginType


class DummyPlugin:
    """Dummy plugin class for testing."""

    def __init__(self, value: str = "default") -> None:
        self.value = value


class MockPluginRegistry(PluginRegistry[DummyPlugin]):
    """Mock implementation of PluginRegistry for testing."""

    plugin_type = PluginType.FORMATTER
    entry_point_group = "persona.test"

    def _register_builtins(self) -> None:
        """Register built-in test plugins."""
        self.register(
            name="builtin1",
            plugin_class=DummyPlugin,
            description="First builtin plugin",
            builtin=True,
        )


class TestPluginInfo:
    """Tests for PluginInfo dataclass."""

    def test_create_plugin_info(self) -> None:
        """Should create PluginInfo with all fields."""
        info = PluginInfo(
            name="test",
            description="Test plugin",
            plugin_type=PluginType.FORMATTER,
            plugin_class=DummyPlugin,
            version="1.0.0",
            author="Test Author",
            enabled=True,
            builtin=False,
        )

        assert info.name == "test"
        assert info.description == "Test plugin"
        assert info.plugin_type == PluginType.FORMATTER
        assert info.version == "1.0.0"
        assert info.author == "Test Author"
        assert info.enabled is True
        assert info.builtin is False

    def test_to_dict(self) -> None:
        """Should convert PluginInfo to dictionary."""
        info = PluginInfo(
            name="test",
            description="Test plugin",
            plugin_type=PluginType.LOADER,
            plugin_class=DummyPlugin,
            version="2.0.0",
            metadata={"key": "value"},
        )

        data = info.to_dict()

        assert data["name"] == "test"
        assert data["type"] == "loader"
        assert data["version"] == "2.0.0"
        assert data["metadata"] == {"key": "value"}


class TestPluginType:
    """Tests for PluginType enum."""

    def test_plugin_types(self) -> None:
        """Should have expected plugin types."""
        assert PluginType.FORMATTER.value == "formatter"
        assert PluginType.LOADER.value == "loader"
        assert PluginType.PROVIDER.value == "provider"
        assert PluginType.VALIDATOR.value == "validator"
        assert PluginType.WORKFLOW.value == "workflow"


class MockPluginRegistryBase:
    """Tests for PluginRegistry base class."""

    @pytest.fixture
    def registry(self) -> MockPluginRegistry:
        """Create a test registry."""
        return MockPluginRegistry()

    def test_register_plugin(self, registry: MockPluginRegistry) -> None:
        """Should register a plugin."""
        registry.register(
            name="custom",
            plugin_class=DummyPlugin,
            description="Custom plugin",
        )

        assert registry.has("custom")
        info = registry.get_info("custom")
        assert info.name == "custom"
        assert info.description == "Custom plugin"

    def test_register_duplicate_raises(self, registry: MockPluginRegistry) -> None:
        """Should raise error for duplicate registration."""
        registry.register(name="test", plugin_class=DummyPlugin)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(name="test", plugin_class=DummyPlugin)

    def test_unregister_plugin(self, registry: MockPluginRegistry) -> None:
        """Should unregister a plugin."""
        registry.register(name="removable", plugin_class=DummyPlugin)
        assert registry.has("removable")

        registry.unregister("removable")
        assert not registry.has("removable")

    def test_unregister_not_found_raises(self, registry: MockPluginRegistry) -> None:
        """Should raise error when unregistering non-existent plugin."""
        with pytest.raises(KeyError, match="not found"):
            registry.unregister("nonexistent")

    def test_get_plugin(self, registry: MockPluginRegistry) -> None:
        """Should get plugin instance."""
        registry.register(name="test", plugin_class=DummyPlugin)

        plugin = registry.get("test")
        assert isinstance(plugin, DummyPlugin)

    def test_get_plugin_with_kwargs(self, registry: MockPluginRegistry) -> None:
        """Should pass kwargs to plugin constructor."""
        registry.register(name="test", plugin_class=DummyPlugin)

        plugin = registry.get("test", value="custom")
        assert plugin.value == "custom"

    def test_get_not_found_raises(self, registry: MockPluginRegistry) -> None:
        """Should raise error for non-existent plugin."""
        with pytest.raises(KeyError, match="not found"):
            registry.get("nonexistent")

    def test_get_cached_returns_same_instance(
        self, registry: MockPluginRegistry
    ) -> None:
        """Should return same instance for cached get."""
        registry.register(name="test", plugin_class=DummyPlugin)

        plugin1 = registry.get_cached("test")
        plugin2 = registry.get_cached("test")
        assert plugin1 is plugin2

    def test_list_names(self, registry: MockPluginRegistry) -> None:
        """Should list all plugin names."""
        registry.register(name="alpha", plugin_class=DummyPlugin)
        registry.register(name="beta", plugin_class=DummyPlugin)

        names = registry.list_names()
        assert "alpha" in names
        assert "beta" in names
        assert "builtin1" in names

    def test_list_builtin(self, registry: MockPluginRegistry) -> None:
        """Should list only builtin plugins."""
        registry.register(name="custom", plugin_class=DummyPlugin, builtin=False)

        builtin_names = registry.list_builtin()
        assert "builtin1" in builtin_names
        assert "custom" not in builtin_names

    def test_list_external(self, registry: MockPluginRegistry) -> None:
        """Should list only external plugins."""
        registry.register(name="external", plugin_class=DummyPlugin, builtin=False)

        external_names = registry.list_external()
        assert "external" in external_names
        assert "builtin1" not in external_names

    def test_enable_disable_plugin(self, registry: MockPluginRegistry) -> None:
        """Should enable and disable plugins."""
        registry.register(name="toggle", plugin_class=DummyPlugin)
        assert registry.get_info("toggle").enabled is True

        registry.disable("toggle")
        assert registry.get_info("toggle").enabled is False

        registry.enable("toggle")
        assert registry.get_info("toggle").enabled is True

    def test_get_disabled_raises(self, registry: MockPluginRegistry) -> None:
        """Should raise error when getting disabled plugin."""
        registry.register(name="disabled", plugin_class=DummyPlugin)
        registry.disable("disabled")

        with pytest.raises(KeyError, match="disabled"):
            registry.get("disabled")

    def test_list_enabled(self, registry: MockPluginRegistry) -> None:
        """Should list only enabled plugins."""
        registry.register(name="enabled", plugin_class=DummyPlugin)
        registry.register(name="disabled", plugin_class=DummyPlugin)
        registry.disable("disabled")

        enabled = registry.list_enabled()
        assert "enabled" in enabled
        assert "disabled" not in enabled

    def test_clear_cache(self, registry: MockPluginRegistry) -> None:
        """Should clear cached instances."""
        registry.register(name="test", plugin_class=DummyPlugin)

        plugin1 = registry.get_cached("test")
        registry.clear_cache()
        plugin2 = registry.get_cached("test")

        assert plugin1 is not plugin2

    def test_list_all_returns_plugin_info(
        self, registry: MockPluginRegistry
    ) -> None:
        """Should return list of PluginInfo objects."""
        plugins = registry.list_all()

        assert len(plugins) > 0
        assert all(isinstance(p, PluginInfo) for p in plugins)

    def test_register_entry_point(self, registry: MockPluginRegistry) -> None:
        """Should register plugin from entry point."""
        registry.register_entry_point(
            name="entry",
            plugin_class=DummyPlugin,
            entry_point="persona.test:entry",
            description="Entry point plugin",
        )

        info = registry.get_info("entry")
        assert info.entry_point == "persona.test:entry"
        assert info.builtin is False

    def test_register_entry_point_skips_if_exists(
        self, registry: MockPluginRegistry
    ) -> None:
        """Should skip entry point registration if name exists."""
        registry.register(name="exists", plugin_class=DummyPlugin, builtin=True)

        # This should not override the existing registration
        registry.register_entry_point(
            name="exists",
            plugin_class=DummyPlugin,
            entry_point="persona.test:exists",
        )

        info = registry.get_info("exists")
        assert info.builtin is True  # Original registration preserved
        assert info.entry_point is None
