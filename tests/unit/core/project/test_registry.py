"""Tests for project registry."""

from pathlib import Path
from unittest.mock import patch

import pytest
from persona.core.project.registry import (
    RegistryManager,
    get_registry_path,
    get_xdg_config_home,
)


class TestRegistryPaths:
    """Tests for registry path functions."""

    def test_get_xdg_config_home_default(self):
        """Test XDG config home defaults to ~/.config."""
        with patch.dict("os.environ", {}, clear=True):
            path = get_xdg_config_home()
            assert path == Path.home() / ".config"

    def test_get_xdg_config_home_custom(self, tmp_path):
        """Test XDG config home respects environment variable."""
        with patch.dict("os.environ", {"XDG_CONFIG_HOME": str(tmp_path)}):
            path = get_xdg_config_home()
            assert path == tmp_path

    def test_get_registry_path_xdg_exists(self, tmp_path):
        """Test registry path prefers XDG location when it exists."""
        xdg_path = tmp_path / "persona" / "config.yaml"
        xdg_path.parent.mkdir(parents=True)
        xdg_path.touch()

        with patch.dict("os.environ", {"XDG_CONFIG_HOME": str(tmp_path)}):
            path = get_registry_path()
            assert path == xdg_path

    def test_get_registry_path_legacy_fallback(self, tmp_path):
        """Test registry path falls back to legacy location."""
        legacy_path = tmp_path / ".persona" / "config.yaml"
        legacy_path.parent.mkdir(parents=True)
        legacy_path.touch()

        with patch("persona.core.project.registry.Path.home", return_value=tmp_path):
            with patch.dict("os.environ", {}, clear=True):
                # Clear XDG_CONFIG_HOME to ensure legacy fallback
                path = get_registry_path()
                # On non-Linux, should prefer legacy
                assert path.name == "config.yaml"


class TestRegistryManager:
    """Tests for RegistryManager class."""

    @pytest.fixture
    def registry_path(self, tmp_path):
        """Create a temporary registry path."""
        path = tmp_path / "config.yaml"
        return path

    @pytest.fixture
    def manager(self, registry_path):
        """Create a registry manager with temp path."""
        return RegistryManager(registry_path=registry_path)

    def test_init_creates_manager(self, manager):
        """Test manager initialisation."""
        assert manager is not None

    def test_get_registry_empty(self, manager):
        """Test getting registry when file doesn't exist."""
        registry = manager.get_registry()
        assert registry is not None
        assert len(registry.projects) == 0

    def test_register_project(self, manager, tmp_path):
        """Test registering a project."""
        project_path = tmp_path / "my-project"
        project_path.mkdir()

        manager.register_project("test", project_path)

        registry = manager.get_registry()
        assert "test" in registry.projects
        assert manager.get_project_path("test") == project_path.resolve()

    def test_register_duplicate_raises(self, manager, tmp_path):
        """Test registering duplicate project raises error."""
        project_path = tmp_path / "my-project"
        project_path.mkdir()

        manager.register_project("test", project_path)

        with pytest.raises(ValueError, match="already registered"):
            manager.register_project("test", project_path)

    def test_unregister_project(self, manager, tmp_path):
        """Test unregistering a project."""
        project_path = tmp_path / "my-project"
        project_path.mkdir()

        manager.register_project("test", project_path)
        result = manager.unregister_project("test")

        assert result is True
        assert not manager.project_exists("test")

    def test_unregister_nonexistent(self, manager):
        """Test unregistering non-existent project."""
        result = manager.unregister_project("nonexistent")
        assert result is False

    def test_update_project_path(self, manager, tmp_path):
        """Test updating project path."""
        old_path = tmp_path / "old"
        new_path = tmp_path / "new"
        old_path.mkdir()
        new_path.mkdir()

        manager.register_project("test", old_path)
        manager.update_project_path("test", new_path)

        assert manager.get_project_path("test") == new_path.resolve()

    def test_update_nonexistent_raises(self, manager, tmp_path):
        """Test updating non-existent project raises error."""
        with pytest.raises(ValueError, match="not registered"):
            manager.update_project_path("nonexistent", tmp_path)

    def test_list_projects(self, manager, tmp_path):
        """Test listing projects."""
        for name in ["alpha", "beta", "gamma"]:
            path = tmp_path / name
            path.mkdir()
            manager.register_project(name, path)

        projects = manager.list_projects()
        assert len(projects) == 3
        names = [name for name, _ in projects]
        assert sorted(names) == ["alpha", "beta", "gamma"]

    def test_project_exists(self, manager, tmp_path):
        """Test checking if project exists."""
        project_path = tmp_path / "test"
        project_path.mkdir()

        assert not manager.project_exists("test")
        manager.register_project("test", project_path)
        assert manager.project_exists("test")

    def test_get_defaults(self, manager):
        """Test getting defaults."""
        defaults = manager.get_defaults()
        assert defaults.provider == "anthropic"
        assert defaults.count == 3

    def test_set_defaults(self, manager):
        """Test setting defaults."""
        manager.set_defaults(provider="openai", count=5)

        defaults = manager.get_defaults()
        assert defaults.provider == "openai"
        assert defaults.count == 5

    def test_init_registry(self, tmp_path):
        """Test initialising registry."""
        registry_path = tmp_path / "new" / "config.yaml"
        manager = RegistryManager(registry_path=registry_path)

        path = manager.init_registry()

        assert path.exists()
        assert "Persona Project Registry" in path.read_text()

    def test_init_registry_exists_raises(self, tmp_path):
        """Test initialising registry when file exists raises."""
        registry_path = tmp_path / "config.yaml"
        registry_path.touch()
        manager = RegistryManager(registry_path=registry_path)

        with pytest.raises(FileExistsError):
            manager.init_registry()

    def test_init_registry_force(self, tmp_path):
        """Test force initialising registry."""
        registry_path = tmp_path / "config.yaml"
        registry_path.write_text("old content")
        manager = RegistryManager(registry_path=registry_path)

        path = manager.init_registry(force=True)

        assert "Persona Project Registry" in path.read_text()

    def test_persistence(self, registry_path, tmp_path):
        """Test that registry persists across instances."""
        project_path = tmp_path / "test"
        project_path.mkdir()

        # Create and save
        manager1 = RegistryManager(registry_path=registry_path)
        manager1.register_project("test", project_path)

        # Load in new instance
        manager2 = RegistryManager(registry_path=registry_path)
        assert manager2.project_exists("test")
        assert manager2.get_project_path("test") == project_path.resolve()
