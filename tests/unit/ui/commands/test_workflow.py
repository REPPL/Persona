"""Tests for workflow CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from persona.core.config.workflow import CustomWorkflowLoader
from persona.ui.cli import app
from typer.testing import CliRunner

runner = CliRunner()


class TestWorkflowList:
    """Tests for workflow list command."""

    def test_list_builtin_workflows(self):
        """Test listing built-in workflows."""
        result = runner.invoke(app, ["workflow", "list"])

        assert result.exit_code == 0
        assert "Built-in Workflows" in result.output
        assert "default" in result.output

    def test_list_filter_by_source(self):
        """Test listing filtered by source."""
        result = runner.invoke(app, ["workflow", "list", "--source", "builtin"])

        assert result.exit_code == 0
        assert "default" in result.output

    def test_list_filter_by_tag(self):
        """Test listing filtered by tag."""
        result = runner.invoke(app, ["workflow", "list", "--tag", "healthcare"])

        assert result.exit_code == 0
        assert "healthcare" in result.output

    def test_list_json_output(self):
        """Test listing with JSON output."""
        result = runner.invoke(app, ["workflow", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["command"] == "workflow list"
        assert "workflows" in data["data"]

    def test_list_with_custom_workflows(self):
        """Test listing with custom workflows."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "custom.yaml").write_text(
                """
id: custom-workflow
name: Custom Workflow
steps:
  - name: step
    template: t
"""
            )

            with patch.object(CustomWorkflowLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    CustomWorkflowLoader,
                    "DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(app, ["workflow", "list"])

                    assert result.exit_code == 0
                    assert "custom-workflow" in result.output


class TestWorkflowShow:
    """Tests for workflow show command."""

    def test_show_builtin_workflow(self):
        """Test showing a built-in workflow."""
        result = runner.invoke(app, ["workflow", "show", "default"])

        assert result.exit_code == 0
        assert "Default Workflow" in result.output
        assert "Steps" in result.output

    def test_show_not_found(self):
        """Test showing nonexistent workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                CustomWorkflowLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"
            ):
                with patch.object(
                    CustomWorkflowLoader,
                    "DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(app, ["workflow", "show", "nonexistent"])

                    assert result.exit_code == 1
                    assert "not found" in result.output.lower()

    def test_show_json_output(self):
        """Test showing workflow with JSON output."""
        result = runner.invoke(app, ["workflow", "show", "default", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["id"] == "default"
        assert "steps" in data["data"]


class TestWorkflowCreate:
    """Tests for workflow create command."""

    def test_create_workflow(self):
        """Test creating a new workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"

            with patch.object(CustomWorkflowLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    CustomWorkflowLoader,
                    "DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(
                        app,
                        [
                            "workflow",
                            "create",
                            "new-workflow",
                            "--name",
                            "New Workflow",
                        ],
                    )

                    assert result.exit_code == 0
                    assert "created" in result.output.lower()
                    assert (user_dir / "new-workflow.yaml").exists()

    def test_create_workflow_with_options(self):
        """Test creating workflow with options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"

            with patch.object(CustomWorkflowLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    CustomWorkflowLoader,
                    "DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(
                        app,
                        [
                            "workflow",
                            "create",
                            "custom",
                            "--name",
                            "Custom",
                            "--provider",
                            "openai",
                            "--template",
                            "builtin/healthcare",
                            "--tags",
                            "custom,test",
                        ],
                    )

                    assert result.exit_code == 0
                    assert (user_dir / "custom.yaml").exists()

    def test_create_workflow_already_exists(self):
        """Test creating workflow that already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "existing.yaml").write_text("id: existing\nname: E")

            with patch.object(CustomWorkflowLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    CustomWorkflowLoader,
                    "DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(
                        app,
                        [
                            "workflow",
                            "create",
                            "existing",
                            "--name",
                            "Updated",
                        ],
                    )

                    assert result.exit_code == 1
                    assert "already exists" in result.output.lower()

    def test_create_workflow_force_overwrite(self):
        """Test creating workflow with force overwrite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "existing.yaml").write_text("id: existing\nname: Old")

            with patch.object(CustomWorkflowLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    CustomWorkflowLoader,
                    "DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(
                        app,
                        [
                            "workflow",
                            "create",
                            "existing",
                            "--name",
                            "Updated",
                            "--force",
                        ],
                    )

                    assert result.exit_code == 0

    def test_create_workflow_project_level(self):
        """Test creating workflow at project level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "project"

            with patch.object(
                CustomWorkflowLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"
            ):
                with patch.object(
                    CustomWorkflowLoader, "DEFAULT_PROJECT_DIR", project_dir
                ):
                    result = runner.invoke(
                        app,
                        [
                            "workflow",
                            "create",
                            "project-workflow",
                            "--name",
                            "Project Workflow",
                            "--project",
                        ],
                    )

                    assert result.exit_code == 0
                    assert (project_dir / "project-workflow.yaml").exists()


class TestWorkflowValidate:
    """Tests for workflow validate command."""

    def test_validate_workflow_valid(self):
        """Test validating a valid workflow."""
        result = runner.invoke(app, ["workflow", "validate", "default"])

        assert result.exit_code == 0
        assert "validation passed" in result.output.lower()

    def test_validate_workflow_not_found(self):
        """Test validating nonexistent workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                CustomWorkflowLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"
            ):
                with patch.object(
                    CustomWorkflowLoader,
                    "DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(app, ["workflow", "validate", "nonexistent"])

                    assert result.exit_code == 1


class TestWorkflowRemove:
    """Tests for workflow remove command."""

    def test_remove_workflow_with_force(self):
        """Test removing workflow with force flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "to-remove.yaml").write_text("id: to-remove\nname: R")

            with patch.object(CustomWorkflowLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    CustomWorkflowLoader,
                    "DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(
                        app, ["workflow", "remove", "to-remove", "--force"]
                    )

                    assert result.exit_code == 0
                    assert "removed" in result.output.lower()
                    assert not (user_dir / "to-remove.yaml").exists()

    def test_remove_workflow_not_found(self):
        """Test removing nonexistent workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                CustomWorkflowLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"
            ):
                with patch.object(
                    CustomWorkflowLoader,
                    "DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(
                        app, ["workflow", "remove", "nonexistent", "--force"]
                    )

                    assert result.exit_code == 1
                    assert "not found" in result.output.lower()

    def test_remove_builtin_workflow(self):
        """Test cannot remove built-in workflow."""
        result = runner.invoke(app, ["workflow", "remove", "default", "--force"])

        assert result.exit_code == 1
        assert (
            "cannot remove" in result.output.lower()
            or "built-in" in result.output.lower()
        )
