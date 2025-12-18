"""Tests for project models."""


import pytest
from persona.core.project.models import (
    DataSource,
    DataSourceType,
    GlobalDefaults,
    ProjectDefaults,
    ProjectMetadata,
    ProjectRegistry,
    ProjectTemplate,
)


class TestDataSource:
    """Tests for DataSource model."""

    def test_create_data_source(self):
        """Test creating a data source."""
        ds = DataSource(
            name="interviews",
            path="data/interviews.csv",
            type=DataSourceType.QUALITATIVE,
        )
        assert ds.name == "interviews"
        assert ds.path == "data/interviews.csv"
        assert ds.type == DataSourceType.QUALITATIVE

    def test_get_absolute_path(self, tmp_path):
        """Test getting absolute path from relative path."""
        ds = DataSource(
            name="test",
            path="data/test.csv",
        )
        expected = tmp_path / "data" / "test.csv"
        assert ds.get_absolute_path(tmp_path) == expected

    def test_data_source_with_description(self):
        """Test data source with description."""
        ds = DataSource(
            name="survey",
            path="data/survey.json",
            type=DataSourceType.QUANTITATIVE,
            description="Customer satisfaction survey results",
        )
        assert ds.description == "Customer satisfaction survey results"


class TestProjectDefaults:
    """Tests for ProjectDefaults model."""

    def test_default_values(self):
        """Test default values are set correctly."""
        defaults = ProjectDefaults()
        assert defaults.provider == "anthropic"
        assert defaults.model is None
        assert defaults.count == 3
        assert defaults.workflow == "default"

    def test_custom_values(self):
        """Test custom values override defaults."""
        defaults = ProjectDefaults(
            provider="openai",
            model="gpt-4o",
            count=5,
        )
        assert defaults.provider == "openai"
        assert defaults.model == "gpt-4o"
        assert defaults.count == 5


class TestProjectMetadata:
    """Tests for ProjectMetadata model."""

    def test_create_minimal(self):
        """Test creating metadata with minimal fields."""
        metadata = ProjectMetadata(name="test-project")
        assert metadata.name == "test-project"
        assert metadata.template == ProjectTemplate.BASIC
        assert metadata.description is None

    def test_create_full(self):
        """Test creating metadata with all fields."""
        metadata = ProjectMetadata(
            name="research-project",
            description="User research study",
            template=ProjectTemplate.RESEARCH,
            defaults=ProjectDefaults(provider="openai", count=5),
        )
        assert metadata.name == "research-project"
        assert metadata.description == "User research study"
        assert metadata.template == ProjectTemplate.RESEARCH
        assert metadata.defaults.provider == "openai"

    def test_name_validation_valid(self):
        """Test valid project names."""
        valid_names = ["test", "my-project", "project_1", "Test123"]
        for name in valid_names:
            metadata = ProjectMetadata(name=name)
            assert metadata.name == name

    def test_name_validation_invalid(self):
        """Test invalid project names raise errors."""
        invalid_names = ["", "my project", "project@name", "test/path"]
        for name in invalid_names:
            with pytest.raises(ValueError):
                ProjectMetadata(name=name)

    def test_to_yaml_dict(self):
        """Test conversion to YAML-compatible dict."""
        metadata = ProjectMetadata(
            name="test",
            template=ProjectTemplate.RESEARCH,
        )
        yaml_dict = metadata.to_yaml_dict()
        assert yaml_dict["name"] == "test"
        assert yaml_dict["template"] == "research"
        assert isinstance(yaml_dict["created_at"], str)

    def test_from_yaml_dict(self):
        """Test creation from YAML dict."""
        data = {
            "name": "test-project",
            "description": "Test description",
            "template": "basic",
            "created_at": "2025-01-01T00:00:00",
        }
        metadata = ProjectMetadata.from_yaml_dict(data)
        assert metadata.name == "test-project"
        assert metadata.description == "Test description"
        assert metadata.template == ProjectTemplate.BASIC

    def test_from_legacy_format(self):
        """Test creation from legacy persona.yaml format."""
        legacy_data = {
            "project": {
                "name": "legacy-project",
                "description": "Legacy description",
            },
            "defaults": {
                "provider": "openai",
            },
        }
        metadata = ProjectMetadata.from_yaml_dict(legacy_data)
        assert metadata.name == "legacy-project"
        assert metadata.description == "Legacy description"


class TestProjectRegistry:
    """Tests for ProjectRegistry model."""

    def test_create_empty(self):
        """Test creating empty registry."""
        registry = ProjectRegistry()
        assert registry.version == "1.0"
        assert len(registry.projects) == 0

    def test_register_project(self, tmp_path):
        """Test registering a project."""
        registry = ProjectRegistry()
        registry.register("test", tmp_path / "test")
        assert "test" in registry.projects

    def test_unregister_project(self, tmp_path):
        """Test unregistering a project."""
        registry = ProjectRegistry()
        registry.register("test", tmp_path / "test")
        result = registry.unregister("test")
        assert result is True
        assert "test" not in registry.projects

    def test_unregister_nonexistent(self):
        """Test unregistering non-existent project."""
        registry = ProjectRegistry()
        result = registry.unregister("nonexistent")
        assert result is False

    def test_get_project_path(self, tmp_path):
        """Test getting project path."""
        registry = ProjectRegistry()
        registry.register("test", tmp_path / "test")
        path = registry.get_project_path("test")
        assert path == tmp_path / "test"

    def test_list_projects(self, tmp_path):
        """Test listing projects."""
        registry = ProjectRegistry()
        registry.register("alpha", tmp_path / "alpha")
        registry.register("beta", tmp_path / "beta")
        projects = registry.list_projects()
        assert len(projects) == 2
        names = [name for name, _ in projects]
        assert "alpha" in names
        assert "beta" in names


class TestGlobalDefaults:
    """Tests for GlobalDefaults model."""

    def test_default_values(self):
        """Test default values."""
        defaults = GlobalDefaults()
        assert defaults.provider == "anthropic"
        assert defaults.model is None
        assert defaults.count == 3

    def test_custom_values(self):
        """Test custom values."""
        defaults = GlobalDefaults(
            provider="gemini",
            model="gemini-pro",
            count=10,
        )
        assert defaults.provider == "gemini"
        assert defaults.model == "gemini-pro"
        assert defaults.count == 10
