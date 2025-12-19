"""
Tests for Ollama model comparison functionality.
"""

from unittest.mock import MagicMock, patch

import pytest

from persona.core.discovery.ollama_models import (
    ModelComparisonResult,
    ModelTestStatus,
    OllamaModelRegistry,
    OllamaTestedModel,
    compare_ollama_models,
    get_untested_models,
)


class TestOllamaTestedModelDataclass:
    """Test OllamaTestedModel dataclass."""

    def test_creation(self):
        """Test creating a OllamaTestedModel."""
        model = OllamaTestedModel(
            name="llama3:8b",
            tested_date="2024-11-15",
            persona_version="1.3.0",
            notes="Test notes",
        )
        assert model.name == "llama3:8b"
        assert model.tested_date == "2024-11-15"
        assert model.persona_version == "1.3.0"
        assert model.test_result == "passed"
        assert model.notes == "Test notes"

    def test_default_values(self):
        """Test default values for OllamaTestedModel."""
        model = OllamaTestedModel(
            name="test:model",
            tested_date="2024-01-01",
            persona_version="1.0.0",
        )
        assert model.test_result == "passed"
        assert model.notes == ""


class TestModelComparisonResult:
    """Test ModelComparisonResult dataclass."""

    def test_has_untested_models_true(self):
        """Test has_untested_models when there are untested models."""
        result = ModelComparisonResult(
            tested_models=["llama3:8b"],
            available_models=["llama3:8b", "new:model"],
            untested_models=["new:model"],
        )
        assert result.has_untested_models is True

    def test_has_untested_models_false(self):
        """Test has_untested_models when all models are tested."""
        result = ModelComparisonResult(
            tested_models=["llama3:8b"],
            available_models=["llama3:8b"],
            untested_models=[],
        )
        assert result.has_untested_models is False

    def test_summary(self):
        """Test summary property."""
        result = ModelComparisonResult(
            tested_models=["a", "b"],
            available_models=["a", "c"],
            untested_models=["c"],
            missing_models=["b"],
        )
        summary = result.summary
        assert "Tested models: 2" in summary
        assert "Available models: 2" in summary
        assert "New untested models: 1" in summary
        assert "Previously tested but now unavailable: 1" in summary

    def test_to_dict(self):
        """Test converting to dictionary."""
        result = ModelComparisonResult(
            tested_models=["a"],
            available_models=["a", "b"],
            untested_models=["b"],
            missing_models=[],
        )
        d = result.to_dict()
        assert d["tested_models"] == ["a"]
        assert d["available_models"] == ["a", "b"]
        assert d["untested_models"] == ["b"]
        assert d["missing_models"] == []
        assert "comparison_time" in d


class TestOllamaModelRegistry:
    """Test OllamaModelRegistry class."""

    def test_tested_model_names(self):
        """Test getting tested model names."""
        registry = OllamaModelRegistry()
        names = registry.tested_model_names
        assert isinstance(names, list)
        assert len(names) > 0
        assert "llama3:8b" in names

    def test_get_tested_model_exists(self):
        """Test getting an existing tested model."""
        registry = OllamaModelRegistry()
        model = registry.get_tested_model("llama3:8b")
        assert model is not None
        assert model.name == "llama3:8b"
        assert model.persona_version is not None

    def test_get_tested_model_not_exists(self):
        """Test getting a non-existent tested model."""
        registry = OllamaModelRegistry()
        model = registry.get_tested_model("nonexistent:model")
        assert model is None

    def test_is_tested_true(self):
        """Test is_tested for a tested model."""
        registry = OllamaModelRegistry()
        assert registry.is_tested("llama3:8b") is True

    def test_is_tested_false(self):
        """Test is_tested for an untested model."""
        registry = OllamaModelRegistry()
        assert registry.is_tested("nonexistent:model") is False

    def test_get_available_models(self):
        """Test getting available models from Ollama."""
        registry = OllamaModelRegistry()

        mock_provider = MagicMock()
        mock_provider.list_available_models.return_value = [
            "llama3:8b",
            "mistral:7b",
            "new:model",
        ]

        # Directly set the mocked provider
        registry._ollama_provider = mock_provider
        models = registry.get_available_models()

        assert models == ["llama3:8b", "mistral:7b", "new:model"]

    def test_compare_models(self):
        """Test comparing tested vs available models."""
        registry = OllamaModelRegistry()

        mock_provider = MagicMock()
        mock_provider.list_available_models.return_value = [
            "llama3:8b",  # Tested
            "new:model",  # Not tested
        ]

        # Directly set the mocked provider
        registry._ollama_provider = mock_provider
        result = registry.compare_models()

        assert "llama3:8b" in result.tested_models
        assert "llama3:8b" in result.available_models
        assert "new:model" in result.untested_models
        # Check for missing models (tested but not available)
        assert "mistral:7b" in result.missing_models

    def test_check_for_new_models_quiet(self):
        """Test checking for new models in quiet mode."""
        registry = OllamaModelRegistry()

        mock_provider = MagicMock()
        mock_provider.list_available_models.return_value = [
            "llama3:8b",
            "new:model",
        ]

        # Directly set the mocked provider
        registry._ollama_provider = mock_provider
        result = registry.check_for_new_models(quiet=True)

        assert result.has_untested_models is True
        assert "new:model" in result.untested_models


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_compare_ollama_models(self):
        """Test compare_ollama_models function."""
        mock_provider = MagicMock()
        mock_provider.list_available_models.return_value = ["llama3:8b", "new:model"]

        with patch.object(
            OllamaModelRegistry,
            "get_available_models",
            return_value=["llama3:8b", "new:model"],
        ):
            result = compare_ollama_models(quiet=True)

        assert isinstance(result, ModelComparisonResult)
        assert result.has_untested_models is True

    def test_get_untested_models(self):
        """Test get_untested_models function."""
        with patch.object(
            OllamaModelRegistry,
            "get_available_models",
            return_value=["llama3:8b", "new:model"],
        ):
            untested = get_untested_models()

        assert "new:model" in untested
        assert "llama3:8b" not in untested


class TestModelTestStatus:
    """Test ModelTestStatus enum."""

    def test_status_values(self):
        """Test enum values."""
        assert ModelTestStatus.TESTED.value == "tested"
        assert ModelTestStatus.UNTESTED.value == "untested"
        assert ModelTestStatus.UNAVAILABLE.value == "unavailable"


@pytest.mark.real_api
class TestOllamaModelRegistryIntegration:
    """
    Integration tests requiring a real Ollama instance.

    Run with: pytest -m real_api
    """

    def test_real_get_available_models(self):
        """Test getting models from real Ollama instance."""
        from persona.core.providers.ollama import OllamaProvider

        provider = OllamaProvider()
        if not provider.is_configured():
            pytest.skip("Ollama not running")

        registry = OllamaModelRegistry()
        models = registry.get_available_models()

        assert isinstance(models, list)
        assert len(models) > 0

    def test_real_compare_models(self):
        """Test comparison with real Ollama instance."""
        from persona.core.providers.ollama import OllamaProvider

        provider = OllamaProvider()
        if not provider.is_configured():
            pytest.skip("Ollama not running")

        registry = OllamaModelRegistry()
        result = registry.compare_models()

        assert isinstance(result, ModelComparisonResult)
        assert len(result.available_models) > 0
        # Print for manual inspection
        print(f"\nTested: {len(result.tested_models)}")
        print(f"Available: {len(result.available_models)}")
        print(f"Untested: {result.untested_models}")
        print(f"Missing: {result.missing_models}")
