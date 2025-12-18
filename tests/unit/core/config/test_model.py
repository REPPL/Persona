"""Tests for custom model configuration."""

import tempfile
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from persona.core.config.model import (
    ModelCapabilities,
    ModelConfig,
    ModelLoader,
    ModelPricing,
    get_all_models,
    get_builtin_models,
)


class TestModelPricing:
    """Tests for ModelPricing model."""

    def test_default_values(self):
        """Test default pricing values."""
        pricing = ModelPricing()
        assert pricing.input == Decimal("0.0")
        assert pricing.output == Decimal("0.0")
        assert pricing.currency == "USD"

    def test_custom_values(self):
        """Test custom pricing values."""
        pricing = ModelPricing(input=3.0, output=15.0)
        assert pricing.input == Decimal("3.0")
        assert pricing.output == Decimal("15.0")

    def test_decimal_coercion(self):
        """Test decimal coercion from various types."""
        pricing = ModelPricing(input="5.50", output=12)
        assert pricing.input == Decimal("5.50")
        assert pricing.output == Decimal("12")


class TestModelCapabilities:
    """Tests for ModelCapabilities model."""

    def test_default_values(self):
        """Test default capability values."""
        caps = ModelCapabilities()
        assert caps.structured_output is True
        assert caps.vision is False
        assert caps.function_calling is True
        assert caps.streaming is True

    def test_custom_values(self):
        """Test custom capability values."""
        caps = ModelCapabilities(vision=True, streaming=False)
        assert caps.vision is True
        assert caps.streaming is False


class TestModelConfig:
    """Tests for ModelConfig model."""

    def test_minimal_config(self):
        """Test minimal valid configuration."""
        config = ModelConfig(
            id="test-model",
            name="Test Model",
            provider="openai",
        )
        assert config.id == "test-model"
        assert config.name == "Test Model"
        assert config.provider == "openai"

    def test_full_config(self):
        """Test full configuration with all fields."""
        config = ModelConfig(
            id="my-finetuned-gpt4",
            name="Fine-tuned GPT-4",
            provider="azure-openai",
            base_model="gpt-4",
            context_window=128000,
            max_output=8192,
            deployment_id="my-deployment",
            description="Custom fine-tuned model",
            pricing=ModelPricing(input=5.0, output=15.0),
            capabilities=ModelCapabilities(vision=True),
        )
        assert config.base_model == "gpt-4"
        assert config.deployment_id == "my-deployment"
        assert config.pricing.input == Decimal("5.0")
        assert config.capabilities.vision is True

    def test_id_validation_valid(self):
        """Test valid model IDs."""
        valid_ids = ["gpt-4", "claude-3", "my.model", "model_v1", "a", "model-1.0"]
        for model_id in valid_ids:
            config = ModelConfig(id=model_id, name="Test", provider="test")
            assert config.id == model_id

    def test_id_validation_invalid(self):
        """Test invalid model IDs."""
        invalid_ids = ["-model", "model-", ".model", "model.", "_model"]
        for model_id in invalid_ids:
            with pytest.raises(ValueError):
                ModelConfig(id=model_id, name="Test", provider="test")

    def test_positive_validation(self):
        """Test positive integer validation."""
        with pytest.raises(ValueError):
            ModelConfig(id="test", name="Test", provider="test", context_window=0)

        with pytest.raises(ValueError):
            ModelConfig(id="test", name="Test", provider="test", max_output=-1)

    def test_get_effective_model_id_no_deployment(self):
        """Test effective model ID without deployment."""
        config = ModelConfig(id="gpt-4", name="GPT-4", provider="openai")
        assert config.get_effective_model_id() == "gpt-4"

    def test_get_effective_model_id_with_deployment(self):
        """Test effective model ID with deployment."""
        config = ModelConfig(
            id="my-gpt4",
            name="My GPT-4",
            provider="azure",
            deployment_id="my-deployment",
        )
        assert config.get_effective_model_id() == "my-deployment"


class TestModelConfigYaml:
    """Tests for ModelConfig YAML serialisation."""

    def test_from_yaml(self):
        """Test loading config from YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(
                {
                    "id": "test-model",
                    "name": "Test Model",
                    "provider": "openai",
                    "context_window": 128000,
                    "pricing": {
                        "input": 3.0,
                        "output": 15.0,
                    },
                },
                f,
            )
            f.flush()

            config = ModelConfig.from_yaml(Path(f.name))

            assert config.id == "test-model"
            assert config.pricing.input == Decimal("3.0")

            Path(f.name).unlink()

    def test_from_yaml_not_found(self):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            ModelConfig.from_yaml(Path("/nonexistent/path.yaml"))

    def test_to_yaml(self):
        """Test saving config to YAML file."""
        config = ModelConfig(
            id="test-model",
            name="Test Model",
            provider="openai",
            pricing=ModelPricing(input=5.0, output=15.0),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.yaml"
            config.to_yaml(path)

            assert path.exists()

            with open(path) as f:
                data = yaml.safe_load(f)

            assert data["id"] == "test-model"
            assert float(data["pricing"]["input"]) == 5.0

    def test_yaml_round_trip(self):
        """Test config survives YAML round trip."""
        original = ModelConfig(
            id="round-trip",
            name="Round Trip Test",
            provider="anthropic",
            context_window=200000,
            max_output=8192,
            pricing=ModelPricing(input=3.0, output=15.0),
            capabilities=ModelCapabilities(vision=True),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.yaml"
            original.to_yaml(path)
            loaded = ModelConfig.from_yaml(path)

            assert loaded.id == original.id
            assert loaded.context_window == original.context_window
            assert loaded.pricing.input == original.pricing.input
            assert loaded.capabilities.vision == original.capabilities.vision


class TestModelLoader:
    """Tests for ModelLoader."""

    def test_default_search_paths(self):
        """Test default search paths."""
        loader = ModelLoader()
        assert loader._user_dir == Path.home() / ".persona" / "models"
        assert loader._project_dir == Path(".persona") / "models"

    def test_list_models_empty(self):
        """Test listing models with no configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = ModelLoader(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
            )
            assert loader.list_models() == []

    def test_list_models_with_configs(self):
        """Test listing models with configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            for model_id in ["model-a", "model-b"]:
                config = ModelConfig(
                    id=model_id,
                    name=f"Model {model_id}",
                    provider="openai",
                )
                config.to_yaml(user_dir / f"{model_id}.yaml")

            loader = ModelLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            models = loader.list_models()
            assert "model-a" in models
            assert "model-b" in models

    def test_list_models_by_provider(self):
        """Test listing models filtered by provider."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            ModelConfig(id="openai-model", name="OpenAI", provider="openai").to_yaml(
                user_dir / "openai-model.yaml"
            )
            ModelConfig(
                id="anthropic-model", name="Anthropic", provider="anthropic"
            ).to_yaml(user_dir / "anthropic-model.yaml")

            loader = ModelLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            openai_models = loader.list_models(provider="openai")
            assert "openai-model" in openai_models
            assert "anthropic-model" not in openai_models

    def test_load_model(self):
        """Test loading a model config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(
                id="test-model",
                name="Test Model",
                provider="openai",
            )
            config.to_yaml(user_dir / "test-model.yaml")

            loader = ModelLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            loaded = loader.load("test-model")
            assert loaded.id == "test-model"
            assert loaded.name == "Test Model"

    def test_load_model_not_found(self):
        """Test loading nonexistent model raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = ModelLoader(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
            )

            with pytest.raises(FileNotFoundError):
                loader.load("nonexistent")

    def test_load_model_caching(self):
        """Test model configs are cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(id="cached", name="Cached", provider="openai")
            config.to_yaml(user_dir / "cached.yaml")

            loader = ModelLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            first = loader.load("cached")
            second = loader.load("cached")

            assert first is second

    def test_save_model(self):
        """Test saving model configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"

            loader = ModelLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            config = ModelConfig(
                id="saved-model",
                name="Saved Model",
                provider="openai",
            )

            path = loader.save(config, user_level=True)

            assert path == user_dir / "saved-model.yaml"
            assert path.exists()

    def test_delete_model(self):
        """Test deleting a model config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(id="to-delete", name="Delete", provider="openai")
            config.to_yaml(user_dir / "to-delete.yaml")

            loader = ModelLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            assert loader.exists("to-delete")
            result = loader.delete("to-delete")
            assert result is True
            assert not loader.exists("to-delete")

    def test_exists(self):
        """Test exists check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(id="exists", name="Exists", provider="openai")
            config.to_yaml(user_dir / "exists.yaml")

            loader = ModelLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            assert loader.exists("exists") is True
            assert loader.exists("nonexistent") is False

    def test_list_by_provider(self):
        """Test listing models grouped by provider."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            ModelConfig(id="openai-1", name="O1", provider="openai").to_yaml(
                user_dir / "openai-1.yaml"
            )
            ModelConfig(id="openai-2", name="O2", provider="openai").to_yaml(
                user_dir / "openai-2.yaml"
            )
            ModelConfig(id="anthropic-1", name="A1", provider="anthropic").to_yaml(
                user_dir / "anthropic-1.yaml"
            )

            loader = ModelLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            by_provider = loader.list_by_provider()

            assert "openai" in by_provider
            assert "anthropic" in by_provider
            assert len(by_provider["openai"]) == 2
            assert len(by_provider["anthropic"]) == 1


class TestGetBuiltinModels:
    """Tests for get_builtin_models function."""

    def test_returns_providers(self):
        """Test returns models for built-in providers."""
        models = get_builtin_models()

        assert "openai" in models
        assert "anthropic" in models
        assert "gemini" in models

    def test_models_not_empty(self):
        """Test each provider has models."""
        models = get_builtin_models()

        for provider, model_list in models.items():
            assert len(model_list) > 0, f"No models for {provider}"


class TestGetAllModels:
    """Tests for get_all_models function."""

    def test_includes_builtin(self):
        """Test includes built-in models."""
        models = get_all_models(include_custom=False)

        assert "openai" in models
        assert len(models["openai"]) > 0

    def test_includes_custom(self):
        """Test includes custom models when available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from persona.core.config.model import ModelLoader

            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            config = ModelConfig(
                id="custom-model",
                name="Custom",
                provider="custom-provider",
            )
            config.to_yaml(user_dir / "custom-model.yaml")

            # Temporarily patch the loader
            original_user_dir = ModelLoader.DEFAULT_USER_DIR
            ModelLoader.DEFAULT_USER_DIR = user_dir

            try:
                models = get_all_models(include_custom=True)
                # Custom models should be included
                assert "custom-provider" in models or any(
                    "custom-model" in m
                    for provider_models in models.values()
                    for m in provider_models
                )
            finally:
                ModelLoader.DEFAULT_USER_DIR = original_user_dir
