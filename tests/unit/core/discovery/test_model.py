"""Tests for model discovery."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from persona.core.discovery.model import (
    ModelDiscovery,
    ModelStatus,
    ModelDiscoveryResult,
)


class TestModelStatus:
    """Tests for ModelStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert ModelStatus.AVAILABLE.value == "available"
        assert ModelStatus.DEPRECATED.value == "deprecated"
        assert ModelStatus.UNAVAILABLE.value == "unavailable"
        assert ModelStatus.UNKNOWN.value == "unknown"


class TestModelDiscoveryResult:
    """Tests for ModelDiscoveryResult dataclass."""

    def test_minimal_result(self):
        """Test minimal discovery result."""
        result = ModelDiscoveryResult(
            model_id="gpt-4",
            status=ModelStatus.AVAILABLE,
            provider="openai",
            source="builtin",
        )
        assert result.model_id == "gpt-4"
        assert result.status == ModelStatus.AVAILABLE
        assert result.metadata == {}

    def test_full_result(self):
        """Test full discovery result."""
        result = ModelDiscoveryResult(
            model_id="gpt-4-0314",
            status=ModelStatus.DEPRECATED,
            provider="openai",
            source="builtin",
            name="GPT-4 (March 2024)",
            context_window=8192,
            deprecation_message="Deprecated. Use gpt-4 instead.",
            metadata={"owned_by": "openai"},
        )
        assert result.deprecation_message is not None
        assert result.context_window == 8192


class TestModelDiscovery:
    """Tests for ModelDiscovery class."""

    def test_deprecated_models_defined(self):
        """Test deprecated models are defined."""
        assert len(ModelDiscovery.DEPRECATED_MODELS) > 0
        assert "claude-2" in ModelDiscovery.DEPRECATED_MODELS

    def test_init_default_dirs(self):
        """Test initialization with default directories."""
        discovery = ModelDiscovery()
        assert discovery._user_dir == Path.home() / ".persona" / "models"
        assert discovery._project_dir == Path(".persona") / "models"

    def test_discover_builtin_model(self):
        """Test discovering a built-in model."""
        discovery = ModelDiscovery(cache_enabled=False)
        result = discovery.discover("gpt-4o")

        assert result is not None
        assert result.model_id == "gpt-4o"
        assert result.status == ModelStatus.AVAILABLE
        assert result.provider == "openai"

    def test_discover_deprecated_model(self):
        """Test discovering a deprecated model."""
        discovery = ModelDiscovery(cache_enabled=False)
        result = discovery.discover("claude-2")

        assert result is not None
        assert result.model_id == "claude-2"
        assert result.status == ModelStatus.DEPRECATED
        assert result.deprecation_message is not None

    def test_discover_unknown_model(self):
        """Test discovering an unknown model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = ModelDiscovery(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
                cache_enabled=False,
            )
            result = discovery.discover("unknown-model-xyz")

            assert result is None

    def test_discover_custom_model(self):
        """Test discovering a custom model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            # Create custom model config
            (user_dir / "custom-model.yaml").write_text("""
id: custom-model
name: Custom Model
provider: custom
context_window: 128000
""")

            discovery = ModelDiscovery(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
                cache_enabled=False,
            )
            result = discovery.discover("custom-model")

            assert result is not None
            assert result.model_id == "custom-model"
            assert result.status == ModelStatus.AVAILABLE
            assert result.source == "custom"

    def test_discover_all_builtin(self):
        """Test discovering all built-in models."""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = ModelDiscovery(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
                cache_enabled=False,
            )

            results = discovery.discover_all()

            # Should have multiple built-in models
            assert len(results) > 0

            # Check for known models
            model_ids = [r.model_id for r in results]
            assert "gpt-4o" in model_ids or "claude-opus-4-20250514" in model_ids

    def test_discover_all_by_provider(self):
        """Test discovering models filtered by provider."""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = ModelDiscovery(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
                cache_enabled=False,
            )

            results = discovery.discover_all(provider="anthropic")

            # All results should be anthropic
            for result in results:
                assert result.provider == "anthropic"

    def test_check_model_available(self):
        """Test check_model for available model."""
        discovery = ModelDiscovery(cache_enabled=False)
        is_available, message = discovery.check_model("gpt-4o")

        assert is_available is True
        assert "available" in message.lower()

    def test_check_model_deprecated(self):
        """Test check_model for deprecated model."""
        discovery = ModelDiscovery(cache_enabled=False)
        is_available, message = discovery.check_model("claude-2")

        assert is_available is True  # Still available but with warning
        assert "Warning" in message

    def test_check_model_not_found(self):
        """Test check_model for unknown model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = ModelDiscovery(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
                cache_enabled=False,
            )
            is_available, message = discovery.check_model("unknown-model")

            assert is_available is False
            assert "not found" in message.lower()

    def test_get_available_models(self):
        """Test get_available_models method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = ModelDiscovery(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
                cache_enabled=False,
            )
            available = discovery.get_available_models()

            assert len(available) > 0

    def test_get_available_models_by_provider(self):
        """Test get_available_models filtered by provider."""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = ModelDiscovery(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
                cache_enabled=False,
            )
            available = discovery.get_available_models(provider="openai")

            assert len(available) > 0

    def test_get_deprecated_models(self):
        """Test get_deprecated_models method."""
        discovery = ModelDiscovery(cache_enabled=False)
        deprecated = discovery.get_deprecated_models()

        assert len(deprecated) > 0
        for result in deprecated:
            assert result.status == ModelStatus.DEPRECATED
            assert result.deprecation_message is not None

    def test_clear_cache(self):
        """Test clearing the cache."""
        discovery = ModelDiscovery(cache_enabled=True)
        discovery._cache["test"] = ([], 0)

        discovery.clear_cache()
        assert len(discovery._cache) == 0

    def test_query_openai_no_api_key(self):
        """Test OpenAI query without API key."""
        with patch.dict(os.environ, {}, clear=True):
            discovery = ModelDiscovery(cache_enabled=False)
            results = discovery._query_openai_models()

            assert results == []

    def test_query_openai_with_api_key(self):
        """Test OpenAI query with API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "data": [
                        {"id": "gpt-4o", "owned_by": "openai"},
                        {"id": "gpt-4o-mini", "owned_by": "openai"},
                        {"id": "dall-e-3", "owned_by": "openai"},  # Should be filtered out
                    ],
                }
                mock_client.return_value.__enter__.return_value.get.return_value = mock_response

                discovery = ModelDiscovery(cache_enabled=False)
                results = discovery._query_openai_models()

                # Should only include gpt models
                model_ids = [r.model_id for r in results]
                assert "gpt-4o" in model_ids
                assert "dall-e-3" not in model_ids
