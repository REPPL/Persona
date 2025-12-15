"""
Tests for global configuration (F-085).
"""

import os
import pytest
from pathlib import Path

from persona.core.config.global_config import (
    GlobalConfig,
    ConfigManager,
    DefaultsConfig,
    BudgetConfig,
    get_global_config_path,
)


class TestGlobalConfig:
    """Tests for GlobalConfig schema."""

    def test_default_config(self):
        """Test default configuration values."""
        config = GlobalConfig.get_default()

        assert config.defaults.provider == "anthropic"
        assert config.defaults.complexity == "moderate"
        assert config.defaults.count == 3
        assert config.output.format == "json"
        assert config.logging.level == "info"
        assert config.telemetry.enabled is False

    def test_custom_config(self):
        """Test custom configuration values."""
        config = GlobalConfig(
            defaults=DefaultsConfig(
                provider="openai",
                model="gpt-4o",
                count=5,
            ),
        )

        assert config.defaults.provider == "openai"
        assert config.defaults.model == "gpt-4o"
        assert config.defaults.count == 5


class TestConfigManager:
    """Tests for ConfigManager."""

    def test_load_global_not_exists(self, tmp_path, monkeypatch):
        """Test loading global config when file doesn't exist."""
        monkeypatch.setattr(
            "persona.core.config.global_config.get_global_config_path",
            lambda: tmp_path / "nonexistent" / "config.yaml",
        )

        manager = ConfigManager()
        config = manager.load_global()

        assert config.defaults.provider == "anthropic"

    def test_load_global_exists(self, tmp_path, monkeypatch):
        """Test loading global config from file."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("""
defaults:
  provider: openai
  count: 10
""")

        monkeypatch.setattr(
            "persona.core.config.global_config.get_global_config_path",
            lambda: config_path,
        )

        manager = ConfigManager()
        config = manager.load_global()

        assert config.defaults.provider == "openai"
        assert config.defaults.count == 10

    def test_env_overrides(self, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv("PERSONA_DEFAULTS_PROVIDER", "gemini")
        monkeypatch.setenv("PERSONA_DEFAULTS_COUNT", "7")

        manager = ConfigManager()
        overrides = manager.load_env_overrides()

        assert overrides["defaults"]["provider"] == "gemini"
        assert overrides["defaults"]["count"] == 7

    def test_get_value(self, tmp_path, monkeypatch):
        """Test getting config values by path."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("""
defaults:
  provider: anthropic
""")

        monkeypatch.setattr(
            "persona.core.config.global_config.get_global_config_path",
            lambda: config_path,
        )
        monkeypatch.setattr(
            "persona.core.config.global_config.get_project_config_path",
            lambda: None,
        )

        manager = ConfigManager()
        value = manager.get_value("defaults.provider")

        assert value == "anthropic"

    def test_get_value_not_found(self, tmp_path, monkeypatch):
        """Test getting nonexistent config value."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("defaults:\n  provider: anthropic\n")

        monkeypatch.setattr(
            "persona.core.config.global_config.get_global_config_path",
            lambda: config_path,
        )
        monkeypatch.setattr(
            "persona.core.config.global_config.get_project_config_path",
            lambda: None,
        )

        manager = ConfigManager()

        with pytest.raises(KeyError):
            manager.get_value("nonexistent.path")

    def test_set_value(self, tmp_path, monkeypatch):
        """Test setting config values."""
        config_path = tmp_path / ".persona" / "config.yaml"

        monkeypatch.setattr(
            "persona.core.config.global_config.get_global_config_path",
            lambda: config_path,
        )

        manager = ConfigManager()
        manager.set_value("defaults.provider", "openai", user_level=True)

        # Verify file was created with value
        assert config_path.exists()
        content = config_path.read_text()
        assert "provider: openai" in content

    def test_init_global(self, tmp_path, monkeypatch):
        """Test initialising global config."""
        config_path = tmp_path / ".persona" / "config.yaml"

        monkeypatch.setattr(
            "persona.core.config.global_config.get_global_config_path",
            lambda: config_path,
        )

        manager = ConfigManager()
        path = manager.init_global()

        assert path == config_path
        assert config_path.exists()
        content = config_path.read_text()
        assert "provider: anthropic" in content

    def test_init_global_already_exists(self, tmp_path, monkeypatch):
        """Test init fails when config exists."""
        config_path = tmp_path / ".persona" / "config.yaml"
        config_path.parent.mkdir(parents=True)
        config_path.write_text("existing: config\n")

        monkeypatch.setattr(
            "persona.core.config.global_config.get_global_config_path",
            lambda: config_path,
        )

        manager = ConfigManager()

        with pytest.raises(FileExistsError):
            manager.init_global()

    def test_init_global_force(self, tmp_path, monkeypatch):
        """Test init with force overwrites existing."""
        config_path = tmp_path / ".persona" / "config.yaml"
        config_path.parent.mkdir(parents=True)
        config_path.write_text("existing: config\n")

        monkeypatch.setattr(
            "persona.core.config.global_config.get_global_config_path",
            lambda: config_path,
        )

        manager = ConfigManager()
        manager.init_global(force=True)

        content = config_path.read_text()
        assert "existing: config" not in content
        assert "provider: anthropic" in content

    def test_reset(self, tmp_path, monkeypatch):
        """Test resetting config."""
        config_path = tmp_path / ".persona" / "config.yaml"
        config_path.parent.mkdir(parents=True)
        config_path.write_text("existing: config\n")

        monkeypatch.setattr(
            "persona.core.config.global_config.get_global_config_path",
            lambda: config_path,
        )

        manager = ConfigManager()
        path = manager.reset(user_level=True)

        assert path == config_path
        assert not config_path.exists()

    def test_layered_config_precedence(self, tmp_path, monkeypatch):
        """Test configuration layer precedence."""
        # Global config
        global_path = tmp_path / "global" / "config.yaml"
        global_path.parent.mkdir(parents=True)
        global_path.write_text("""
defaults:
  provider: anthropic
  count: 3
  complexity: moderate
""")

        # Project config (overrides some values)
        project_path = tmp_path / "project" / ".persona" / "config.yaml"
        project_path.parent.mkdir(parents=True)
        project_path.write_text("""
defaults:
  count: 5
""")

        monkeypatch.setattr(
            "persona.core.config.global_config.get_global_config_path",
            lambda: global_path,
        )
        monkeypatch.setattr(
            "persona.core.config.global_config.get_project_config_path",
            lambda: project_path,
        )

        # Environment override
        monkeypatch.setenv("PERSONA_DEFAULTS_COMPLEXITY", "detailed")

        manager = ConfigManager()
        config = manager.load()

        # Provider from global (not overridden)
        assert config.defaults.provider == "anthropic"
        # Count from project (overrides global)
        assert config.defaults.count == 5
        # Complexity from env (overrides all)
        assert config.defaults.complexity == "detailed"
