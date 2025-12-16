"""Tests for project manager."""

from pathlib import Path
from unittest.mock import patch

import pytest

from persona.core.project.manager import (
    ProjectManager,
    create_project,
    load_project,
)
from persona.core.project.models import (
    DataSourceType,
    ProjectDefaults,
    ProjectTemplate,
)


class TestProjectManager:
    """Tests for ProjectManager class."""

    def test_detect_project_yaml(self, tmp_path):
        """Test detecting project.yaml."""
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text("name: test")

        manager = ProjectManager()
        detected = manager.detect_project(project_dir)

        assert detected == project_dir

    def test_detect_persona_yaml(self, tmp_path):
        """Test detecting persona.yaml (legacy)."""
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()
        (project_dir / "persona.yaml").write_text("project:\n  name: test")

        manager = ProjectManager()
        detected = manager.detect_project(project_dir)

        assert detected == project_dir

    def test_detect_project_searches_up(self, tmp_path):
        """Test project detection searches up directory tree."""
        project_dir = tmp_path / "project"
        nested_dir = project_dir / "src" / "deep" / "nested"
        project_dir.mkdir()
        nested_dir.mkdir(parents=True)
        (project_dir / "project.yaml").write_text("name: test")

        manager = ProjectManager()
        detected = manager.detect_project(nested_dir)

        assert detected == project_dir

    def test_detect_no_project(self, tmp_path):
        """Test detecting when no project exists."""
        manager = ProjectManager()
        detected = manager.detect_project(tmp_path)

        assert detected is None

    def test_load_project(self, tmp_path):
        """Test loading a project."""
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text(
            """
name: my-project
description: Test project
template: basic
"""
        )

        manager = ProjectManager()
        metadata = manager.load(project_dir)

        assert metadata.name == "my-project"
        assert metadata.description == "Test project"
        assert metadata.template == ProjectTemplate.BASIC

    def test_load_legacy_format(self, tmp_path):
        """Test loading legacy persona.yaml format."""
        project_dir = tmp_path / "legacy"
        project_dir.mkdir()
        (project_dir / "persona.yaml").write_text(
            """
project:
  name: legacy-project
  description: Legacy format
defaults:
  provider: openai
  count: 5
"""
        )

        manager = ProjectManager()
        metadata = manager.load(project_dir)

        assert metadata.name == "legacy-project"
        assert metadata.description == "Legacy format"

    def test_load_not_found(self, tmp_path):
        """Test loading non-existent project raises."""
        manager = ProjectManager()

        with pytest.raises(FileNotFoundError):
            manager.load(tmp_path)

    def test_save_project(self, tmp_path):
        """Test saving project metadata."""
        project_dir = tmp_path / "test"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text("name: test")

        manager = ProjectManager()
        manager.load(project_dir)
        manager._metadata.description = "Updated description"
        path = manager.save()

        assert path.exists()
        content = path.read_text()
        assert "Updated description" in content

    def test_create_basic_project(self, tmp_path):
        """Test creating a basic project."""
        # Mock registry to avoid file operations
        with patch("persona.core.project.manager.get_registry_manager"):
            manager = ProjectManager()
            metadata = manager.create(
                name="test-project",
                path=tmp_path,
                template=ProjectTemplate.BASIC,
                description="Test description",
                register=False,
            )

        project_dir = tmp_path / "test-project"
        assert project_dir.exists()
        assert (project_dir / "project.yaml").exists()
        assert (project_dir / "data").is_dir()
        assert (project_dir / "output").is_dir()
        assert (project_dir / "README.md").exists()

        assert metadata.name == "test-project"
        assert metadata.description == "Test description"

    def test_create_research_project(self, tmp_path):
        """Test creating a research project."""
        with patch("persona.core.project.manager.get_registry_manager"):
            manager = ProjectManager()
            manager.create(
                name="research",
                path=tmp_path,
                template=ProjectTemplate.RESEARCH,
                register=False,
            )

        project_dir = tmp_path / "research"
        assert (project_dir / "data" / "raw").is_dir()
        assert (project_dir / "data" / "processed").is_dir()
        assert (project_dir / "config" / "prompts").is_dir()
        assert (project_dir / "config" / "models").is_dir()
        assert (project_dir / "output" / "personas").is_dir()
        assert (project_dir / "templates").is_dir()

    def test_create_existing_raises(self, tmp_path):
        """Test creating in existing directory raises."""
        existing = tmp_path / "existing"
        existing.mkdir()

        with patch("persona.core.project.manager.get_registry_manager"):
            manager = ProjectManager()

            with pytest.raises(FileExistsError):
                manager.create(name="existing", path=tmp_path, register=False)

    def test_add_data_source(self, tmp_path):
        """Test adding a data source."""
        project_dir = tmp_path / "test"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text("name: test")

        manager = ProjectManager()
        manager.load(project_dir)
        ds = manager.add_data_source(
            name="interviews",
            path="data/interviews.csv",
            source_type="qualitative",
        )

        assert ds.name == "interviews"
        assert ds.type == DataSourceType.QUALITATIVE

        # Check it was saved
        sources = manager.list_data_sources()
        assert len(sources) == 1

    def test_add_duplicate_data_source_raises(self, tmp_path):
        """Test adding duplicate data source raises."""
        project_dir = tmp_path / "test"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text("name: test")

        manager = ProjectManager()
        manager.load(project_dir)
        manager.add_data_source(name="test", path="data/test.csv")

        with pytest.raises(ValueError, match="already exists"):
            manager.add_data_source(name="test", path="data/other.csv")

    def test_remove_data_source(self, tmp_path):
        """Test removing a data source."""
        project_dir = tmp_path / "test"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text("name: test")

        manager = ProjectManager()
        manager.load(project_dir)
        manager.add_data_source(name="test", path="data/test.csv")

        result = manager.remove_data_source("test")
        assert result is True
        assert len(manager.list_data_sources()) == 0

    def test_remove_nonexistent_data_source(self, tmp_path):
        """Test removing non-existent data source."""
        project_dir = tmp_path / "test"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text("name: test")

        manager = ProjectManager()
        manager.load(project_dir)

        result = manager.remove_data_source("nonexistent")
        assert result is False

    def test_get_data_source(self, tmp_path):
        """Test getting a data source by name."""
        project_dir = tmp_path / "test"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text("name: test")

        manager = ProjectManager()
        manager.load(project_dir)
        manager.add_data_source(name="test", path="data/test.csv")

        ds = manager.get_data_source("test")
        assert ds is not None
        assert ds.name == "test"

        assert manager.get_data_source("nonexistent") is None

    def test_update_defaults(self, tmp_path):
        """Test updating project defaults."""
        project_dir = tmp_path / "test"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text("name: test")

        manager = ProjectManager()
        manager.load(project_dir)
        manager.update_defaults(provider="openai", count=10)

        assert manager.metadata.defaults.provider == "openai"
        assert manager.metadata.defaults.count == 10


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_load_project(self, tmp_path):
        """Test load_project function."""
        project_dir = tmp_path / "test"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text("name: test")

        manager = load_project(project_dir)

        assert manager.metadata.name == "test"

    def test_create_project(self, tmp_path):
        """Test create_project function."""
        with patch("persona.core.project.manager.get_registry_manager"):
            manager = create_project(
                name="new-project",
                path=tmp_path,
                template="research",
                description="New project",
                register=False,
            )

        assert manager.metadata.name == "new-project"
        assert manager.metadata.template == ProjectTemplate.RESEARCH
