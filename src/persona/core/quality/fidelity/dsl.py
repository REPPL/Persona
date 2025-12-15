"""
YAML constraint DSL parser.

This module parses YAML constraint files into PromptConstraints objects,
providing a user-friendly way to specify fidelity requirements.
"""

from pathlib import Path
from typing import Any

import yaml

from persona.core.quality.fidelity.models import PromptConstraints


class ConstraintParser:
    """
    Parse YAML constraint files into PromptConstraints.

    Supports a declarative YAML DSL for specifying structural,
    content, numeric, and style constraints.
    """

    def parse_file(self, file_path: str | Path) -> PromptConstraints:
        """
        Parse a YAML constraint file.

        Args:
            file_path: Path to YAML constraint file.

        Returns:
            PromptConstraints object.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If YAML is invalid or missing required fields.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Constraint file not found: {file_path}")

        with path.open("r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid YAML: expected dict, got {type(data)}")

        return self.parse_dict(data)

    def parse_dict(self, data: dict[str, Any]) -> PromptConstraints:
        """
        Parse a dictionary into PromptConstraints.

        Args:
            data: Dictionary with constraint data.

        Returns:
            PromptConstraints object.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        # Get constraints section
        constraints_data = data.get("constraints", {})

        if not isinstance(constraints_data, dict):
            raise ValueError(
                f"Invalid constraints: expected dict, got {type(constraints_data)}"
            )

        # Parse structural constraints
        structure = constraints_data.get("structure", {})
        required_fields = structure.get("required_fields", [])
        field_types = structure.get("field_types", {})

        # Parse content constraints
        content = constraints_data.get("content", {})
        occupation_keywords = content.get("occupation_keywords", [])
        goal_themes = content.get("goal_themes", [])
        required_keywords = content.get("required_keywords", {})

        # Parse numeric limits
        limits = constraints_data.get("limits", {})
        age_range = self._parse_range(limits.get("age_range"))
        goal_count = self._parse_range(limits.get("goal_count"))
        pain_point_count = self._parse_range(limits.get("pain_point_count"))
        behaviour_count = self._parse_range(limits.get("behaviour_count"))

        # Parse style constraints
        style_data = constraints_data.get("style", {})
        style_tone = style_data.get("tone")
        complexity = style_data.get("detail_level") or style_data.get("complexity")
        custom_rules = style_data.get("custom_rules", [])

        # Validate types
        if not isinstance(required_fields, list):
            raise ValueError(f"required_fields must be a list, got {type(required_fields)}")

        if not isinstance(field_types, dict):
            raise ValueError(f"field_types must be a dict, got {type(field_types)}")

        return PromptConstraints(
            required_fields=required_fields,
            field_types=field_types,
            age_range=age_range,
            goal_count=goal_count,
            pain_point_count=pain_point_count,
            behaviour_count=behaviour_count,
            complexity=complexity,
            style=style_tone,
            custom_rules=custom_rules,
            required_keywords=required_keywords,
            occupation_keywords=occupation_keywords,
            goal_themes=goal_themes,
        )

    def _parse_range(self, value: Any) -> tuple[int, int] | None:
        """
        Parse a range value from YAML.

        Accepts:
        - [min, max] list
        - {min: x, max: y} dict
        - None

        Args:
            value: Range specification.

        Returns:
            Tuple of (min, max) or None.

        Raises:
            ValueError: If range is invalid.
        """
        if value is None:
            return None

        if isinstance(value, list):
            if len(value) != 2:
                raise ValueError(f"Range must have exactly 2 values, got {len(value)}")
            return (int(value[0]), int(value[1]))

        if isinstance(value, dict):
            if "min" not in value or "max" not in value:
                raise ValueError("Range dict must have 'min' and 'max' keys")
            return (int(value["min"]), int(value["max"]))

        raise ValueError(f"Invalid range format: {value}")

    def to_yaml(self, constraints: PromptConstraints) -> str:
        """
        Convert PromptConstraints back to YAML string.

        Args:
            constraints: PromptConstraints to convert.

        Returns:
            YAML string representation.
        """
        data = {
            "name": "Generated Constraints",
            "constraints": {
                "structure": {},
                "content": {},
                "limits": {},
                "style": {},
            },
        }

        # Structure
        if constraints.required_fields:
            data["constraints"]["structure"]["required_fields"] = constraints.required_fields

        if constraints.field_types:
            data["constraints"]["structure"]["field_types"] = constraints.field_types

        # Content
        if constraints.occupation_keywords:
            data["constraints"]["content"]["occupation_keywords"] = constraints.occupation_keywords

        if constraints.goal_themes:
            data["constraints"]["content"]["goal_themes"] = constraints.goal_themes

        if constraints.required_keywords:
            data["constraints"]["content"]["required_keywords"] = constraints.required_keywords

        # Limits
        if constraints.age_range:
            data["constraints"]["limits"]["age_range"] = list(constraints.age_range)

        if constraints.goal_count:
            data["constraints"]["limits"]["goal_count"] = list(constraints.goal_count)

        if constraints.pain_point_count:
            data["constraints"]["limits"]["pain_point_count"] = list(constraints.pain_point_count)

        if constraints.behaviour_count:
            data["constraints"]["limits"]["behaviour_count"] = list(constraints.behaviour_count)

        # Style
        if constraints.style:
            data["constraints"]["style"]["tone"] = constraints.style

        if constraints.complexity:
            data["constraints"]["style"]["detail_level"] = constraints.complexity

        if constraints.custom_rules:
            data["constraints"]["style"]["custom_rules"] = constraints.custom_rules

        # Remove empty sections
        data["constraints"] = {
            k: v for k, v in data["constraints"].items() if v
        }

        return yaml.dump(data, default_flow_style=False, sort_keys=False)
