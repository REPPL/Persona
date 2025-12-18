"""Tests for vendor CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from persona.core.config.vendor import AuthType, VendorConfig
from persona.ui.cli import app
from typer.testing import CliRunner

runner = CliRunner()


class TestVendorList:
    """Tests for vendor list command."""

    def test_list_no_custom_vendors(self):
        """Test listing with no custom vendors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR",
                Path(tmpdir) / "user",
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(app, ["vendor", "list"])

                    assert result.exit_code == 0
                    assert "Built-in Providers" in result.output
                    assert "anthropic" in result.output
                    assert "No custom vendors" in result.output

    def test_list_with_custom_vendors(self):
        """Test listing with custom vendors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="test-vendor",
                name="Test Vendor",
                api_base="https://api.example.com",
                auth_type=AuthType.NONE,
            )
            config.to_yaml(user_dir / "test-vendor.yaml")

            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR", user_dir
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    # Clear the factory cache
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(app, ["vendor", "list"])

                    assert result.exit_code == 0
                    assert "test-vendor" in result.output

    def test_list_json_output(self):
        """Test listing with JSON output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR",
                Path(tmpdir) / "user",
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(app, ["vendor", "list", "--json"])

                    assert result.exit_code == 0
                    data = json.loads(result.output)
                    assert data["command"] == "vendor list"
                    assert "builtin" in data["data"]


class TestVendorShow:
    """Tests for vendor show command."""

    def test_show_custom_vendor(self):
        """Test showing a custom vendor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="show-test",
                name="Show Test Vendor",
                api_base="https://api.example.com",
                default_model="gpt-4",
            )
            config.to_yaml(user_dir / "show-test.yaml")

            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR", user_dir
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(app, ["vendor", "show", "show-test"])

                    assert result.exit_code == 0
                    assert "Show Test Vendor" in result.output
                    assert "https://api.example.com" in result.output

    def test_show_not_found(self):
        """Test showing nonexistent vendor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR",
                Path(tmpdir) / "user",
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(app, ["vendor", "show", "nonexistent"])

                    assert result.exit_code == 1
                    assert "not found" in result.output.lower()

    def test_show_json_output(self):
        """Test showing vendor with JSON output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="json-test",
                name="JSON Test",
                api_base="https://api.example.com",
            )
            config.to_yaml(user_dir / "json-test.yaml")

            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR", user_dir
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(
                        app, ["vendor", "show", "json-test", "--json"]
                    )

                    assert result.exit_code == 0
                    data = json.loads(result.output)
                    assert data["data"]["id"] == "json-test"


class TestVendorAdd:
    """Tests for vendor add command."""

    def test_add_vendor(self):
        """Test adding a new vendor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            project_dir = Path(tmpdir) / "project"

            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR", user_dir
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    project_dir,
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(
                        app,
                        [
                            "vendor",
                            "add",
                            "new-vendor",
                            "--name",
                            "New Vendor",
                            "--api-base",
                            "https://api.example.com",
                        ],
                    )

                    assert result.exit_code == 0
                    assert "added" in result.output.lower()
                    assert (user_dir / "new-vendor.yaml").exists()

    def test_add_vendor_with_all_options(self):
        """Test adding vendor with all options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"

            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR", user_dir
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(
                        app,
                        [
                            "vendor",
                            "add",
                            "full-vendor",
                            "--name",
                            "Full Vendor",
                            "--api-base",
                            "https://api.example.com",
                            "--api-version",
                            "2024-01-01",
                            "--auth-type",
                            "header",
                            "--auth-env",
                            "MY_API_KEY",
                            "--default-model",
                            "gpt-4",
                            "--models",
                            "gpt-4,gpt-3.5-turbo",
                        ],
                    )

                    assert result.exit_code == 0

                    # Verify config
                    config = VendorConfig.from_yaml(user_dir / "full-vendor.yaml")
                    assert config.api_version == "2024-01-01"
                    assert config.auth_type == "header"
                    assert len(config.models) == 2

    def test_add_vendor_already_exists(self):
        """Test adding vendor that already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="existing",
                name="Existing",
                api_base="https://api.example.com",
            )
            config.to_yaml(user_dir / "existing.yaml")

            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR", user_dir
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(
                        app,
                        [
                            "vendor",
                            "add",
                            "existing",
                            "--name",
                            "Updated",
                            "--api-base",
                            "https://new.example.com",
                        ],
                    )

                    assert result.exit_code == 1
                    assert "already exists" in result.output.lower()

    def test_add_vendor_force_overwrite(self):
        """Test adding vendor with force overwrite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="overwrite",
                name="Original",
                api_base="https://original.example.com",
            )
            config.to_yaml(user_dir / "overwrite.yaml")

            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR", user_dir
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(
                        app,
                        [
                            "vendor",
                            "add",
                            "overwrite",
                            "--name",
                            "Updated",
                            "--api-base",
                            "https://updated.example.com",
                            "--force",
                        ],
                    )

                    assert result.exit_code == 0

                    # Verify updated
                    updated = VendorConfig.from_yaml(user_dir / "overwrite.yaml")
                    assert updated.name == "Updated"

    def test_add_vendor_invalid_auth_type(self):
        """Test adding vendor with invalid auth type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR",
                Path(tmpdir) / "user",
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    result = runner.invoke(
                        app,
                        [
                            "vendor",
                            "add",
                            "invalid",
                            "--name",
                            "Invalid",
                            "--api-base",
                            "https://api.example.com",
                            "--auth-type",
                            "invalid",
                        ],
                    )

                    assert result.exit_code == 1
                    assert "invalid auth type" in result.output.lower()

    def test_add_vendor_project_level(self):
        """Test adding vendor at project level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            project_dir = Path(tmpdir) / "project"

            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR", user_dir
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    project_dir,
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(
                        app,
                        [
                            "vendor",
                            "add",
                            "project-vendor",
                            "--name",
                            "Project Vendor",
                            "--api-base",
                            "https://api.example.com",
                            "--project",
                        ],
                    )

                    assert result.exit_code == 0
                    assert (project_dir / "project-vendor.yaml").exists()
                    assert not (user_dir / "project-vendor.yaml").exists()


class TestVendorRemove:
    """Tests for vendor remove command."""

    def test_remove_vendor_with_confirm(self):
        """Test removing vendor with confirmation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="to-remove",
                name="To Remove",
                api_base="https://api.example.com",
            )
            config.to_yaml(user_dir / "to-remove.yaml")

            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR", user_dir
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(
                        app, ["vendor", "remove", "to-remove", "--force"]
                    )

                    assert result.exit_code == 0
                    assert "removed" in result.output.lower()
                    assert not (user_dir / "to-remove.yaml").exists()

    def test_remove_vendor_not_found(self):
        """Test removing nonexistent vendor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR",
                Path(tmpdir) / "user",
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(
                        app, ["vendor", "remove", "nonexistent", "--force"]
                    )

                    assert result.exit_code == 1
                    assert "not found" in result.output.lower()


class TestVendorTest:
    """Tests for vendor test command."""

    def test_test_builtin_provider(self):
        """Test testing a built-in provider."""
        result = runner.invoke(app, ["vendor", "test", "anthropic"])

        assert result.exit_code == 0
        # Will show configured or not configured based on env

    def test_test_custom_vendor(self):
        """Test testing a custom vendor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="test-custom",
                name="Test Custom",
                api_base="https://api.example.com",
                auth_type=AuthType.NONE,
            )
            config.to_yaml(user_dir / "test-custom.yaml")

            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR", user_dir
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(app, ["vendor", "test", "test-custom"])

                    # Will fail connection but should run
                    assert result.exit_code == 0

    def test_test_vendor_not_found(self):
        """Test testing nonexistent vendor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "persona.core.config.vendor.VendorLoader.DEFAULT_USER_DIR",
                Path(tmpdir) / "user",
            ):
                with patch(
                    "persona.core.config.vendor.VendorLoader.DEFAULT_PROJECT_DIR",
                    Path(tmpdir) / "project",
                ):
                    from persona.core.providers.factory import ProviderFactory

                    ProviderFactory.clear_vendor_cache()

                    result = runner.invoke(app, ["vendor", "test", "nonexistent"])

                    assert result.exit_code == 1

    def test_test_vendor_json_output(self):
        """Test testing vendor with JSON output."""
        result = runner.invoke(app, ["vendor", "test", "anthropic", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "configured" in data or "vendor" in data
