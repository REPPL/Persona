"""Tests for model CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from persona.core.config.model import ModelConfig, ModelLoader
from persona.ui.cli import app
from typer.testing import CliRunner

runner = CliRunner()


class TestModelList:
    """Tests for model list command."""

    def test_list_builtin_models(self):
        """Test listing built-in models."""
        result = runner.invoke(app, ["model", "list"])

        assert result.exit_code == 0
        assert "Built-in Models" in result.output
        assert "openai" in result.output
        assert "anthropic" in result.output

    def test_list_no_custom_models(self):
        """Test listing with no custom models."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(ModelLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(app, ["model", "list"])

                    assert result.exit_code == 0
                    assert "No custom models" in result.output

    def test_list_with_custom_models(self):
        """Test listing with custom models."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(
                id="custom-model",
                name="Custom Model",
                provider="openai",
            )
            config.to_yaml(user_dir / "custom-model.yaml")

            with patch.object(ModelLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(app, ["model", "list"])

                    assert result.exit_code == 0
                    assert "custom-model" in result.output

    def test_list_filter_by_provider(self):
        """Test listing filtered by provider."""
        result = runner.invoke(app, ["model", "list", "--provider", "openai"])

        assert result.exit_code == 0
        assert "openai" in result.output

    def test_list_custom_only(self):
        """Test listing custom models only."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(ModelLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(app, ["model", "list", "--custom"])

                    assert result.exit_code == 0
                    # Should not show built-in models section prominently
                    assert "No custom models" in result.output

    def test_list_json_output(self):
        """Test listing with JSON output."""
        result = runner.invoke(app, ["model", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["command"] == "model list"
        assert "builtin" in data["data"]


class TestModelShow:
    """Tests for model show command."""

    def test_show_custom_model(self):
        """Test showing a custom model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(
                id="show-model",
                name="Show Model",
                provider="openai",
                context_window=128000,
                max_output=4096,
            )
            config.to_yaml(user_dir / "show-model.yaml")

            with patch.object(ModelLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(app, ["model", "show", "show-model"])

                    assert result.exit_code == 0
                    assert "Show Model" in result.output
                    assert "128,000" in result.output

    def test_show_not_found(self):
        """Test showing nonexistent model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(ModelLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(app, ["model", "show", "nonexistent"])

                    assert result.exit_code == 1
                    assert "not found" in result.output.lower()

    def test_show_json_output(self):
        """Test showing model with JSON output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(
                id="json-model",
                name="JSON Model",
                provider="openai",
            )
            config.to_yaml(user_dir / "json-model.yaml")

            with patch.object(ModelLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(
                        app, ["model", "show", "json-model", "--json"]
                    )

                    assert result.exit_code == 0
                    data = json.loads(result.output)
                    assert data["data"]["id"] == "json-model"


class TestModelAdd:
    """Tests for model add command."""

    def test_add_model(self):
        """Test adding a new model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            project_dir = Path(tmpdir) / "project"

            with patch.object(ModelLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(ModelLoader, "DEFAULT_PROJECT_DIR", project_dir):
                    result = runner.invoke(
                        app,
                        [
                            "model",
                            "add",
                            "new-model",
                            "--name",
                            "New Model",
                            "--provider",
                            "openai",
                        ],
                    )

                    assert result.exit_code == 0
                    assert "added" in result.output.lower()
                    assert (user_dir / "new-model.yaml").exists()

    def test_add_model_with_pricing(self):
        """Test adding model with pricing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"

            with patch.object(ModelLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(
                        app,
                        [
                            "model",
                            "add",
                            "priced-model",
                            "--name",
                            "Priced Model",
                            "--provider",
                            "openai",
                            "--input-price",
                            "3.00",
                            "--output-price",
                            "15.00",
                            "--context",
                            "128000",
                            "--max-output",
                            "8192",
                        ],
                    )

                    assert result.exit_code == 0

                    config = ModelConfig.from_yaml(user_dir / "priced-model.yaml")
                    assert float(config.pricing.input) == 3.0
                    assert float(config.pricing.output) == 15.0

    def test_add_model_already_exists(self):
        """Test adding model that already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(id="existing", name="Existing", provider="openai")
            config.to_yaml(user_dir / "existing.yaml")

            with patch.object(ModelLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(
                        app,
                        [
                            "model",
                            "add",
                            "existing",
                            "--name",
                            "Updated",
                            "--provider",
                            "openai",
                        ],
                    )

                    assert result.exit_code == 1
                    assert "already exists" in result.output.lower()

    def test_add_model_force_overwrite(self):
        """Test adding model with force overwrite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(id="overwrite", name="Original", provider="openai")
            config.to_yaml(user_dir / "overwrite.yaml")

            with patch.object(ModelLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(
                        app,
                        [
                            "model",
                            "add",
                            "overwrite",
                            "--name",
                            "Updated",
                            "--provider",
                            "openai",
                            "--force",
                        ],
                    )

                    assert result.exit_code == 0

                    updated = ModelConfig.from_yaml(user_dir / "overwrite.yaml")
                    assert updated.name == "Updated"

    def test_add_model_project_level(self):
        """Test adding model at project level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            project_dir = Path(tmpdir) / "project"

            with patch.object(ModelLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(ModelLoader, "DEFAULT_PROJECT_DIR", project_dir):
                    result = runner.invoke(
                        app,
                        [
                            "model",
                            "add",
                            "project-model",
                            "--name",
                            "Project Model",
                            "--provider",
                            "openai",
                            "--project",
                        ],
                    )

                    assert result.exit_code == 0
                    assert (project_dir / "project-model.yaml").exists()


class TestModelRemove:
    """Tests for model remove command."""

    def test_remove_model_with_force(self):
        """Test removing model with force flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(id="to-remove", name="Remove", provider="openai")
            config.to_yaml(user_dir / "to-remove.yaml")

            with patch.object(ModelLoader, "DEFAULT_USER_DIR", user_dir):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(
                        app, ["model", "remove", "to-remove", "--force"]
                    )

                    assert result.exit_code == 0
                    assert "removed" in result.output.lower()
                    assert not (user_dir / "to-remove.yaml").exists()

    def test_remove_model_not_found(self):
        """Test removing nonexistent model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(ModelLoader, "DEFAULT_USER_DIR", Path(tmpdir) / "user"):
                with patch.object(
                    ModelLoader, "DEFAULT_PROJECT_DIR", Path(tmpdir) / "project"
                ):
                    result = runner.invoke(
                        app, ["model", "remove", "nonexistent", "--force"]
                    )

                    assert result.exit_code == 1
                    assert "not found" in result.output.lower()


class TestModelPricing:
    """Tests for model pricing command."""

    def test_pricing_shows_models(self):
        """Test pricing shows available models."""
        result = runner.invoke(app, ["model", "pricing"])

        assert result.exit_code == 0
        assert "Model" in result.output
        assert "Input" in result.output
        assert "Output" in result.output

    def test_pricing_filter_by_provider(self):
        """Test pricing filtered by provider."""
        result = runner.invoke(app, ["model", "pricing", "--provider", "anthropic"])

        assert result.exit_code == 0
        # Should show anthropic models

    def test_pricing_json_output(self):
        """Test pricing with JSON output."""
        result = runner.invoke(app, ["model", "pricing", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "pricing" in data
        assert len(data["pricing"]) > 0
