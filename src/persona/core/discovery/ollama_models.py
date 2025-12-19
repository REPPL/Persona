"""
Ollama model testing comparison.

This module compares tested Ollama models with available models
from a running Ollama instance and alerts about untested models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from rich.console import Console
from rich.table import Table


class ModelTestStatus(Enum):
    """Status of model testing."""

    TESTED = "tested"
    UNTESTED = "untested"
    UNAVAILABLE = "unavailable"


@dataclass
class OllamaTestedModel:
    """Record of a tested Ollama model."""

    name: str
    tested_date: str
    persona_version: str
    test_result: str = "passed"
    notes: str = ""


@dataclass
class ModelComparisonResult:
    """Result of comparing tested vs available models."""

    tested_models: list[str] = field(default_factory=list)
    available_models: list[str] = field(default_factory=list)
    untested_models: list[str] = field(default_factory=list)
    missing_models: list[str] = field(default_factory=list)
    comparison_time: datetime = field(default_factory=datetime.now)

    @property
    def has_untested_models(self) -> bool:
        """Check if there are untested models available."""
        return len(self.untested_models) > 0

    @property
    def summary(self) -> str:
        """Get a summary of the comparison."""
        lines = [
            f"Tested models: {len(self.tested_models)}",
            f"Available models: {len(self.available_models)}",
            f"New untested models: {len(self.untested_models)}",
            f"Previously tested but now unavailable: {len(self.missing_models)}",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tested_models": self.tested_models,
            "available_models": self.available_models,
            "untested_models": self.untested_models,
            "missing_models": self.missing_models,
            "comparison_time": self.comparison_time.isoformat(),
        }


class OllamaModelRegistry:
    """
    Registry of tested Ollama models.

    Tracks which Ollama models have been tested with Persona
    and provides comparison with available models.
    """

    # Models that have been tested with Persona
    # Format: model_name -> OllamaTestedModel
    TESTED_MODELS: dict[str, OllamaTestedModel] = {
        # Llama family
        "llama3:8b": OllamaTestedModel(
            name="llama3:8b",
            tested_date="2024-11-15",
            persona_version="1.3.0",
            notes="Good for basic persona generation",
        ),
        "llama3:70b": OllamaTestedModel(
            name="llama3:70b",
            tested_date="2024-11-15",
            persona_version="1.3.0",
            notes="High quality, requires significant VRAM",
        ),
        "llama3.2:3b": OllamaTestedModel(
            name="llama3.2:3b",
            tested_date="2024-12-01",
            persona_version="1.5.0",
            notes="Fast, good for hybrid pipeline drafts",
        ),
        # Qwen family
        "qwen2.5:7b": OllamaTestedModel(
            name="qwen2.5:7b",
            tested_date="2024-11-20",
            persona_version="1.4.0",
            notes="Good balance of speed and quality",
        ),
        "qwen2.5:72b": OllamaTestedModel(
            name="qwen2.5:72b",
            tested_date="2024-11-20",
            persona_version="1.4.0",
            notes="Excellent quality, requires significant VRAM",
        ),
        # Mistral family
        "mistral:7b": OllamaTestedModel(
            name="mistral:7b",
            tested_date="2024-11-15",
            persona_version="1.3.0",
            notes="Good general purpose model",
        ),
        "mixtral:8x7b": OllamaTestedModel(
            name="mixtral:8x7b",
            tested_date="2024-11-15",
            persona_version="1.3.0",
            notes="MoE architecture, good quality",
        ),
    }

    def __init__(self) -> None:
        """Initialise the registry."""
        self._ollama_provider = None

    @property
    def tested_model_names(self) -> list[str]:
        """Get list of tested model names."""
        return list(self.TESTED_MODELS.keys())

    def get_tested_model(self, name: str) -> OllamaTestedModel | None:
        """
        Get tested model information.

        Args:
            name: Model name.

        Returns:
            OllamaTestedModel or None if not tested.
        """
        return self.TESTED_MODELS.get(name)

    def is_tested(self, name: str) -> bool:
        """
        Check if a model has been tested.

        Args:
            name: Model name.

        Returns:
            True if model has been tested.
        """
        return name in self.TESTED_MODELS

    def get_available_models(self) -> list[str]:
        """
        Get available models from Ollama.

        Returns:
            List of available model names.

        Raises:
            RuntimeError: If Ollama is not running.
        """
        from persona.core.providers.ollama import OllamaProvider

        if self._ollama_provider is None:
            self._ollama_provider = OllamaProvider()

        return self._ollama_provider.list_available_models()

    def compare_models(self) -> ModelComparisonResult:
        """
        Compare tested models with available Ollama models.

        Returns:
            ModelComparisonResult with comparison details.

        Raises:
            RuntimeError: If Ollama is not running.
        """
        available = self.get_available_models()
        tested = self.tested_model_names

        # Models available but not tested
        untested = [m for m in available if m not in tested]

        # Models tested but not currently available
        missing = [m for m in tested if m not in available]

        return ModelComparisonResult(
            tested_models=tested,
            available_models=available,
            untested_models=untested,
            missing_models=missing,
        )

    def check_for_new_models(self, quiet: bool = False) -> ModelComparisonResult:
        """
        Check for new untested models and optionally alert.

        Args:
            quiet: If True, don't print alerts.

        Returns:
            ModelComparisonResult with comparison details.

        Raises:
            RuntimeError: If Ollama is not running.
        """
        result = self.compare_models()

        if not quiet and result.has_untested_models:
            self._print_alert(result)

        return result

    def _print_alert(self, result: ModelComparisonResult) -> None:
        """Print alert about untested models."""
        console = Console()

        console.print()
        console.print(
            "[bold yellow]New Ollama models detected that haven't been tested:[/]"
        )

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Model Name")
        table.add_column("Status")
        table.add_column("Action")

        for model in result.untested_models:
            table.add_row(
                model,
                "[yellow]Untested[/]",
                "Consider testing with Persona",
            )

        console.print(table)

        console.print()
        console.print(
            f"[dim]Tested models: {len(result.tested_models)}, "
            f"Available: {len(result.available_models)}, "
            f"New: {len(result.untested_models)}[/]"
        )

        if result.missing_models:
            console.print()
            console.print(
                "[dim]Previously tested models no longer available: "
                f"{', '.join(result.missing_models)}[/]"
            )


def compare_ollama_models(quiet: bool = False) -> ModelComparisonResult:
    """
    Compare tested models with available Ollama models.

    This is a convenience function to quickly check for new untested models.

    Args:
        quiet: If True, don't print alerts.

    Returns:
        ModelComparisonResult with comparison details.

    Raises:
        RuntimeError: If Ollama is not running.

    Example:
        >>> result = compare_ollama_models()
        >>> if result.has_untested_models:
        ...     print(f"New models: {result.untested_models}")
    """
    registry = OllamaModelRegistry()
    return registry.check_for_new_models(quiet=quiet)


def get_untested_models() -> list[str]:
    """
    Get list of available but untested Ollama models.

    Returns:
        List of untested model names.

    Raises:
        RuntimeError: If Ollama is not running.

    Example:
        >>> untested = get_untested_models()
        >>> print(f"Models to test: {untested}")
    """
    registry = OllamaModelRegistry()
    result = registry.compare_models()
    return result.untested_models
