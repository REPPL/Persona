"""
Workflow configuration and loading.

This module provides workflow definitions that combine prompts,
models, and generation settings.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from persona.core.prompts.template import DEFAULT_PERSONA_TEMPLATE, PromptTemplate


@dataclass
class Workflow:
    """
    Workflow configuration for persona generation.

    A workflow defines the prompt template, model settings, and
    output configuration for a generation run.

    Attributes:
        name: Workflow identifier.
        description: Human-readable description.
        template: Prompt template to use.
        provider: Default LLM provider.
        model: Default model identifier.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
        variables: Default variable values.
    """

    name: str
    description: str = ""
    template: PromptTemplate = field(
        default_factory=lambda: PromptTemplate(DEFAULT_PERSONA_TEMPLATE)
    )
    provider: str = "anthropic"
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    variables: dict[str, Any] = field(default_factory=dict)

    def render_prompt(self, **kwargs: Any) -> str:
        """
        Render the workflow prompt with variables.

        Args:
            **kwargs: Variables to inject into the template.

        Returns:
            Rendered prompt string.
        """
        # Merge default variables with provided ones
        merged = {**self.variables, **kwargs}
        return self.template.render(**merged)


class WorkflowLoader:
    """
    Loader for workflow configurations from YAML files.

    Example:
        loader = WorkflowLoader()
        workflow = loader.load("workflows/research.yaml")
    """

    # Built-in workflow definitions
    BUILTIN_WORKFLOWS = {
        "default": {
            "name": "default",
            "description": "Standard persona generation workflow",
            "provider": "anthropic",
            "temperature": 0.7,
            "max_tokens": 4096,
            "variables": {
                "complexity": "moderate",
                "detail_level": "standard",
                "include_reasoning": False,
            },
        },
        "research": {
            "name": "research",
            "description": "Research-focused workflow with detailed reasoning",
            "provider": "anthropic",
            "temperature": 0.5,
            "max_tokens": 8192,
            "variables": {
                "complexity": "complex",
                "detail_level": "detailed",
                "include_reasoning": True,
            },
        },
        "quick": {
            "name": "quick",
            "description": "Fast generation with minimal output",
            "provider": "openai",
            "temperature": 0.8,
            "max_tokens": 2048,
            "variables": {
                "complexity": "simple",
                "detail_level": "minimal",
                "include_reasoning": False,
            },
        },
    }

    def load(self, path: str | Path) -> Workflow:
        """
        Load a workflow from a YAML file.

        Args:
            path: Path to the workflow YAML file.

        Returns:
            Workflow instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the YAML is invalid.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {path}")

        with open(path, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not config:
            raise ValueError(f"Empty workflow file: {path}")

        return self._create_workflow(config)

    def load_builtin(self, name: str) -> Workflow:
        """
        Load a built-in workflow by name.

        Args:
            name: Name of the built-in workflow.

        Returns:
            Workflow instance.

        Raises:
            ValueError: If the workflow name is not recognised.
        """
        if name not in self.BUILTIN_WORKFLOWS:
            available = ", ".join(self.list_builtin())
            raise ValueError(
                f"Unknown built-in workflow: {name}. " f"Available: {available}"
            )

        config = self.BUILTIN_WORKFLOWS[name].copy()
        return self._create_workflow(config)

    def list_builtin(self) -> list[str]:
        """
        List available built-in workflows.

        Returns:
            List of workflow names.
        """
        return list(self.BUILTIN_WORKFLOWS.keys())

    def _create_workflow(self, config: dict[str, Any]) -> Workflow:
        """Create a Workflow from a config dictionary."""
        # Handle template - can be string or file path
        template_config = config.get("template")
        if template_config:
            if isinstance(template_config, str):
                # Check if it's a file path
                if Path(template_config).exists():
                    template = PromptTemplate.from_file(template_config)
                else:
                    template = PromptTemplate(template_config)
            else:
                template = PromptTemplate(DEFAULT_PERSONA_TEMPLATE)
        else:
            template = PromptTemplate(DEFAULT_PERSONA_TEMPLATE)

        return Workflow(
            name=config.get("name", "custom"),
            description=config.get("description", ""),
            template=template,
            provider=config.get("provider", "anthropic"),
            model=config.get("model"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 4096),
            variables=config.get("variables", {}),
        )

    def create_from_dict(self, config: dict[str, Any]) -> Workflow:
        """
        Create a workflow from a dictionary configuration.

        Args:
            config: Workflow configuration dictionary.

        Returns:
            Workflow instance.
        """
        return self._create_workflow(config)
