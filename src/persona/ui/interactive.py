"""
Interactive mode for Persona CLI (F-092).

Provides questionary-based prompts for guided user interaction.
"""

import sys
from pathlib import Path
from typing import Optional

import questionary
from questionary import Choice
from rich.console import Console

from persona.core.cost import PricingData
from persona.core.providers import ProviderFactory


def is_interactive_supported() -> bool:
    """Check if interactive mode is supported in current environment.

    Interactive mode requires a TTY. In pipes, redirects, or non-interactive
    shells, we return False and commands should use defaults or explicit flags.
    """
    return sys.stdin.isatty() and sys.stdout.isatty()


def get_configured_providers() -> list[tuple[str, str, bool]]:
    """Get list of providers with their configuration status.

    Returns:
        List of (provider_name, display_name, is_configured) tuples.
    """
    providers = [
        ("anthropic", "Anthropic (Claude)"),
        ("openai", "OpenAI (GPT)"),
        ("gemini", "Google (Gemini)"),
    ]

    result = []
    for name, display in providers:
        try:
            provider = ProviderFactory.create(name)
            is_configured = provider.is_configured()
        except (ValueError, ImportError, OSError):
            # Provider unavailable or not properly installed
            is_configured = False
        result.append((name, display, is_configured))

    return result


def get_models_for_provider(provider: str) -> list[tuple[str, str, bool]]:
    """Get available models for a provider.

    Returns:
        List of (model_id, display_name, is_default) tuples.
    """
    # Default models per provider
    defaults = {
        "anthropic": "claude-sonnet-4-20250514",
        "openai": "gpt-4o",
        "gemini": "gemini-2.0-flash",
    }

    models = []
    for pricing in PricingData.list_models(provider=provider):
        is_default = pricing.model == defaults.get(provider, "")
        # Format display with price
        display = f"{pricing.model} (${float(pricing.input_price):.2f}/${float(pricing.output_price):.2f} per M)"
        if is_default:
            display += " ✓"
        models.append((pricing.model, display, is_default))

    # Sort with default first
    models.sort(key=lambda x: (not x[2], x[0]))
    return models


class InteractivePrompts:
    """Interactive prompts for Persona CLI."""

    def __init__(self, console: Optional[Console] = None):
        """Initialise prompts.

        Args:
            console: Rich console for output (optional).
        """
        self.console = console or Console()

    def select_provider(self, default: Optional[str] = None) -> Optional[str]:
        """Prompt user to select an LLM provider.

        Args:
            default: Default provider to pre-select.

        Returns:
            Selected provider name or None if cancelled.
        """
        providers = get_configured_providers()

        # Build choices with status indicators
        choices = []
        for name, display, configured in providers:
            status = "✓" if configured else "○ not configured"
            label = f"{display} {status}"
            choices.append(Choice(title=label, value=name, disabled=not configured))

        # Find default index
        default_value = default
        if not default_value:
            # Use first configured provider as default
            for name, _, configured in providers:
                if configured:
                    default_value = name
                    break

        result = questionary.select(
            "Select LLM provider:",
            choices=choices,
            default=default_value,
        ).ask()

        return result

    def select_model(
        self, provider: str, default: Optional[str] = None
    ) -> Optional[str]:
        """Prompt user to select a model.

        Args:
            provider: Provider name to get models for.
            default: Default model to pre-select.

        Returns:
            Selected model ID or None if cancelled.
        """
        models = get_models_for_provider(provider)

        if not models:
            self.console.print(f"[yellow]No models found for {provider}[/yellow]")
            return None

        choices = [
            Choice(title=display, value=model_id) for model_id, display, _ in models
        ]

        # Find default
        default_value = default
        if not default_value:
            for model_id, _, is_default in models:
                if is_default:
                    default_value = model_id
                    break

        result = questionary.select(
            "Select model:",
            choices=choices,
            default=default_value,
        ).ask()

        return result

    def input_count(self, default: int = 3) -> Optional[int]:
        """Prompt user for persona count.

        Args:
            default: Default count.

        Returns:
            Count or None if cancelled.
        """
        result = questionary.text(
            "Number of personas to generate:",
            default=str(default),
            validate=lambda x: x.isdigit() and int(x) > 0,
        ).ask()

        if result is None:
            return None
        return int(result)

    def input_path(
        self,
        message: str = "Data file or directory:",
        default: str = "",
        must_exist: bool = True,
    ) -> Optional[Path]:
        """Prompt user for a file path with autocomplete.

        Args:
            message: Prompt message.
            default: Default path.
            must_exist: Whether path must exist.

        Returns:
            Path or None if cancelled.
        """

        def validate_path(text: str) -> bool | str:
            if not text:
                return "Path cannot be empty"
            path = Path(text).expanduser()
            if must_exist and not path.exists():
                return f"Path does not exist: {text}"
            return True

        result = questionary.path(
            message,
            default=default,
            validate=validate_path,
        ).ask()

        if result is None:
            return None
        return Path(result).expanduser()

    def select_output_format(self, default: str = "json") -> Optional[str]:
        """Prompt user to select output format.

        Args:
            default: Default format.

        Returns:
            Selected format or None if cancelled.
        """
        choices = [
            Choice(title="JSON (structured data)", value="json"),
            Choice(title="Markdown (human-readable)", value="markdown"),
            Choice(title="YAML (configuration-friendly)", value="yaml"),
        ]

        result = questionary.select(
            "Output format:",
            choices=choices,
            default=default,
        ).ask()

        return result

    def select_workflow(self, default: str = "default") -> Optional[str]:
        """Prompt user to select a workflow.

        Args:
            default: Default workflow.

        Returns:
            Selected workflow or None if cancelled.
        """
        choices = [
            Choice(title="Default (balanced)", value="default"),
            Choice(title="Research (detailed, methodical)", value="research"),
            Choice(title="Quick (fast, minimal)", value="quick"),
        ]

        result = questionary.select(
            "Workflow:",
            choices=choices,
            default=default,
        ).ask()

        return result

    def confirm(
        self,
        message: str,
        default: bool = True,
    ) -> Optional[bool]:
        """Prompt user for confirmation.

        Args:
            message: Confirmation message.
            default: Default choice.

        Returns:
            True/False or None if cancelled.
        """
        result = questionary.confirm(
            message,
            default=default,
        ).ask()

        return result

    def input_text(
        self,
        message: str,
        default: str = "",
        secret: bool = False,
    ) -> Optional[str]:
        """Prompt user for text input.

        Args:
            message: Prompt message.
            default: Default value.
            secret: Whether to hide input (for API keys).

        Returns:
            Input text or None if cancelled.
        """
        if secret:
            result = questionary.password(message).ask()
        else:
            result = questionary.text(message, default=default).ask()

        return result


class GenerateWizard:
    """Interactive wizard for persona generation."""

    def __init__(self, console: Optional[Console] = None):
        """Initialise wizard.

        Args:
            console: Rich console for output.
        """
        self.console = console or Console()
        self.prompts = InteractivePrompts(console=self.console)

    def run(
        self,
        data_path: Optional[Path] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        count: Optional[int] = None,
        workflow: Optional[str] = None,
    ) -> Optional[dict]:
        """Run the generation wizard.

        Pre-filled values skip their prompts. Returns None if user cancels.

        Args:
            data_path: Pre-filled data path.
            provider: Pre-filled provider.
            model: Pre-filled model.
            count: Pre-filled count.
            workflow: Pre-filled workflow.

        Returns:
            Dictionary with generation parameters or None if cancelled.
        """
        from persona import __version__

        self.console.print(f"[dim]Persona {__version__}[/dim]\n")
        self.console.print("[bold]Generate Personas - Interactive Mode[/bold]\n")

        # Data path
        if data_path is None:
            data_path = self.prompts.input_path(
                "Data file or directory:",
                default="./data/",
            )
            if data_path is None:
                return None

        # Provider
        if provider is None:
            provider = self.prompts.select_provider()
            if provider is None:
                return None

        # Model
        if model is None:
            model = self.prompts.select_model(provider)
            if model is None:
                return None

        # Count
        if count is None:
            count = self.prompts.input_count(default=3)
            if count is None:
                return None

        # Workflow
        if workflow is None:
            workflow = self.prompts.select_workflow()
            if workflow is None:
                return None

        # Show summary and confirm
        self.console.print("\n[bold]Generation Summary:[/bold]")
        self.console.print(f"  Data source: {data_path}")
        self.console.print(f"  Provider: {provider}")
        self.console.print(f"  Model: {model}")
        self.console.print(f"  Count: {count}")
        self.console.print(f"  Workflow: {workflow}")

        # Estimate cost
        from persona.core.cost import CostEstimator
        from persona.core.data import DataLoader

        try:
            loader = DataLoader()
            if data_path.is_dir():
                data = loader.load_directory(data_path)
            else:
                data = loader.load_file(data_path)
            tokens = loader.count_tokens(data)

            estimator = CostEstimator()
            estimate = estimator.estimate(
                model=model,
                input_tokens=tokens,
                persona_count=count,
                provider=provider,
            )
            if estimate.pricing:
                self.console.print(
                    f"  Estimated cost: {estimator.format_cost(estimate.total_cost)}"
                )
        except (ValueError, KeyError, AttributeError):
            # Cost estimate is optional - continue if pricing data unavailable
            pass

        self.console.print()

        if not self.prompts.confirm("Proceed with generation?"):
            self.console.print("[yellow]Cancelled.[/yellow]")
            return None

        return {
            "data_path": data_path,
            "provider": provider,
            "model": model,
            "count": count,
            "workflow": workflow,
        }


class ConfigWizard:
    """Interactive wizard for configuration."""

    def __init__(self, console: Optional[Console] = None):
        """Initialise wizard.

        Args:
            console: Rich console for output.
        """
        self.console = console or Console()
        self.prompts = InteractivePrompts(console=self.console)

    def run(self) -> Optional[dict]:
        """Run the configuration wizard.

        Returns:
            Dictionary with configuration values or None if cancelled.
        """
        from persona import __version__

        self.console.print(f"[dim]Persona {__version__}[/dim]\n")
        self.console.print("[bold]Configure Persona - Interactive Mode[/bold]\n")

        # What to configure
        section = questionary.select(
            "What would you like to configure?",
            choices=[
                Choice(title="Default provider and model", value="defaults"),
                Choice(title="Budget limits", value="budgets"),
                Choice(title="Output preferences", value="output"),
                Choice(title="Logging settings", value="logging"),
            ],
        ).ask()

        if section is None:
            return None

        if section == "defaults":
            return self._configure_defaults()
        elif section == "budgets":
            return self._configure_budgets()
        elif section == "output":
            return self._configure_output()
        elif section == "logging":
            return self._configure_logging()

        return None

    def _configure_defaults(self) -> Optional[dict]:
        """Configure default provider and model."""
        provider = self.prompts.select_provider()
        if provider is None:
            return None

        model = self.prompts.select_model(provider)
        if model is None:
            return None

        count = self.prompts.input_count(default=3)
        if count is None:
            return None

        return {
            "section": "defaults",
            "provider": provider,
            "model": model,
            "count": count,
        }

    def _configure_budgets(self) -> Optional[dict]:
        """Configure budget limits."""
        per_run = questionary.text(
            "Maximum cost per run ($):",
            default="5.00",
            validate=lambda x: _is_float(x) and float(x) > 0,
        ).ask()
        if per_run is None:
            return None

        daily = questionary.text(
            "Daily budget limit ($):",
            default="25.00",
            validate=lambda x: _is_float(x) and float(x) > 0,
        ).ask()
        if daily is None:
            return None

        monthly = questionary.text(
            "Monthly budget limit ($):",
            default="100.00",
            validate=lambda x: _is_float(x) and float(x) > 0,
        ).ask()
        if monthly is None:
            return None

        return {
            "section": "budgets",
            "per_run": float(per_run),
            "daily": float(daily),
            "monthly": float(monthly),
        }

    def _configure_output(self) -> Optional[dict]:
        """Configure output preferences."""
        output_format = self.prompts.select_output_format()
        if output_format is None:
            return None

        include_readme = self.prompts.confirm(
            "Generate README with output?",
            default=True,
        )
        if include_readme is None:
            return None

        timestamp_folders = self.prompts.confirm(
            "Use timestamp folders for output?",
            default=True,
        )
        if timestamp_folders is None:
            return None

        return {
            "section": "output",
            "format": output_format,
            "include_readme": include_readme,
            "timestamp_folders": timestamp_folders,
        }

    def _configure_logging(self) -> Optional[dict]:
        """Configure logging settings."""
        level = questionary.select(
            "Log level:",
            choices=[
                Choice(title="Debug (most verbose)", value="debug"),
                Choice(title="Info (default)", value="info"),
                Choice(title="Warning", value="warning"),
                Choice(title="Error (least verbose)", value="error"),
            ],
            default="info",
        ).ask()
        if level is None:
            return None

        log_format = questionary.select(
            "Log format:",
            choices=[
                Choice(title="Console (human-readable)", value="console"),
                Choice(title="JSON (structured)", value="json"),
            ],
            default="console",
        ).ask()
        if log_format is None:
            return None

        return {
            "section": "logging",
            "level": level,
            "format": log_format,
        }


def _is_float(value: str) -> bool:
    """Check if string is a valid float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


class ConfigEditor:
    """Form-based configuration editor (F-093).

    Provides a comprehensive TUI editor for all Persona configuration options.
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        project_level: bool = False,
    ):
        """Initialise editor.

        Args:
            console: Rich console for output.
            project_level: Whether editing project or global config.
        """
        self.console = console or Console()
        self.prompts = InteractivePrompts(console=self.console)
        self.project_level = project_level

    def run(self, section: Optional[str] = None) -> Optional[dict]:
        """Run the configuration editor.

        Args:
            section: Specific section to edit (defaults, budgets, output, logging).
                    If None, allows user to select section.

        Returns:
            Dictionary with configuration changes or None if cancelled.
        """
        from persona import __version__
        from persona.core.config.global_config import get_config_manager

        self.console.print(f"[dim]Persona {__version__}[/dim]\n")
        config_type = "Project" if self.project_level else "Global"
        self.console.print(f"[bold]Configuration Editor ({config_type})[/bold]\n")

        # Load current configuration
        manager = get_config_manager()
        current_config = manager.load()

        # Show current values
        self._show_current_config(current_config)

        # Select section to edit
        if section is None:
            section = questionary.select(
                "Select section to edit:",
                choices=[
                    Choice(title="Provider & Model Defaults", value="defaults"),
                    Choice(title="Budget Limits", value="budgets"),
                    Choice(title="Output Preferences", value="output"),
                    Choice(title="Logging Settings", value="logging"),
                    Choice(title="All sections", value="all"),
                    Choice(title="Reset to defaults", value="reset"),
                ],
            ).ask()

        if section is None:
            self.console.print("[yellow]Cancelled.[/yellow]")
            return None

        if section == "reset":
            if self.prompts.confirm("Reset all settings to defaults?", default=False):
                return self._reset_all()
            return None

        if section == "all":
            return self._edit_all(current_config)

        return self._edit_section(section, current_config)

    def _show_current_config(self, config) -> None:
        """Display current configuration values."""
        self.console.print("[bold]Current Configuration:[/bold]")

        self.console.print("\n[dim]Defaults:[/dim]")
        self.console.print(f"  provider: {config.defaults.provider}")
        self.console.print(f"  model: {config.defaults.model or 'auto'}")
        self.console.print(f"  count: {config.defaults.count}")
        self.console.print(f"  complexity: {config.defaults.complexity}")
        self.console.print(f"  detail_level: {config.defaults.detail_level}")

        self.console.print("\n[dim]Budgets:[/dim]")
        self.console.print(f"  per_run: ${config.budgets.per_run or 'not set'}")
        self.console.print(f"  daily: ${config.budgets.daily or 'not set'}")
        self.console.print(f"  monthly: ${config.budgets.monthly or 'not set'}")

        self.console.print("\n[dim]Output:[/dim]")
        self.console.print(f"  format: {config.output.format}")
        self.console.print(f"  include_readme: {config.output.include_readme}")
        self.console.print(f"  timestamp_folders: {config.output.timestamp_folders}")

        self.console.print("\n[dim]Logging:[/dim]")
        self.console.print(f"  level: {config.logging.level}")
        self.console.print(f"  format: {config.logging.format}")
        self.console.print()

    def _edit_section(self, section: str, config) -> Optional[dict]:
        """Edit a specific configuration section."""
        if section == "defaults":
            return self._edit_defaults(config)
        elif section == "budgets":
            return self._edit_budgets(config)
        elif section == "output":
            return self._edit_output(config)
        elif section == "logging":
            return self._edit_logging(config)
        return None

    def _edit_all(self, config) -> Optional[dict]:
        """Edit all configuration sections."""
        result = {}

        self.console.print("[bold]Editing all sections...[/bold]\n")

        # Defaults
        defaults = self._edit_defaults(config)
        if defaults:
            result.update(defaults)

        # Budgets
        budgets = self._edit_budgets(config)
        if budgets:
            result.update(budgets)

        # Output
        output = self._edit_output(config)
        if output:
            result.update(output)

        # Logging
        logging_settings = self._edit_logging(config)
        if logging_settings:
            result.update(logging_settings)

        if not result:
            return None

        # Preview changes
        self.console.print("\n[bold]Changes to apply:[/bold]")
        for key, value in result.items():
            self.console.print(f"  {key}: {value}")

        if not self.prompts.confirm("\nApply these changes?"):
            self.console.print("[yellow]Cancelled.[/yellow]")
            return None

        return result

    def _edit_defaults(self, config) -> Optional[dict]:
        """Edit default provider and generation settings."""
        self.console.print("\n[bold]Provider & Model Defaults[/bold]")

        result = {}

        # Provider
        provider = self.prompts.select_provider(default=config.defaults.provider)
        if provider and provider != config.defaults.provider:
            result["defaults.provider"] = provider

        # Model
        if provider:
            current_model = config.defaults.model
            model = self.prompts.select_model(provider, default=current_model)
            if model and model != current_model:
                result["defaults.model"] = model

        # Count
        count_str = questionary.text(
            "Default persona count:",
            default=str(config.defaults.count),
            validate=lambda x: x.isdigit() and 1 <= int(x) <= 20,
        ).ask()
        if count_str:
            count = int(count_str)
            if count != config.defaults.count:
                result["defaults.count"] = count

        # Complexity
        complexity = questionary.select(
            "Default complexity:",
            choices=[
                Choice(title="Simple (fast)", value="simple"),
                Choice(title="Moderate (balanced)", value="moderate"),
                Choice(title="Complex (thorough)", value="complex"),
            ],
            default=config.defaults.complexity,
        ).ask()
        if complexity and complexity != config.defaults.complexity:
            result["defaults.complexity"] = complexity

        # Detail level
        detail_level = questionary.select(
            "Default detail level:",
            choices=[
                Choice(title="Minimal", value="minimal"),
                Choice(title="Standard", value="standard"),
                Choice(title="Detailed", value="detailed"),
            ],
            default=config.defaults.detail_level,
        ).ask()
        if detail_level and detail_level != config.defaults.detail_level:
            result["defaults.detail_level"] = detail_level

        return result if result else None

    def _edit_budgets(self, config) -> Optional[dict]:
        """Edit budget limits."""
        self.console.print("\n[bold]Budget Limits[/bold]")

        result = {}

        # Per-run budget
        per_run_str = questionary.text(
            "Per-run budget ($, or 'none' to disable):",
            default=str(config.budgets.per_run or "none"),
            validate=lambda x: x.lower() == "none" or (_is_float(x) and float(x) > 0),
        ).ask()
        if per_run_str:
            if per_run_str.lower() == "none":
                if config.budgets.per_run is not None:
                    result["budgets.per_run"] = None
            else:
                per_run = float(per_run_str)
                if per_run != config.budgets.per_run:
                    result["budgets.per_run"] = per_run

        # Daily budget
        daily_str = questionary.text(
            "Daily budget ($, or 'none' to disable):",
            default=str(config.budgets.daily or "none"),
            validate=lambda x: x.lower() == "none" or (_is_float(x) and float(x) > 0),
        ).ask()
        if daily_str:
            if daily_str.lower() == "none":
                if config.budgets.daily is not None:
                    result["budgets.daily"] = None
            else:
                daily = float(daily_str)
                if daily != config.budgets.daily:
                    result["budgets.daily"] = daily

        # Monthly budget
        monthly_str = questionary.text(
            "Monthly budget ($, or 'none' to disable):",
            default=str(config.budgets.monthly or "none"),
            validate=lambda x: x.lower() == "none" or (_is_float(x) and float(x) > 0),
        ).ask()
        if monthly_str:
            if monthly_str.lower() == "none":
                if config.budgets.monthly is not None:
                    result["budgets.monthly"] = None
            else:
                monthly = float(monthly_str)
                if monthly != config.budgets.monthly:
                    result["budgets.monthly"] = monthly

        return result if result else None

    def _edit_output(self, config) -> Optional[dict]:
        """Edit output preferences."""
        self.console.print("\n[bold]Output Preferences[/bold]")

        result = {}

        # Format
        output_format = questionary.select(
            "Default output format:",
            choices=[
                Choice(title="JSON", value="json"),
                Choice(title="Markdown", value="markdown"),
                Choice(title="YAML", value="yaml"),
            ],
            default=config.output.format,
        ).ask()
        if output_format and output_format != config.output.format:
            result["output.format"] = output_format

        # Include README
        include_readme = questionary.confirm(
            "Generate README with output?",
            default=config.output.include_readme,
        ).ask()
        if (
            include_readme is not None
            and include_readme != config.output.include_readme
        ):
            result["output.include_readme"] = include_readme

        # Timestamp folders
        timestamp_folders = questionary.confirm(
            "Use timestamp folders?",
            default=config.output.timestamp_folders,
        ).ask()
        if (
            timestamp_folders is not None
            and timestamp_folders != config.output.timestamp_folders
        ):
            result["output.timestamp_folders"] = timestamp_folders

        return result if result else None

    def _edit_logging(self, config) -> Optional[dict]:
        """Edit logging settings."""
        self.console.print("\n[bold]Logging Settings[/bold]")

        result = {}

        # Level
        level = questionary.select(
            "Log level:",
            choices=[
                Choice(title="Debug (most verbose)", value="debug"),
                Choice(title="Info", value="info"),
                Choice(title="Warning", value="warning"),
                Choice(title="Error (least verbose)", value="error"),
            ],
            default=config.logging.level,
        ).ask()
        if level and level != config.logging.level:
            result["logging.level"] = level

        # Format
        log_format = questionary.select(
            "Log format:",
            choices=[
                Choice(title="Console (human-readable)", value="console"),
                Choice(title="JSON (structured)", value="json"),
            ],
            default=config.logging.format,
        ).ask()
        if log_format and log_format != config.logging.format:
            result["logging.format"] = log_format

        return result if result else None

    def _reset_all(self) -> dict:
        """Return reset values for all settings."""
        return {
            "defaults.provider": "anthropic",
            "defaults.model": None,
            "defaults.count": 3,
            "defaults.complexity": "moderate",
            "defaults.detail_level": "standard",
            "defaults.workflow": "default",
            "budgets.per_run": None,
            "budgets.daily": None,
            "budgets.monthly": None,
            "output.format": "json",
            "output.include_readme": True,
            "output.timestamp_folders": True,
            "logging.level": "info",
            "logging.format": "console",
        }
