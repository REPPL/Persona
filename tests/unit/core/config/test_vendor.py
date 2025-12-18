"""Tests for custom vendor configuration."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from persona.core.config.vendor import (
    AuthType,
    VendorConfig,
    VendorEndpoints,
    VendorLoader,
)


class TestAuthType:
    """Tests for AuthType enum."""

    def test_all_auth_types(self):
        """Test all authentication types exist."""
        assert AuthType.BEARER == "bearer"
        assert AuthType.HEADER == "header"
        assert AuthType.QUERY == "query"
        assert AuthType.NONE == "none"

    def test_string_conversion(self):
        """Test enum can be used as string."""
        assert str(AuthType.BEARER) == "AuthType.BEARER"
        assert AuthType.BEARER.value == "bearer"


class TestVendorEndpoints:
    """Tests for VendorEndpoints model."""

    def test_default_endpoints(self):
        """Test default endpoint values."""
        endpoints = VendorEndpoints()
        assert endpoints.chat == "/v1/chat/completions"
        assert endpoints.models is None

    def test_custom_endpoints(self):
        """Test custom endpoint values."""
        endpoints = VendorEndpoints(
            chat="/openai/deployments/{deployment}/chat/completions",
            models="/openai/models",
        )
        assert "{deployment}" in endpoints.chat
        assert endpoints.models == "/openai/models"


class TestVendorConfig:
    """Tests for VendorConfig model."""

    def test_minimal_config(self):
        """Test minimal valid configuration."""
        config = VendorConfig(
            id="test-vendor",
            name="Test Vendor",
            api_base="https://api.example.com",
        )
        assert config.id == "test-vendor"
        assert config.name == "Test Vendor"
        assert config.api_base == "https://api.example.com"

    def test_full_config(self):
        """Test full configuration with all fields."""
        config = VendorConfig(
            id="azure-openai",
            name="Azure OpenAI",
            api_base="https://my-deployment.openai.azure.com",
            api_version="2024-02-15-preview",
            auth_type=AuthType.HEADER,
            auth_env="AZURE_OPENAI_API_KEY",
            auth_header="api-key",
            endpoints=VendorEndpoints(
                chat="/openai/deployments/{deployment}/chat/completions"
            ),
            headers={"api-key": "${AZURE_OPENAI_API_KEY}"},
            default_model="gpt-4",
            models=["gpt-4", "gpt-4-turbo"],
            timeout=60,
            request_format="openai",
            response_format="openai",
        )
        assert config.api_version == "2024-02-15-preview"
        assert config.auth_type == "header"
        assert len(config.models) == 2

    def test_id_validation_lowercase(self):
        """Test vendor ID must be lowercase."""
        with pytest.raises(ValueError) as exc_info:
            VendorConfig(
                id="Test-Vendor",
                name="Test",
                api_base="https://api.example.com",
            )
        assert "lowercase" in str(exc_info.value).lower()

    def test_id_validation_no_start_hyphen(self):
        """Test vendor ID cannot start with hyphen."""
        with pytest.raises(ValueError):
            VendorConfig(
                id="-test",
                name="Test",
                api_base="https://api.example.com",
            )

    def test_id_validation_no_end_hyphen(self):
        """Test vendor ID cannot end with hyphen."""
        with pytest.raises(ValueError):
            VendorConfig(
                id="test-",
                name="Test",
                api_base="https://api.example.com",
            )

    def test_id_validation_single_char(self):
        """Test single character vendor ID is valid."""
        config = VendorConfig(
            id="a",
            name="A",
            api_base="https://api.example.com",
        )
        assert config.id == "a"

    def test_api_base_validation_http(self):
        """Test API base must be http or https."""
        with pytest.raises(ValueError) as exc_info:
            VendorConfig(
                id="test",
                name="Test",
                api_base="ftp://api.example.com",
            )
        assert "http" in str(exc_info.value).lower()

    def test_api_base_trailing_slash_removed(self):
        """Test trailing slash is removed from API base."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com/",
        )
        assert config.api_base == "https://api.example.com"


class TestVendorConfigAuth:
    """Tests for VendorConfig authentication methods."""

    def test_get_auth_value_from_env(self):
        """Test getting auth value from environment."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_env="TEST_API_KEY",
        )

        with patch.dict(os.environ, {"TEST_API_KEY": "secret123"}):
            assert config.get_auth_value() == "secret123"

    def test_get_auth_value_not_set(self):
        """Test getting auth value when not set."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_env="NONEXISTENT_KEY",
        )

        assert config.get_auth_value() is None

    def test_is_configured_with_auth(self):
        """Test is_configured when auth is set."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_env="TEST_KEY",
        )

        with patch.dict(os.environ, {"TEST_KEY": "key"}):
            assert config.is_configured() is True

    def test_is_configured_without_auth(self):
        """Test is_configured when auth is not set."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_env="NONEXISTENT_KEY",
        )

        assert config.is_configured() is False

    def test_is_configured_no_auth_required(self):
        """Test is_configured when no auth is required."""
        config = VendorConfig(
            id="local",
            name="Local",
            api_base="http://localhost:8080",
            auth_type=AuthType.NONE,
        )

        assert config.is_configured() is True

    def test_resolve_headers_with_env(self):
        """Test resolving headers with environment variables."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            headers={
                "Authorization": "Bearer ${TEST_TOKEN}",
                "X-Custom": "static-value",
            },
        )

        with patch.dict(os.environ, {"TEST_TOKEN": "my-token"}):
            headers = config.resolve_headers()
            assert headers["Authorization"] == "Bearer my-token"
            assert headers["X-Custom"] == "static-value"

    def test_resolve_headers_missing_env(self):
        """Test resolving headers with missing environment variable."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            headers={"Authorization": "Bearer ${MISSING_VAR}"},
        )

        headers = config.resolve_headers()
        assert headers["Authorization"] == "Bearer "


class TestVendorConfigUrl:
    """Tests for VendorConfig URL building."""

    def test_build_url_basic(self):
        """Test basic URL building."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
        )

        url = config.build_url("chat")
        assert url == "https://api.example.com/v1/chat/completions"

    def test_build_url_with_variables(self):
        """Test URL building with variable substitution."""
        config = VendorConfig(
            id="azure",
            name="Azure",
            api_base="https://my.openai.azure.com",
            endpoints=VendorEndpoints(
                chat="/openai/deployments/{deployment}/chat/completions"
            ),
        )

        url = config.build_url("chat", deployment="gpt-4")
        assert (
            url
            == "https://my.openai.azure.com/openai/deployments/gpt-4/chat/completions"
        )

    def test_build_url_with_api_version(self):
        """Test URL building with API version."""
        config = VendorConfig(
            id="azure",
            name="Azure",
            api_base="https://my.openai.azure.com",
            api_version="2024-02-15",
        )

        url = config.build_url("chat")
        assert "api-version=2024-02-15" in url

    def test_build_headers_bearer(self):
        """Test building headers with bearer auth."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_type=AuthType.BEARER,
            auth_env="TEST_KEY",
        )

        with patch.dict(os.environ, {"TEST_KEY": "my-key"}):
            headers = config.build_headers()
            assert headers["Authorization"] == "Bearer my-key"

    def test_build_headers_header_auth(self):
        """Test building headers with header auth."""
        config = VendorConfig(
            id="azure",
            name="Azure",
            api_base="https://api.example.com",
            auth_type=AuthType.HEADER,
            auth_env="AZURE_KEY",
            auth_header="api-key",
        )

        with patch.dict(os.environ, {"AZURE_KEY": "azure-key"}):
            headers = config.build_headers()
            assert headers["api-key"] == "azure-key"


class TestVendorConfigYaml:
    """Tests for VendorConfig YAML serialisation."""

    def test_from_yaml(self):
        """Test loading config from YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(
                {
                    "id": "test-vendor",
                    "name": "Test Vendor",
                    "api_base": "https://api.example.com",
                    "auth_type": "bearer",
                    "auth_env": "TEST_API_KEY",
                },
                f,
            )
            f.flush()

            config = VendorConfig.from_yaml(Path(f.name))

            assert config.id == "test-vendor"
            assert config.name == "Test Vendor"
            assert config.auth_type == "bearer"

            Path(f.name).unlink()

    def test_from_yaml_not_found(self):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            VendorConfig.from_yaml(Path("/nonexistent/path.yaml"))

    def test_to_yaml(self):
        """Test saving config to YAML file."""
        config = VendorConfig(
            id="test-vendor",
            name="Test Vendor",
            api_base="https://api.example.com",
            auth_env="TEST_KEY",
            models=["model-a", "model-b"],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.yaml"
            config.to_yaml(path)

            assert path.exists()

            # Verify content
            with open(path) as f:
                data = yaml.safe_load(f)

            assert data["id"] == "test-vendor"
            assert data["models"] == ["model-a", "model-b"]

    def test_yaml_round_trip(self):
        """Test config survives YAML round trip."""
        original = VendorConfig(
            id="round-trip",
            name="Round Trip Test",
            api_base="https://api.example.com",
            api_version="v1",
            auth_type=AuthType.HEADER,
            auth_env="RT_KEY",
            default_model="default",
            models=["model-1", "model-2"],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.yaml"
            original.to_yaml(path)
            loaded = VendorConfig.from_yaml(path)

            assert loaded.id == original.id
            assert loaded.api_version == original.api_version
            assert loaded.models == original.models


class TestVendorLoader:
    """Tests for VendorLoader."""

    def test_default_search_paths(self):
        """Test default search paths."""
        loader = VendorLoader()
        assert loader._user_dir == Path.home() / ".persona" / "vendors"
        assert loader._project_dir == Path(".persona") / "vendors"

    def test_custom_search_paths(self):
        """Test custom search paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            project_dir = Path(tmpdir) / "project"

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=project_dir,
            )

            assert loader._user_dir == user_dir
            assert loader._project_dir == project_dir

    def test_list_vendors_empty(self):
        """Test listing vendors with no configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = VendorLoader(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
            )
            assert loader.list_vendors() == []

    def test_list_vendors_with_configs(self):
        """Test listing vendors with configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            # Create vendor configs
            for vendor_id in ["vendor-a", "vendor-b"]:
                config = VendorConfig(
                    id=vendor_id,
                    name=f"Vendor {vendor_id}",
                    api_base="https://api.example.com",
                )
                config.to_yaml(user_dir / f"{vendor_id}.yaml")

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            vendors = loader.list_vendors()
            assert "vendor-a" in vendors
            assert "vendor-b" in vendors

    def test_load_vendor(self):
        """Test loading a vendor config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="test-vendor",
                name="Test Vendor",
                api_base="https://api.example.com",
            )
            config.to_yaml(user_dir / "test-vendor.yaml")

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            loaded = loader.load("test-vendor")
            assert loaded.id == "test-vendor"
            assert loaded.name == "Test Vendor"

    def test_load_vendor_not_found(self):
        """Test loading nonexistent vendor raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = VendorLoader(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
            )

            with pytest.raises(FileNotFoundError):
                loader.load("nonexistent")

    def test_load_vendor_caching(self):
        """Test vendor configs are cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="cached",
                name="Cached",
                api_base="https://api.example.com",
            )
            config.to_yaml(user_dir / "cached.yaml")

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            # Load twice
            first = loader.load("cached")
            second = loader.load("cached")

            assert first is second  # Same object from cache

    def test_save_vendor_user_level(self):
        """Test saving vendor at user level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            project_dir = Path(tmpdir) / "project"

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=project_dir,
            )

            config = VendorConfig(
                id="saved",
                name="Saved",
                api_base="https://api.example.com",
            )

            path = loader.save(config, user_level=True)

            assert path == user_dir / "saved.yaml"
            assert path.exists()

    def test_save_vendor_project_level(self):
        """Test saving vendor at project level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            project_dir = Path(tmpdir) / "project"

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=project_dir,
            )

            config = VendorConfig(
                id="project-saved",
                name="Project Saved",
                api_base="https://api.example.com",
            )

            path = loader.save(config, user_level=False)

            assert path == project_dir / "project-saved.yaml"
            assert path.exists()

    def test_delete_vendor(self):
        """Test deleting a vendor config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="to-delete",
                name="To Delete",
                api_base="https://api.example.com",
            )
            config.to_yaml(user_dir / "to-delete.yaml")

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            assert loader.exists("to-delete")

            result = loader.delete("to-delete")

            assert result is True
            assert not loader.exists("to-delete")

    def test_delete_nonexistent(self):
        """Test deleting nonexistent vendor returns False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = VendorLoader(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
            )

            result = loader.delete("nonexistent")
            assert result is False

    def test_exists(self):
        """Test exists check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="exists",
                name="Exists",
                api_base="https://api.example.com",
            )
            config.to_yaml(user_dir / "exists.yaml")

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            assert loader.exists("exists") is True
            assert loader.exists("nonexistent") is False

    def test_clear_cache(self):
        """Test clearing the cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = VendorConfig(
                id="cached",
                name="Cached",
                api_base="https://api.example.com",
            )
            config.to_yaml(user_dir / "cached.yaml")

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            loader.load("cached")
            assert "cached" in loader._cache

            loader.clear_cache()
            assert loader._cache == {}

    def test_get_configured_vendors(self):
        """Test getting configured vendors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            # Create unconfigured vendor
            unconfigured = VendorConfig(
                id="unconfigured",
                name="Unconfigured",
                api_base="https://api.example.com",
                auth_env="NONEXISTENT_KEY",
            )
            unconfigured.to_yaml(user_dir / "unconfigured.yaml")

            # Create local vendor (no auth needed)
            local = VendorConfig(
                id="local",
                name="Local",
                api_base="http://localhost:8080",
                auth_type=AuthType.NONE,
            )
            local.to_yaml(user_dir / "local.yaml")

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            configured = loader.get_configured_vendors()
            assert "local" in configured
            assert "unconfigured" not in configured

    def test_project_overrides_user(self):
        """Test project-level config overrides user-level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            project_dir = Path(tmpdir) / "project"
            user_dir.mkdir()
            project_dir.mkdir()

            # Create user-level config
            user_config = VendorConfig(
                id="override",
                name="User Level",
                api_base="https://user.example.com",
            )
            user_config.to_yaml(user_dir / "override.yaml")

            # Create project-level config
            project_config = VendorConfig(
                id="override",
                name="Project Level",
                api_base="https://project.example.com",
            )
            project_config.to_yaml(project_dir / "override.yaml")

            loader = VendorLoader(
                user_dir=user_dir,
                project_dir=project_dir,
            )

            loaded = loader.load("override")
            # Project level should take precedence
            assert loaded.name == "Project Level"
            assert loaded.api_base == "https://project.example.com"
