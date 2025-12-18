"""
Jinja2-based prompt template handling.

This module provides the PromptTemplate class for rendering prompts
with variable injection.
"""

from pathlib import Path
from typing import Any

from jinja2 import BaseLoader, Environment, StrictUndefined, TemplateError


class StringLoader(BaseLoader):
    """Jinja2 loader for string templates."""

    def get_source(self, environment: Environment, template: str):
        """Return the template source."""
        return template, None, lambda: True


class PromptTemplate:
    """
    Jinja2-based prompt template.

    Supports variable injection, conditional sections, and loops.

    Example:
        template = PromptTemplate('''
            Generate {{ count }} personas from the following data:
            {{ data }}
        ''')
        prompt = template.render(count=3, data="Interview transcripts...")
    """

    def __init__(self, template_string: str) -> None:
        """
        Create a prompt template from a string.

        Args:
            template_string: Jinja2 template string.
        """
        self._template_string = template_string
        self._env = Environment(
            loader=StringLoader(),
            undefined=StrictUndefined,
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._template = self._env.from_string(template_string)

    @classmethod
    def from_file(cls, path: str | Path) -> "PromptTemplate":
        """
        Load a template from a file.

        Args:
            path: Path to the template file.

        Returns:
            PromptTemplate instance.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")

        template_string = path.read_text(encoding="utf-8")
        return cls(template_string)

    def render(self, **variables: Any) -> str:
        """
        Render the template with the given variables.

        Args:
            **variables: Template variables to inject.

        Returns:
            Rendered prompt string.

        Raises:
            TemplateError: If rendering fails (e.g., undefined variable).
        """
        try:
            return self._template.render(**variables)
        except TemplateError as e:
            raise TemplateError(f"Template rendering failed: {e}")

    def get_variables(self) -> list[str]:
        """
        Get list of variables used in the template.

        Returns:
            List of variable names.
        """
        from jinja2 import meta

        ast = self._env.parse(self._template_string)
        return list(meta.find_undeclared_variables(ast))

    def validate(self, **variables: Any) -> bool:
        """
        Validate that all required variables are provided.

        Args:
            **variables: Variables to validate.

        Returns:
            True if all required variables are present.

        Raises:
            ValueError: If required variables are missing.
        """
        required = set(self.get_variables())
        provided = set(variables.keys())
        missing = required - provided

        if missing:
            raise ValueError(
                f"Missing required variables: {', '.join(sorted(missing))}"
            )

        return True

    @property
    def template_string(self) -> str:
        """Return the original template string."""
        return self._template_string


# Default prompt templates
DEFAULT_PERSONA_TEMPLATE = """You are an expert UX researcher specialising in persona development.

Analyse the following user research data and generate {{ count }} distinct user personas.

## Research Data

{{ data }}

## Requirements

Generate {{ count }} personas that:
1. Are distinct from each other (representing different user segments)
2. Are grounded in evidence from the research data
3. Include realistic details that bring them to life

{% if complexity == 'simple' %}
Keep the personas concise with key attributes only.
{% elif complexity == 'complex' %}
Create detailed personas with comprehensive background information.
{% else %}
Create moderately detailed personas balancing depth with readability.
{% endif %}

{% if detail_level == 'minimal' %}
Include only essential information: name, role, key goals, main pain points.
{% elif detail_level == 'detailed' %}
Include comprehensive information: demographics, behaviours, quotes, scenarios.
{% else %}
Include standard information: demographics, goals, pain points, behaviours.
{% endif %}

## Output Format

Respond with valid JSON in this structure:
```json
{
  "personas": [
    {
      "id": "persona-001",
      "name": "Name",
      "demographics": {
        "age_range": "25-34",
        "occupation": "Job Title",
        "location": "Location Type"
      },
      "goals": ["Goal 1", "Goal 2"],
      "pain_points": ["Pain point 1", "Pain point 2"],
      "behaviours": ["Behaviour 1", "Behaviour 2"],
      "quotes": ["Quote from research data"]
    }
  ]
}
```

Wrap your response in <output></output> tags.
{% if include_reasoning %}
Before the output, include your reasoning in <reasoning></reasoning> tags.
{% endif %}
"""
