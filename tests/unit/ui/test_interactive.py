"""
Tests for interactive mode (F-092).
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from persona.ui.interactive import (
    ConfigEditor,
    ConfigWizard,
    GenerateWizard,
    InteractivePrompts,
    get_configured_providers,
    get_models_for_provider,
    is_interactive_supported,
)


class TestInteractiveSupport:
    """Tests for interactive mode detection."""

    def test_is_interactive_supported_tty(self, monkeypatch):
        """Test detection when both stdin and stdout are TTY."""
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        assert is_interactive_supported() is True

    def test_is_interactive_supported_no_stdin_tty(self, monkeypatch):
        """Test detection when stdin is not TTY (piped)."""
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        assert is_interactive_supported() is False

    def test_is_interactive_supported_no_stdout_tty(self, monkeypatch):
        """Test detection when stdout is not TTY (redirected)."""
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
        assert is_interactive_supported() is False


class TestGetConfiguredProviders:
    """Tests for provider configuration detection."""

    def test_returns_provider_list(self):
        """Test that provider list is returned."""
        providers = get_configured_providers()
        assert len(providers) == 3
        names = [p[0] for p in providers]
        assert "anthropic" in names
        assert "openai" in names
        assert "gemini" in names

    def test_provider_display_names(self):
        """Test that display names are included."""
        providers = get_configured_providers()
        displays = {p[0]: p[1] for p in providers}
        assert "Claude" in displays["anthropic"]
        assert "GPT" in displays["openai"]
        assert "Gemini" in displays["gemini"]


class TestGetModelsForProvider:
    """Tests for model listing."""

    def test_anthropic_models(self):
        """Test getting Anthropic models."""
        models = get_models_for_provider("anthropic")
        assert len(models) > 0
        model_ids = [m[0] for m in models]
        # Check for expected models
        assert any("claude" in m.lower() for m in model_ids)

    def test_openai_models(self):
        """Test getting OpenAI models."""
        models = get_models_for_provider("openai")
        assert len(models) > 0
        model_ids = [m[0] for m in models]
        assert any("gpt" in m.lower() for m in model_ids)

    def test_gemini_models(self):
        """Test getting Gemini models."""
        models = get_models_for_provider("gemini")
        assert len(models) > 0
        model_ids = [m[0] for m in models]
        assert any("gemini" in m.lower() for m in model_ids)

    def test_default_model_first(self):
        """Test that default model appears first."""
        models = get_models_for_provider("anthropic")
        if models:
            # Default should be at the start (is_default=True sorts first)
            _, _, is_default = models[0]
            assert is_default is True


class TestInteractivePrompts:
    """Tests for InteractivePrompts class."""

    @pytest.fixture
    def prompts(self):
        """Create prompts instance."""
        return InteractivePrompts()

    def test_init(self, prompts):
        """Test prompts initialisation."""
        assert prompts.console is not None

    @patch("persona.ui.interactive.questionary.select")
    def test_select_provider(self, mock_select, prompts):
        """Test provider selection prompt."""
        mock_select.return_value.ask.return_value = "openai"

        result = prompts.select_provider()

        assert result == "openai"
        mock_select.assert_called_once()

    @patch("persona.ui.interactive.questionary.select")
    def test_select_provider_cancelled(self, mock_select, prompts):
        """Test provider selection cancelled."""
        mock_select.return_value.ask.return_value = None

        result = prompts.select_provider()

        assert result is None

    @patch("persona.ui.interactive.questionary.select")
    def test_select_model(self, mock_select, prompts):
        """Test model selection prompt."""
        mock_select.return_value.ask.return_value = "gpt-4o"

        result = prompts.select_model("openai")

        assert result == "gpt-4o"
        mock_select.assert_called_once()

    @patch("persona.ui.interactive.questionary.text")
    def test_input_count(self, mock_text, prompts):
        """Test count input prompt."""
        mock_text.return_value.ask.return_value = "5"

        result = prompts.input_count()

        assert result == 5

    @patch("persona.ui.interactive.questionary.text")
    def test_input_count_cancelled(self, mock_text, prompts):
        """Test count input cancelled."""
        mock_text.return_value.ask.return_value = None

        result = prompts.input_count()

        assert result is None

    @patch("persona.ui.interactive.questionary.path")
    def test_input_path(self, mock_path, prompts, tmp_path):
        """Test path input prompt."""
        test_path = str(tmp_path / "data.csv")
        mock_path.return_value.ask.return_value = test_path

        result = prompts.input_path()

        assert result == Path(test_path)

    @patch("persona.ui.interactive.questionary.path")
    def test_input_path_cancelled(self, mock_path, prompts):
        """Test path input cancelled."""
        mock_path.return_value.ask.return_value = None

        result = prompts.input_path()

        assert result is None

    @patch("persona.ui.interactive.questionary.select")
    def test_select_output_format(self, mock_select, prompts):
        """Test output format selection."""
        mock_select.return_value.ask.return_value = "yaml"

        result = prompts.select_output_format()

        assert result == "yaml"

    @patch("persona.ui.interactive.questionary.select")
    def test_select_workflow(self, mock_select, prompts):
        """Test workflow selection."""
        mock_select.return_value.ask.return_value = "research"

        result = prompts.select_workflow()

        assert result == "research"

    @patch("persona.ui.interactive.questionary.confirm")
    def test_confirm(self, mock_confirm, prompts):
        """Test confirmation prompt."""
        mock_confirm.return_value.ask.return_value = True

        result = prompts.confirm("Proceed?")

        assert result is True

    @patch("persona.ui.interactive.questionary.text")
    def test_input_text(self, mock_text, prompts):
        """Test text input prompt."""
        mock_text.return_value.ask.return_value = "hello"

        result = prompts.input_text("Message:")

        assert result == "hello"

    @patch("persona.ui.interactive.questionary.password")
    def test_input_text_secret(self, mock_password, prompts):
        """Test secret text input prompt."""
        mock_password.return_value.ask.return_value = "secret123"

        result = prompts.input_text("API Key:", secret=True)

        assert result == "secret123"


class TestGenerateWizard:
    """Tests for GenerateWizard."""

    @pytest.fixture
    def wizard(self):
        """Create wizard instance."""
        return GenerateWizard()

    def test_init(self, wizard):
        """Test wizard initialisation."""
        assert wizard.prompts is not None
        assert wizard.console is not None

    @patch.object(InteractivePrompts, "select_provider")
    @patch.object(InteractivePrompts, "select_model")
    @patch.object(InteractivePrompts, "input_count")
    @patch.object(InteractivePrompts, "select_workflow")
    @patch.object(InteractivePrompts, "confirm")
    def test_run_with_prefilled(
        self,
        mock_confirm,
        mock_workflow,
        mock_count,
        mock_model,
        mock_provider,
        wizard,
        tmp_path,
    ):
        """Test wizard run with pre-filled values."""
        # Create test data file
        data_file = tmp_path / "data.csv"
        data_file.write_text("col1,col2\nval1,val2")

        mock_confirm.return_value = True

        # Pre-fill all values - should skip all prompts
        result = wizard.run(
            data_path=data_file,
            provider="openai",
            model="gpt-4o",
            count=5,
            workflow="research",
        )

        assert result is not None
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o"
        assert result["count"] == 5
        assert result["workflow"] == "research"

        # Prompts shouldn't be called since values were pre-filled
        mock_provider.assert_not_called()
        mock_model.assert_not_called()
        mock_count.assert_not_called()
        mock_workflow.assert_not_called()

    @patch.object(InteractivePrompts, "input_path")
    def test_run_cancelled(self, mock_path, wizard):
        """Test wizard cancelled at first prompt."""
        mock_path.return_value = None

        result = wizard.run()

        assert result is None


class TestConfigWizard:
    """Tests for ConfigWizard."""

    @pytest.fixture
    def wizard(self):
        """Create wizard instance."""
        return ConfigWizard()

    def test_init(self, wizard):
        """Test wizard initialisation."""
        assert wizard.prompts is not None
        assert wizard.console is not None

    @patch("persona.ui.interactive.questionary.select")
    def test_run_cancelled(self, mock_select, wizard):
        """Test wizard cancelled at section selection."""
        mock_select.return_value.ask.return_value = None

        result = wizard.run()

        assert result is None

    @patch("persona.ui.interactive.questionary.select")
    @patch.object(InteractivePrompts, "select_provider")
    @patch.object(InteractivePrompts, "select_model")
    @patch.object(InteractivePrompts, "input_count")
    def test_run_defaults_section(
        self,
        mock_count,
        mock_model,
        mock_provider,
        mock_select,
        wizard,
    ):
        """Test configuring defaults section."""
        mock_select.return_value.ask.return_value = "defaults"
        mock_provider.return_value = "openai"
        mock_model.return_value = "gpt-4o"
        mock_count.return_value = 5

        result = wizard.run()

        assert result is not None
        assert result["section"] == "defaults"
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o"
        assert result["count"] == 5

    @patch("persona.ui.interactive.questionary.select")
    @patch("persona.ui.interactive.questionary.text")
    def test_run_budgets_section(
        self,
        mock_text,
        mock_select,
        wizard,
    ):
        """Test configuring budgets section."""
        mock_select.return_value.ask.return_value = "budgets"
        mock_text.return_value.ask.side_effect = ["10.00", "50.00", "200.00"]

        result = wizard.run()

        assert result is not None
        assert result["section"] == "budgets"
        assert result["per_run"] == 10.0
        assert result["daily"] == 50.0
        assert result["monthly"] == 200.0

    @patch("persona.ui.interactive.questionary.select")
    @patch.object(InteractivePrompts, "select_output_format")
    @patch.object(InteractivePrompts, "confirm")
    def test_run_output_section(
        self,
        mock_confirm,
        mock_format,
        mock_select,
        wizard,
    ):
        """Test configuring output section."""
        mock_select.return_value.ask.return_value = "output"
        mock_format.return_value = "yaml"
        mock_confirm.side_effect = [False, True]  # include_readme, timestamp_folders

        result = wizard.run()

        assert result is not None
        assert result["section"] == "output"
        assert result["format"] == "yaml"
        assert result["include_readme"] is False
        assert result["timestamp_folders"] is True

    @patch("persona.ui.interactive.questionary.select")
    def test_run_logging_section(self, mock_select, wizard):
        """Test configuring logging section."""
        # First call for section selection, then level, then format
        mock_select.return_value.ask.side_effect = ["logging", "debug", "json"]

        result = wizard.run()

        assert result is not None
        assert result["section"] == "logging"
        assert result["level"] == "debug"
        assert result["format"] == "json"


class TestConfigEditor:
    """Tests for ConfigEditor (F-093)."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        mock = MagicMock()
        mock.defaults.provider = "anthropic"
        mock.defaults.model = "claude-sonnet-4-20250514"
        mock.defaults.count = 3
        mock.defaults.complexity = "moderate"
        mock.defaults.detail_level = "standard"
        mock.defaults.workflow = "default"
        mock.budgets.per_run = 5.0
        mock.budgets.daily = 25.0
        mock.budgets.monthly = 100.0
        mock.output.format = "json"
        mock.output.include_readme = True
        mock.output.timestamp_folders = True
        mock.logging.level = "info"
        mock.logging.format = "console"
        return mock

    @pytest.fixture
    def editor(self):
        """Create editor instance."""
        return ConfigEditor()

    def test_init(self, editor):
        """Test editor initialisation."""
        assert editor.prompts is not None
        assert editor.console is not None
        assert editor.project_level is False

    def test_init_project_level(self):
        """Test editor with project level."""
        editor = ConfigEditor(project_level=True)
        assert editor.project_level is True

    @patch("persona.ui.interactive.questionary.select")
    @patch("persona.core.config.global_config.get_config_manager")
    def test_run_cancelled(self, mock_manager, mock_select, editor, mock_config):
        """Test editor cancelled at section selection."""
        mock_manager.return_value.load.return_value = mock_config
        mock_select.return_value.ask.return_value = None

        result = editor.run()

        assert result is None

    @patch("persona.ui.interactive.questionary.select")
    @patch("persona.ui.interactive.questionary.text")
    @patch("persona.core.config.global_config.get_config_manager")
    @patch.object(InteractivePrompts, "select_provider")
    @patch.object(InteractivePrompts, "select_model")
    def test_run_defaults_section(
        self,
        mock_model,
        mock_provider,
        mock_manager,
        mock_text,
        mock_select,
        editor,
        mock_config,
    ):
        """Test editing defaults section."""
        mock_manager.return_value.load.return_value = mock_config
        mock_select.return_value.ask.side_effect = ["defaults", "complex", "detailed"]
        mock_provider.return_value = "openai"
        mock_model.return_value = "gpt-4o"
        mock_text.return_value.ask.return_value = "5"

        result = editor.run()

        assert result is not None
        assert result.get("defaults.provider") == "openai"
        assert result.get("defaults.model") == "gpt-4o"
        assert result.get("defaults.count") == 5
        assert result.get("defaults.complexity") == "complex"
        assert result.get("defaults.detail_level") == "detailed"

    @patch("persona.ui.interactive.questionary.select")
    @patch("persona.ui.interactive.questionary.text")
    @patch("persona.core.config.global_config.get_config_manager")
    def test_run_budgets_section(
        self,
        mock_manager,
        mock_text,
        mock_select,
        editor,
        mock_config,
    ):
        """Test editing budgets section."""
        mock_manager.return_value.load.return_value = mock_config
        mock_select.return_value.ask.return_value = "budgets"
        mock_text.return_value.ask.side_effect = ["10.00", "50.00", "200.00"]

        result = editor.run()

        assert result is not None
        assert result.get("budgets.per_run") == 10.0
        assert result.get("budgets.daily") == 50.0
        assert result.get("budgets.monthly") == 200.0

    @patch("persona.ui.interactive.questionary.select")
    @patch("persona.ui.interactive.questionary.confirm")
    @patch("persona.core.config.global_config.get_config_manager")
    def test_run_output_section(
        self,
        mock_manager,
        mock_confirm,
        mock_select,
        editor,
        mock_config,
    ):
        """Test editing output section."""
        mock_manager.return_value.load.return_value = mock_config
        mock_select.return_value.ask.side_effect = ["output", "yaml"]
        mock_confirm.return_value.ask.side_effect = [
            False,
            False,
        ]  # include_readme, timestamp

        result = editor.run()

        assert result is not None
        assert result.get("output.format") == "yaml"
        assert result.get("output.include_readme") is False
        assert result.get("output.timestamp_folders") is False

    @patch("persona.ui.interactive.questionary.select")
    @patch("persona.core.config.global_config.get_config_manager")
    def test_run_logging_section(
        self,
        mock_manager,
        mock_select,
        editor,
        mock_config,
    ):
        """Test editing logging section."""
        mock_manager.return_value.load.return_value = mock_config
        mock_select.return_value.ask.side_effect = ["logging", "debug", "json"]

        result = editor.run()

        assert result is not None
        assert result.get("logging.level") == "debug"
        assert result.get("logging.format") == "json"

    @patch("persona.ui.interactive.questionary.select")
    @patch("persona.ui.interactive.questionary.confirm")
    @patch("persona.core.config.global_config.get_config_manager")
    def test_run_reset(
        self,
        mock_manager,
        mock_confirm,
        mock_select,
        editor,
        mock_config,
    ):
        """Test reset to defaults."""
        mock_manager.return_value.load.return_value = mock_config
        mock_select.return_value.ask.return_value = "reset"
        mock_confirm.return_value.ask.return_value = True

        result = editor.run()

        assert result is not None
        assert result["defaults.provider"] == "anthropic"
        assert result["defaults.model"] is None
        assert result["defaults.count"] == 3
        assert result["budgets.per_run"] is None
        assert result["output.format"] == "json"
        assert result["logging.level"] == "info"

    @patch("persona.ui.interactive.questionary.select")
    @patch("persona.ui.interactive.questionary.confirm")
    @patch("persona.core.config.global_config.get_config_manager")
    def test_run_reset_cancelled(
        self,
        mock_manager,
        mock_confirm,
        mock_select,
        editor,
        mock_config,
    ):
        """Test reset cancelled."""
        mock_manager.return_value.load.return_value = mock_config
        mock_select.return_value.ask.return_value = "reset"
        mock_confirm.return_value.ask.return_value = False

        result = editor.run()

        assert result is None

    def test_reset_all_values(self, editor):
        """Test reset returns correct default values."""
        result = editor._reset_all()

        assert result["defaults.provider"] == "anthropic"
        assert result["defaults.model"] is None
        assert result["defaults.count"] == 3
        assert result["defaults.complexity"] == "moderate"
        assert result["defaults.detail_level"] == "standard"
        assert result["defaults.workflow"] == "default"
        assert result["budgets.per_run"] is None
        assert result["budgets.daily"] is None
        assert result["budgets.monthly"] is None
        assert result["output.format"] == "json"
        assert result["output.include_readme"] is True
        assert result["output.timestamp_folders"] is True
        assert result["logging.level"] == "info"
        assert result["logging.format"] == "console"

    def test_show_current_config(self, editor, mock_config, capsys):
        """Test current config display."""
        editor._show_current_config(mock_config)
        # Method should complete without error (output goes to Rich console)

    @patch("persona.ui.interactive.questionary.text")
    def test_edit_budgets_with_none(
        self,
        mock_text,
        editor,
        mock_config,
    ):
        """Test editing budgets with 'none' values."""
        mock_text.return_value.ask.side_effect = ["none", "none", "none"]

        result = editor._edit_budgets(mock_config)

        # Should return None values since budgets were set and now being cleared
        assert result.get("budgets.per_run") is None
        assert result.get("budgets.daily") is None
        assert result.get("budgets.monthly") is None

    @patch("persona.ui.interactive.questionary.select")
    @patch.object(InteractivePrompts, "select_provider")
    @patch.object(InteractivePrompts, "select_model")
    @patch("persona.ui.interactive.questionary.text")
    def test_edit_defaults_no_changes(
        self,
        mock_text,
        mock_model,
        mock_provider,
        mock_select,
        editor,
        mock_config,
    ):
        """Test editing defaults with no changes."""
        # Return same values as config
        mock_provider.return_value = "anthropic"
        mock_model.return_value = "claude-sonnet-4-20250514"
        mock_text.return_value.ask.return_value = "3"  # Same count
        mock_select.return_value.ask.side_effect = [
            "moderate",
            "standard",
        ]  # Same values

        result = editor._edit_defaults(mock_config)

        # No changes made
        assert result is None

    @patch("persona.ui.interactive.questionary.select")
    @patch("persona.ui.interactive.questionary.confirm")
    def test_edit_output_no_changes(
        self,
        mock_confirm,
        mock_select,
        editor,
        mock_config,
    ):
        """Test editing output with no changes."""
        mock_select.return_value.ask.return_value = "json"  # Same format
        mock_confirm.return_value.ask.side_effect = [True, True]  # Same values

        result = editor._edit_output(mock_config)

        # No changes made
        assert result is None

    @patch("persona.ui.interactive.questionary.select")
    def test_edit_logging_no_changes(
        self,
        mock_select,
        editor,
        mock_config,
    ):
        """Test editing logging with no changes."""
        mock_select.return_value.ask.side_effect = ["info", "console"]  # Same values

        result = editor._edit_logging(mock_config)

        # No changes made
        assert result is None
