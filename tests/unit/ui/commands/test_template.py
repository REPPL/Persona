"""Tests for template CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from persona.ui.cli import app
from persona.core.config.template import TemplateLoader

runner = CliRunner()


class TestTemplateList:
    """Tests for template list command."""

    def test_list_builtin_templates(self):
        """Test listing built-in templates."""
        result = runner.invoke(app, ["template", "list"])

        assert result.exit_code == 0
        assert "Built-in Templates" in result.output
        assert "default" in result.output

    def test_list_filter_by_source(self):
        """Test listing filtered by source."""
        result = runner.invoke(app, ["template", "list", "--source", "builtin"])

        assert result.exit_code == 0
        assert "default" in result.output

    def test_list_filter_by_tag(self):
        """Test listing filtered by tag."""
        result = runner.invoke(app, ["template", "list", "--tag", "healthcare"])

        assert result.exit_code == 0
        assert "healthcare" in result.output

    def test_list_json_output(self):
        """Test listing with JSON output."""
        result = runner.invoke(app, ["template", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["command"] == "template list"
        assert "templates" in data["data"]

    def test_list_no_custom_templates(self):
        """Test listing with no custom templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, ["template", "list", "--source", "user"])

                    assert result.exit_code == 0
                    # Should show no user templates


class TestTemplateShow:
    """Tests for template show command."""

    def test_show_builtin_template(self):
        """Test showing a built-in template."""
        result = runner.invoke(app, ["template", "show", "default"])

        assert result.exit_code == 0
        assert "Default Persona Generation" in result.output
        assert "Variables" in result.output

    def test_show_with_content(self):
        """Test showing template with content."""
        result = runner.invoke(app, ["template", "show", "default", "--content"])

        assert result.exit_code == 0
        assert "{{ count }}" in result.output or "count" in result.output

    def test_show_not_found(self):
        """Test showing nonexistent template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, ["template", "show", "nonexistent"])

                    assert result.exit_code == 1
                    assert "not found" in result.output.lower()

    def test_show_json_output(self):
        """Test showing template with JSON output."""
        result = runner.invoke(app, ["template", "show", "default", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["id"] == "default"
        assert "content" in data["data"]


class TestTemplateCreate:
    """Tests for template create command."""

    def test_create_template(self):
        """Test creating a new template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"

            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, [
                        "template", "create", "new-template",
                        "--name", "New Template",
                    ])

                    assert result.exit_code == 0
                    assert "created" in result.output.lower()
                    assert (user_dir / "new-template.j2").exists()

    def test_create_template_based_on(self):
        """Test creating template based on another."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"

            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, [
                        "template", "create", "my-healthcare",
                        "--name", "My Healthcare",
                        "--based-on", "healthcare",
                    ])

                    assert result.exit_code == 0
                    assert (user_dir / "my-healthcare.j2").exists()

    def test_create_template_already_exists(self):
        """Test creating template that already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "existing.j2").write_text("content")

            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, [
                        "template", "create", "existing",
                        "--name", "Existing",
                    ])

                    assert result.exit_code == 1
                    assert "already exists" in result.output.lower()

    def test_create_template_force_overwrite(self):
        """Test creating template with force overwrite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "existing.j2").write_text("old content")

            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, [
                        "template", "create", "existing",
                        "--name", "Updated",
                        "--force",
                    ])

                    assert result.exit_code == 0

    def test_create_template_project_level(self):
        """Test creating template at project level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "project"

            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", project_dir):
                    result = runner.invoke(app, [
                        "template", "create", "project-template",
                        "--name", "Project Template",
                        "--project",
                    ])

                    assert result.exit_code == 0
                    assert (project_dir / "project-template.j2").exists()


class TestTemplateTest:
    """Tests for template test command."""

    def test_test_template_valid(self):
        """Test testing a valid template."""
        result = runner.invoke(app, ["template", "test", "default"])

        assert result.exit_code == 0
        assert "validation passed" in result.output.lower()

    def test_test_template_custom_vars(self):
        """Test testing template with custom variables."""
        result = runner.invoke(app, [
            "template", "test", "default",
            "--count", "5",
            "--complexity", "complex",
        ])

        assert result.exit_code == 0
        assert "validation passed" in result.output.lower()

    def test_test_template_not_found(self):
        """Test testing nonexistent template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, ["template", "test", "nonexistent"])

                    assert result.exit_code == 1


class TestTemplateExport:
    """Tests for template export command."""

    def test_export_template(self):
        """Test exporting a template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "exported.j2"

            result = runner.invoke(app, [
                "template", "export", "default",
                "--output", str(output_path),
            ])

            assert result.exit_code == 0
            assert "exported" in result.output.lower()
            assert output_path.exists()

    def test_export_template_not_found(self):
        """Test exporting nonexistent template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "exported.j2"

            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, [
                        "template", "export", "nonexistent",
                        "--output", str(output_path),
                    ])

                    assert result.exit_code == 1


class TestTemplateImport:
    """Tests for template import command."""

    def test_import_template(self):
        """Test importing a template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source.j2"
            source_path.write_text("{{ data }}")
            user_dir = Path(tmpdir) / "user"

            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, [
                        "template", "import", str(source_path),
                    ])

                    assert result.exit_code == 0
                    assert "imported" in result.output.lower()
                    assert (user_dir / "source.j2").exists()

    def test_import_template_custom_id(self):
        """Test importing template with custom ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source.j2"
            source_path.write_text("{{ data }}")
            user_dir = Path(tmpdir) / "user"

            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, [
                        "template", "import", str(source_path),
                        "--id", "custom-id",
                    ])

                    assert result.exit_code == 0
                    assert "custom-id" in result.output
                    assert (user_dir / "custom-id.j2").exists()

    def test_import_template_not_found(self):
        """Test importing nonexistent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, [
                "template", "import", "/nonexistent/path.j2",
            ])

            assert result.exit_code == 1
            assert "not found" in result.output.lower()


class TestTemplateRemove:
    """Tests for template remove command."""

    def test_remove_template_with_force(self):
        """Test removing template with force flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "to-remove.j2").write_text("content")

            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, [
                        "template", "remove", "to-remove", "--force"
                    ])

                    assert result.exit_code == 0
                    assert "removed" in result.output.lower()
                    assert not (user_dir / "to-remove.j2").exists()

    def test_remove_template_not_found(self):
        """Test removing nonexistent template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(TemplateLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"):
                with patch.object(TemplateLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"):
                    result = runner.invoke(app, [
                        "template", "remove", "nonexistent", "--force"
                    ])

                    assert result.exit_code == 1
                    assert "not found" in result.output.lower()

    def test_remove_builtin_template(self):
        """Test cannot remove built-in template."""
        result = runner.invoke(app, [
            "template", "remove", "default", "--force"
        ])

        assert result.exit_code == 1
        assert "cannot remove" in result.output.lower() or "built-in" in result.output.lower()
