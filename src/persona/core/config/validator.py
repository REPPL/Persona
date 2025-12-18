"""
Configuration validation (F-055).

Provides comprehensive validation for all configuration types
with schema validation, semantic validation, and cross-reference checking.
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class ValidationLevel(Enum):
    """Validation severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue."""

    level: ValidationLevel
    field: str
    message: str
    line_number: int | None = None
    suggestion: str | None = None
    file_path: Path | None = None

    def __str__(self) -> str:
        parts = []
        if self.file_path:
            parts.append(str(self.file_path))
        if self.line_number:
            parts.append(f"line {self.line_number}")

        location = ":".join(parts) if parts else ""
        prefix = f"[{location}] " if location else ""

        msg = f"{prefix}{self.level.value.upper()}: {self.field}: {self.message}"
        if self.suggestion:
            msg += f" (Suggestion: {self.suggestion})"
        return msg


@dataclass
class ValidationResult:
    """Result of configuration validation."""

    is_valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    config_type: str = ""
    file_path: Path | None = None

    @property
    def errors(self) -> list[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.level == ValidationLevel.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.level == ValidationLevel.WARNING]

    def add_error(
        self,
        field: str,
        message: str,
        line_number: int | None = None,
        suggestion: str | None = None,
    ) -> None:
        """Add an error."""
        self.issues.append(
            ValidationIssue(
                level=ValidationLevel.ERROR,
                field=field,
                message=message,
                line_number=line_number,
                suggestion=suggestion,
                file_path=self.file_path,
            )
        )
        self.is_valid = False

    def add_warning(
        self,
        field: str,
        message: str,
        line_number: int | None = None,
        suggestion: str | None = None,
    ) -> None:
        """Add a warning."""
        self.issues.append(
            ValidationIssue(
                level=ValidationLevel.WARNING,
                field=field,
                message=message,
                line_number=line_number,
                suggestion=suggestion,
                file_path=self.file_path,
            )
        )

    def merge(self, other: "ValidationResult") -> None:
        """Merge another result into this one."""
        self.issues.extend(other.issues)
        if not other.is_valid:
            self.is_valid = False


# JSON Schema definitions for configuration types
VENDOR_SCHEMA = {
    "type": "object",
    "required": ["name", "api_base"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "api_base": {"type": "string", "pattern": "^https://"},
        "auth_env": {"type": "string"},
        "auth_header": {"type": "string"},
        "models": {
            "type": "array",
            "items": {"type": "string"},
        },
        "rate_limits": {
            "type": "object",
            "properties": {
                "requests_per_minute": {"type": "integer", "minimum": 1},
                "tokens_per_minute": {"type": "integer", "minimum": 1},
            },
        },
    },
}

MODEL_SCHEMA = {
    "type": "object",
    "required": ["name", "provider"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "provider": {"type": "string", "minLength": 1},
        "context_window": {"type": "integer", "minimum": 1},
        "input_price": {"type": "number", "minimum": 0},
        "output_price": {"type": "number", "minimum": 0},
        "capabilities": {
            "type": "array",
            "items": {"type": "string"},
        },
        "deprecated": {"type": "boolean"},
    },
}

EXPERIMENT_SCHEMA = {
    "type": "object",
    "required": ["name"],
    "properties": {
        "name": {"type": "string", "minLength": 1, "pattern": "^[a-zA-Z0-9_-]+$"},
        "provider": {"type": "string"},
        "model": {"type": "string"},
        "count": {"type": "integer", "minimum": 1, "maximum": 100},
        "complexity": {"type": "string", "enum": ["simple", "moderate", "complex"]},
        "detail": {
            "type": "string",
            "enum": ["minimal", "standard", "detailed", "comprehensive"],
        },
        "template": {"type": "string"},
        "workflow": {"type": "string"},
    },
}

TEMPLATE_SCHEMA = {
    "type": "object",
    "required": ["name"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "variables": {
            "type": "array",
            "items": {"type": "string"},
        },
        "content": {"type": "string"},
    },
}

WORKFLOW_SCHEMA = {
    "type": "object",
    "required": ["name", "steps"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "steps": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string"},
                    "template": {"type": "string"},
                    "output": {"type": "string"},
                },
            },
        },
    },
}


class ConfigValidator:
    """
    Validates configuration files for Persona.

    Performs three layers of validation:
    1. Schema validation (structure, types, required fields)
    2. Semantic validation (valid values, ranges, patterns)
    3. Cross-reference validation (model exists, provider configured)

    Example:
        validator = ConfigValidator()
        result = validator.validate_file(Path("experiment.yaml"))
        if not result.is_valid:
            for error in result.errors:
                print(error)
    """

    # Schema mapping for config types
    SCHEMAS: dict[str, dict] = {
        "vendor": VENDOR_SCHEMA,
        "model": MODEL_SCHEMA,
        "experiment": EXPERIMENT_SCHEMA,
        "template": TEMPLATE_SCHEMA,
        "workflow": WORKFLOW_SCHEMA,
    }

    # Known providers
    KNOWN_PROVIDERS = {"openai", "anthropic", "gemini", "google"}

    # Known models (prefixes)
    KNOWN_MODEL_PREFIXES = {"gpt-", "claude-", "gemini-", "o1-", "o3-"}

    def __init__(self) -> None:
        """Initialise the validator."""
        self._custom_providers: set[str] = set()
        self._custom_models: set[str] = set()

    def register_custom_provider(self, provider: str) -> None:
        """Register a custom provider for validation."""
        self._custom_providers.add(provider.lower())

    def register_custom_model(self, model: str) -> None:
        """Register a custom model for validation."""
        self._custom_models.add(model)

    def validate_file(self, path: Path) -> ValidationResult:
        """
        Validate a configuration file.

        Args:
            path: Path to the configuration file.

        Returns:
            Validation result with any issues found.
        """
        result = ValidationResult(file_path=path)

        if not path.exists():
            result.add_error("file", f"File not found: {path}")
            return result

        # Load the file
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()

            if path.suffix.lower() in [".yaml", ".yml"]:
                data = yaml.safe_load(content)
            elif path.suffix.lower() == ".json":
                data = json.loads(content)
            else:
                result.add_error("file", f"Unsupported file format: {path.suffix}")
                return result

        except yaml.YAMLError as e:
            result.add_error("file", f"Invalid YAML: {e}")
            return result
        except json.JSONDecodeError as e:
            result.add_error("file", f"Invalid JSON: {e}")
            return result

        # Detect config type from path or content
        config_type = self._detect_config_type(path, data)
        result.config_type = config_type

        # Validate based on type
        if config_type == "vendor":
            self._validate_vendor(data, result)
        elif config_type == "model":
            self._validate_model(data, result)
        elif config_type == "experiment":
            self._validate_experiment(data, result)
        elif config_type == "template":
            self._validate_template(data, result)
        elif config_type == "workflow":
            self._validate_workflow(data, result)
        else:
            result.add_warning(
                "type", "Unknown config type, performing basic validation"
            )
            self._validate_basic(data, result)

        return result

    def validate_data(
        self,
        data: dict[str, Any],
        config_type: str,
    ) -> ValidationResult:
        """
        Validate configuration data directly.

        Args:
            data: Configuration dictionary.
            config_type: Type of configuration.

        Returns:
            Validation result.
        """
        result = ValidationResult(config_type=config_type)

        if config_type == "vendor":
            self._validate_vendor(data, result)
        elif config_type == "model":
            self._validate_model(data, result)
        elif config_type == "experiment":
            self._validate_experiment(data, result)
        elif config_type == "template":
            self._validate_template(data, result)
        elif config_type == "workflow":
            self._validate_workflow(data, result)
        else:
            self._validate_basic(data, result)

        return result

    def validate_all(self, directory: Path) -> list[ValidationResult]:
        """
        Validate all configuration files in a directory.

        Args:
            directory: Directory to scan.

        Returns:
            List of validation results.
        """
        results = []

        for path in directory.rglob("*.yaml"):
            results.append(self.validate_file(path))

        for path in directory.rglob("*.yml"):
            results.append(self.validate_file(path))

        for path in directory.rglob("*.json"):
            # Skip non-config JSON files
            if path.name not in ["package.json", "tsconfig.json"]:
                results.append(self.validate_file(path))

        return results

    def _detect_config_type(self, path: Path, data: dict) -> str:
        """Detect the configuration type from path or content."""
        path_str = str(path).lower()

        if "vendor" in path_str:
            return "vendor"
        if "model" in path_str:
            return "model"
        if "experiment" in path_str or path.name == "config.yaml":
            return "experiment"
        if "template" in path_str:
            return "template"
        if "workflow" in path_str:
            return "workflow"

        # Detect from content
        if "api_base" in data:
            return "vendor"
        if "provider" in data and "context_window" in data:
            return "model"
        if "steps" in data:
            return "workflow"
        if "variables" in data or "content" in data:
            return "template"

        return "unknown"

    def _validate_schema(
        self,
        data: dict,
        schema: dict,
        result: ValidationResult,
    ) -> None:
        """Validate data against JSON schema (simplified validation)."""
        # Check required fields
        for field in schema.get("required", []):
            if field not in data:
                result.add_error(
                    field,
                    f"Required field '{field}' is missing",
                    suggestion=f"Add '{field}' to the configuration",
                )

        # Check field types and constraints
        properties = schema.get("properties", {})
        for field, value in data.items():
            if field not in properties:
                continue

            field_schema = properties[field]
            self._validate_field(field, value, field_schema, result)

    def _validate_field(
        self,
        field: str,
        value: Any,
        schema: dict,
        result: ValidationResult,
    ) -> None:
        """Validate a single field against its schema."""
        expected_type = schema.get("type")

        # Type checking
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        if expected_type and expected_type in type_map:
            expected = type_map[expected_type]
            if not isinstance(value, expected):
                result.add_error(
                    field,
                    f"Expected {expected_type}, got {type(value).__name__}",
                )
                return

        # String constraints
        if expected_type == "string" and isinstance(value, str):
            if "minLength" in schema and len(value) < schema["minLength"]:
                result.add_error(
                    field,
                    f"String too short (minimum {schema['minLength']} characters)",
                )
            if "pattern" in schema and not re.match(schema["pattern"], value):
                result.add_error(
                    field,
                    "String does not match required pattern",
                )
            if "enum" in schema and value not in schema["enum"]:
                result.add_error(
                    field,
                    f"Invalid value '{value}'. Allowed: {schema['enum']}",
                    suggestion=f"Use one of: {', '.join(schema['enum'])}",
                )

        # Number constraints
        if expected_type in ("integer", "number") and isinstance(value, (int, float)):
            if "minimum" in schema and value < schema["minimum"]:
                result.add_error(
                    field,
                    f"Value {value} is below minimum {schema['minimum']}",
                )
            if "maximum" in schema and value > schema["maximum"]:
                result.add_error(
                    field,
                    f"Value {value} exceeds maximum {schema['maximum']}",
                )

        # Array constraints
        if expected_type == "array" and isinstance(value, list):
            if "minItems" in schema and len(value) < schema["minItems"]:
                result.add_error(
                    field,
                    f"Array too short (minimum {schema['minItems']} items)",
                )

    def _validate_vendor(self, data: dict, result: ValidationResult) -> None:
        """Validate vendor configuration."""
        self._validate_schema(data, VENDOR_SCHEMA, result)

        # Semantic validation
        if "api_base" in data:
            api_base = data["api_base"]
            if not api_base.startswith("https://"):
                result.add_error(
                    "api_base",
                    "API base must use HTTPS",
                    suggestion="Change to https://...",
                )

        if "auth_env" in data:
            import os

            if not os.environ.get(data["auth_env"]):
                result.add_warning(
                    "auth_env",
                    f"Environment variable '{data['auth_env']}' is not set",
                )

    def _validate_model(self, data: dict, result: ValidationResult) -> None:
        """Validate model configuration."""
        self._validate_schema(data, MODEL_SCHEMA, result)

        # Check provider exists
        if "provider" in data:
            provider = data["provider"].lower()
            if (
                provider not in self.KNOWN_PROVIDERS
                and provider not in self._custom_providers
            ):
                result.add_warning(
                    "provider",
                    f"Unknown provider '{provider}'",
                    suggestion="Register the provider first or check spelling",
                )

        # Check pricing
        if "input_price" in data and "output_price" not in data:
            result.add_warning(
                "output_price",
                "Input price set but output price missing",
            )

    def _validate_experiment(self, data: dict, result: ValidationResult) -> None:
        """Validate experiment configuration."""
        self._validate_schema(data, EXPERIMENT_SCHEMA, result)

        # Cross-reference validation
        if "provider" in data:
            provider = data["provider"].lower()
            if (
                provider not in self.KNOWN_PROVIDERS
                and provider not in self._custom_providers
            ):
                result.add_error(
                    "provider",
                    f"Unknown provider '{provider}'",
                    suggestion=f"Available providers: {', '.join(self.KNOWN_PROVIDERS)}",
                )

        if "model" in data:
            model = data["model"]
            is_known = any(
                model.startswith(prefix) for prefix in self.KNOWN_MODEL_PREFIXES
            )
            if not is_known and model not in self._custom_models:
                result.add_warning(
                    "model",
                    f"Model '{model}' not recognised",
                    suggestion="Verify model name is correct",
                )

    def _validate_template(self, data: dict, result: ValidationResult) -> None:
        """Validate template configuration."""
        self._validate_schema(data, TEMPLATE_SCHEMA, result)

        # Check for Jinja2 syntax if content provided
        if "content" in data:
            content = data["content"]
            # Basic Jinja2 syntax check
            if "{{" in content and "}}" not in content:
                result.add_error(
                    "content",
                    "Unclosed Jinja2 variable block",
                )
            if "{%" in content and "%}" not in content:
                result.add_error(
                    "content",
                    "Unclosed Jinja2 control block",
                )

    def _validate_workflow(self, data: dict, result: ValidationResult) -> None:
        """Validate workflow configuration."""
        self._validate_schema(data, WORKFLOW_SCHEMA, result)

        # Validate steps
        if "steps" in data:
            step_names = set()
            for i, step in enumerate(data["steps"]):
                if not isinstance(step, dict):
                    result.add_error(
                        f"steps[{i}]",
                        "Step must be an object",
                    )
                    continue

                name = step.get("name", "")
                if not name:
                    result.add_error(
                        f"steps[{i}].name",
                        "Step name is required",
                    )
                elif name in step_names:
                    result.add_error(
                        f"steps[{i}].name",
                        f"Duplicate step name '{name}'",
                    )
                else:
                    step_names.add(name)

    def _validate_basic(self, data: dict, result: ValidationResult) -> None:
        """Basic validation for unknown config types."""
        if not isinstance(data, dict):
            result.add_error("root", "Configuration must be a dictionary")
            return

        if not data:
            result.add_warning("root", "Configuration is empty")


def validate_config(path: Path) -> ValidationResult:
    """
    Convenience function to validate a config file.

    Args:
        path: Path to configuration file.

    Returns:
        Validation result.
    """
    validator = ConfigValidator()
    return validator.validate_file(path)
