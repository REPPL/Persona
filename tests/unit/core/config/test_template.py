"""Tests for custom prompt template configuration."""

import tempfile
from pathlib import Path

import pytest
from persona.core.config.template import (
    TemplateLoader,
    TemplateMetadata,
    get_builtin_templates,
)


class TestTemplateMetadata:
    """Tests for TemplateMetadata model."""

    def test_default_values(self):
        """Test default metadata values."""
        meta = TemplateMetadata(name="Test")
        assert meta.name == "Test"
        assert meta.description == ""
        assert meta.author == ""
        assert meta.version == "1.0.0"
        assert meta.extends is None
        assert meta.tags == []

    def test_custom_values(self):
        """Test custom metadata values."""
        meta = TemplateMetadata(
            name="Healthcare Template",
            description="For healthcare personas",
            author="Test Author",
            version="2.0.0",
            extends="default",
            tags=["healthcare", "patient"],
        )
        assert meta.name == "Healthcare Template"
        assert meta.version == "2.0.0"
        assert "healthcare" in meta.tags

    def test_from_template_with_front_matter(self):
        """Test extracting metadata from template content."""
        content = """{# ---
name: Test Template
description: A test template
author: Tester
version: 1.2.0
tags:
  - test
  - example
--- #}
Template body here
"""
        meta = TemplateMetadata.from_template(content)
        assert meta.name == "Test Template"
        assert meta.description == "A test template"
        assert meta.author == "Tester"
        assert meta.version == "1.2.0"
        assert "test" in meta.tags

    def test_from_template_without_front_matter(self):
        """Test extracting metadata from template without front matter."""
        content = "Just a template body with {{ variable }}"
        meta = TemplateMetadata.from_template(content)
        assert meta.name == "Unnamed Template"

    def test_from_template_malformed_front_matter(self):
        """Test handling malformed front matter."""
        content = """{# ---
not valid yaml: [
--- #}
Body
"""
        meta = TemplateMetadata.from_template(content)
        assert meta.name == "Unnamed Template"


class TestTemplateLoader:
    """Tests for TemplateLoader."""

    def test_default_search_paths(self):
        """Test default search paths."""
        loader = TemplateLoader()
        assert loader._user_dir == Path.home() / ".persona" / "templates"
        assert loader._project_dir == Path(".persona") / "templates"

    def test_list_templates_empty(self):
        """Test listing templates with no custom templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = TemplateLoader(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
            )
            # Should still find built-in templates
            templates = loader.list_templates()
            assert "default" in templates
            assert "healthcare" in templates

    def test_list_templates_with_custom(self):
        """Test listing templates with custom templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            # Create custom template
            (user_dir / "custom.j2").write_text("{{ data }}")

            loader = TemplateLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            templates = loader.list_templates()
            assert "custom" in templates

    def test_list_templates_by_source(self):
        """Test listing templates filtered by source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "user-template.j2").write_text("{{ data }}")

            loader = TemplateLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            user_templates = loader.list_templates(source="user")
            assert "user-template" in user_templates
            assert "default" not in user_templates

            builtin_templates = loader.list_templates(source="builtin")
            assert "default" in builtin_templates
            assert "user-template" not in builtin_templates

    def test_list_templates_by_tag(self):
        """Test listing templates filtered by tag."""
        loader = TemplateLoader()
        healthcare_templates = loader.list_templates(tag="healthcare")
        assert "healthcare" in healthcare_templates
        assert "default" not in healthcare_templates

    def test_exists(self):
        """Test exists check."""
        loader = TemplateLoader()
        assert loader.exists("default") is True
        assert loader.exists("nonexistent") is False

    def test_get_info(self):
        """Test getting template info."""
        loader = TemplateLoader()
        info = loader.get_info("default")

        assert info.id == "default"
        assert info.source == "builtin"
        assert info.metadata.name == "Default Persona Generation"
        assert "count" in info.variables
        assert "data" in info.variables

    def test_get_info_not_found(self):
        """Test getting info for nonexistent template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = TemplateLoader(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
            )

            with pytest.raises(FileNotFoundError):
                loader.get_info("nonexistent")

    def test_load_template(self):
        """Test loading template content."""
        loader = TemplateLoader()
        content = loader.load("default")

        assert "{{ count }}" in content
        assert "{{ data }}" in content

    def test_load_template_not_found(self):
        """Test loading nonexistent template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = TemplateLoader(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
            )

            with pytest.raises(FileNotFoundError):
                loader.load("nonexistent")

    def test_get_variables(self):
        """Test getting template variables."""
        loader = TemplateLoader()
        variables = loader.get_variables("default")

        assert "count" in variables
        assert "data" in variables
        assert "complexity" in variables
        assert "detail_level" in variables

    def test_validate_template_valid(self):
        """Test validating template with valid variables."""
        loader = TemplateLoader()
        is_valid, errors = loader.validate_template(
            "default",
            count=3,
            data="Test data",
            complexity="moderate",
            detail_level="standard",
            include_reasoning=True,
        )

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_template_missing_vars(self):
        """Test validating template with missing variables."""
        loader = TemplateLoader()
        is_valid, errors = loader.validate_template(
            "default",
            count=3,
        )

        assert is_valid is False
        assert any("Missing variables" in e for e in errors)

    def test_save_template(self):
        """Test saving a template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"

            loader = TemplateLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            content = "{{ data }}"
            path = loader.save("new-template", content, user_level=True)

            assert path == user_dir / "new-template.j2"
            assert path.exists()

    def test_save_template_exists(self):
        """Test saving template that already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "existing.j2").write_text("old content")

            loader = TemplateLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            with pytest.raises(FileExistsError):
                loader.save("existing", "new content", user_level=True)

    def test_save_template_overwrite(self):
        """Test saving template with overwrite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "existing.j2").write_text("old content")

            loader = TemplateLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            loader.save("existing", "new content", user_level=True, overwrite=True)

            content = (user_dir / "existing.j2").read_text()
            assert content == "new content"

    def test_delete_template(self):
        """Test deleting a template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "to-delete.j2").write_text("content")

            loader = TemplateLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            assert loader.exists("to-delete")
            result = loader.delete("to-delete")
            assert result is True
            assert not loader.exists("to-delete")

    def test_delete_builtin_template(self):
        """Test cannot delete built-in template."""
        loader = TemplateLoader()
        result = loader.delete("default")
        assert result is False
        assert loader.exists("default")

    def test_export_template(self):
        """Test exporting a template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "exported.j2"

            loader = TemplateLoader()
            result = loader.export_template("default", output_path)

            assert result == output_path
            assert output_path.exists()
            content = output_path.read_text()
            assert "{{ count }}" in content

    def test_import_template(self):
        """Test importing a template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source file
            source_path = Path(tmpdir) / "source.j2"
            source_path.write_text("{{ imported }}")

            user_dir = Path(tmpdir) / "user"

            loader = TemplateLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            imported_id = loader.import_template(source_path)
            assert imported_id == "source"
            assert loader.exists("source")

    def test_import_template_custom_id(self):
        """Test importing template with custom ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source.j2"
            source_path.write_text("{{ data }}")

            user_dir = Path(tmpdir) / "user"

            loader = TemplateLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            imported_id = loader.import_template(source_path, template_id="custom-id")
            assert imported_id == "custom-id"
            assert loader.exists("custom-id")

    def test_project_templates_override_user(self):
        """Test project templates override user templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "override.j2").write_text("user version")

            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()
            (project_dir / "override.j2").write_text("project version")

            loader = TemplateLoader(
                user_dir=user_dir,
                project_dir=project_dir,
            )

            info = loader.get_info("override")
            assert info.source == "project"
            content = loader.load("override")
            assert content == "project version"


class TestGetBuiltinTemplates:
    """Tests for get_builtin_templates function."""

    def test_returns_builtin_templates(self):
        """Test returns only built-in templates."""
        templates = get_builtin_templates()

        assert "default" in templates
        assert "healthcare" in templates

        for template_id, info in templates.items():
            assert info.source == "builtin"

    def test_templates_have_metadata(self):
        """Test built-in templates have proper metadata."""
        templates = get_builtin_templates()

        default = templates["default"]
        assert default.metadata.name == "Default Persona Generation"
        assert len(default.variables) > 0
