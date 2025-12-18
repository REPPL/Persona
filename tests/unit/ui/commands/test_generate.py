"""Tests for generate command."""

from unittest.mock import MagicMock, patch

from persona.ui.cli import app
from typer.testing import CliRunner

runner = CliRunner()


class TestGenerateCommand:
    """Tests for generate command."""

    def test_generate_help_shows_local_flag(self):
        """Test that --local flag appears in help."""
        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--local" in result.output
        assert "local models" in result.output.lower()

    def test_generate_help_shows_cloud_flag(self):
        """Test that --cloud flag appears in help."""
        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--cloud" in result.output

    def test_generate_help_shows_all_flag(self):
        """Test that --all flag appears in help."""
        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--all" in result.output


class TestOllamaModelSelection:
    """Tests for Ollama model selection helper."""

    def test_handle_ollama_model_selection_import(self):
        """Test that the helper function can be imported."""
        from persona.ui.commands.generate import _handle_ollama_model_selection

        assert callable(_handle_ollama_model_selection)

    def test_handle_multi_model_generation_import(self):
        """Test that the multi-model helper function can be imported."""
        from persona.ui.commands.generate import _handle_multi_model_generation

        assert callable(_handle_multi_model_generation)

    @patch("persona.core.providers.ProviderFactory")
    def test_handle_ollama_model_selection_all_models_flag(self, mock_factory):
        """Test that --all-models flag returns correct tuple."""
        from persona.ui.commands.generate import _handle_ollama_model_selection

        mock_provider = MagicMock()
        mock_provider.is_configured.return_value = True
        mock_provider.list_available_models.return_value = ["llama3:8b", "qwen2.5:7b"]
        mock_factory.create.return_value = mock_provider

        console = MagicMock()
        model, all_models = _handle_ollama_model_selection(console, all_models=True)

        assert model is None  # No single model selected
        assert all_models is True  # Multi-model mode enabled


class TestMultiModelGeneration:
    """Tests for multi-model generation functionality."""

    def test_multi_model_generation_dry_run(self, tmp_path):
        """Test multi-model generation in dry run mode."""
        from unittest.mock import MagicMock, patch

        from persona.ui.commands.generate import _handle_multi_model_generation

        # Create test data
        data_file = tmp_path / "test.csv"
        data_file.write_text("name,description\nAlice,A developer")

        console = MagicMock()

        with patch("persona.ui.commands.generate.ProviderFactory") as mock_factory:
            mock_provider = MagicMock()
            mock_provider.is_configured.return_value = True
            mock_provider.list_available_models.return_value = [
                "llama3:8b",
                "qwen2.5:7b",
            ]
            mock_factory.create.return_value = mock_provider

            with patch(
                "persona.ui.commands.generate._resolve_data_path"
            ) as mock_resolve:
                mock_resolve.return_value = data_file

                with patch("persona.ui.commands.generate.DataLoader") as mock_loader:
                    loader_instance = MagicMock()
                    loader_instance.load_path.return_value = (
                        "test data",
                        [str(data_file)],
                    )
                    loader_instance.count_tokens.return_value = 100
                    mock_loader.return_value = loader_instance

                    # Run in dry run mode - should not raise
                    _handle_multi_model_generation(
                        console=console,
                        data_path=data_file,
                        output=None,
                        count=3,
                        workflow="default",
                        experiment=None,
                        dry_run=True,
                        no_progress=True,
                        anonymise=False,
                        anonymise_strategy="redact",
                        verify=False,
                        verify_models=None,
                        verify_threshold=0.7,
                        include_cloud=False,
                    )

                    # Verify dry run message was printed
                    call_args = [str(call) for call in console.print.call_args_list]
                    assert any("Dry run" in str(arg) for arg in call_args)
