"""Tests for configuration validation (F-055)."""

from pathlib import Path
from tempfile import TemporaryDirectory

import yaml
from persona.core.config.validator import (
    ConfigValidator,
    ValidationIssue,
    ValidationLevel,
    ValidationResult,
    validate_config,
)


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_initial_state(self):
        """Initial state is valid."""
        result = ValidationResult()
        assert result.is_valid

    def test_add_error_invalidates(self):
        """Adding error invalidates result."""
        result = ValidationResult()
        result.add_error("field", "error message")
        assert not result.is_valid

    def test_add_warning_keeps_valid(self):
        """Adding warning keeps result valid."""
        result = ValidationResult()
        result.add_warning("field", "warning message")
        assert result.is_valid

    def test_errors_property(self):
        """Returns only errors."""
        result = ValidationResult()
        result.add_error("field1", "error")
        result.add_warning("field2", "warning")

        errors = result.errors
        assert len(errors) == 1
        assert errors[0].level == ValidationLevel.ERROR

    def test_warnings_property(self):
        """Returns only warnings."""
        result = ValidationResult()
        result.add_error("field1", "error")
        result.add_warning("field2", "warning")

        warnings = result.warnings
        assert len(warnings) == 1
        assert warnings[0].level == ValidationLevel.WARNING

    def test_merge(self):
        """Merges two results."""
        result1 = ValidationResult()
        result1.add_error("field1", "error1")

        result2 = ValidationResult()
        result2.add_warning("field2", "warning2")

        result1.merge(result2)
        assert len(result1.issues) == 2


class TestValidationIssue:
    """Tests for ValidationIssue."""

    def test_str_with_location(self):
        """String representation includes location."""
        issue = ValidationIssue(
            level=ValidationLevel.ERROR,
            field="name",
            message="is required",
            file_path=Path("/path/to/file.yaml"),
            line_number=10,
        )

        result = str(issue)
        assert "/path/to/file.yaml" in result
        assert "line 10" in result
        assert "name" in result

    def test_str_with_suggestion(self):
        """String representation includes suggestion."""
        issue = ValidationIssue(
            level=ValidationLevel.ERROR,
            field="provider",
            message="unknown provider",
            suggestion="use 'openai' or 'anthropic'",
        )

        result = str(issue)
        assert "Suggestion" in result


class TestConfigValidator:
    """Tests for ConfigValidator."""

    def test_validate_missing_file(self):
        """Reports error for missing file."""
        validator = ConfigValidator()
        result = validator.validate_file(Path("/nonexistent/file.yaml"))

        assert not result.is_valid
        assert any("not found" in str(e) for e in result.errors)

    def test_validate_invalid_yaml(self):
        """Reports error for invalid YAML."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.yaml"
            path.write_text("invalid: yaml: content: [")

            validator = ConfigValidator()
            result = validator.validate_file(path)

            assert not result.is_valid
            assert any("Invalid YAML" in str(e) for e in result.errors)

    def test_validate_invalid_json(self):
        """Reports error for invalid JSON."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.json"
            path.write_text("{invalid json}")

            validator = ConfigValidator()
            result = validator.validate_file(path)

            assert not result.is_valid
            assert any("Invalid JSON" in str(e) for e in result.errors)

    def test_validate_vendor_valid(self):
        """Validates valid vendor config."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "Custom Provider",
                "api_base": "https://api.example.com",
                "auth_env": "CUSTOM_API_KEY",
            },
            config_type="vendor",
        )

        assert result.is_valid

    def test_validate_vendor_missing_required(self):
        """Reports missing required vendor fields."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {"name": "Custom Provider"},
            config_type="vendor",
        )

        assert not result.is_valid
        assert any("api_base" in str(e) for e in result.errors)

    def test_validate_vendor_invalid_url(self):
        """Reports invalid API base URL."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "Custom Provider",
                "api_base": "http://insecure.example.com",  # HTTP not HTTPS
            },
            config_type="vendor",
        )

        assert not result.is_valid
        assert any("HTTPS" in str(e) for e in result.errors)

    def test_validate_model_valid(self):
        """Validates valid model config."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "custom-model",
                "provider": "openai",
                "context_window": 128000,
                "input_price": 5.0,
                "output_price": 15.0,
            },
            config_type="model",
        )

        assert result.is_valid

    def test_validate_model_missing_required(self):
        """Reports missing required model fields."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {"name": "custom-model"},
            config_type="model",
        )

        assert not result.is_valid
        assert any("provider" in str(e) for e in result.errors)

    def test_validate_experiment_valid(self):
        """Validates valid experiment config."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "my-experiment",
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "count": 3,
                "complexity": "moderate",
            },
            config_type="experiment",
        )

        assert result.is_valid

    def test_validate_experiment_invalid_name(self):
        """Reports invalid experiment name."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {"name": "invalid name with spaces!"},
            config_type="experiment",
        )

        assert not result.is_valid
        assert any("pattern" in str(e) for e in result.errors)

    def test_validate_experiment_unknown_provider(self):
        """Reports unknown provider."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "test",
                "provider": "unknown-provider",
            },
            config_type="experiment",
        )

        assert not result.is_valid
        assert any("Unknown provider" in str(e) for e in result.errors)

    def test_validate_experiment_invalid_complexity(self):
        """Reports invalid complexity value."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "test",
                "complexity": "invalid",
            },
            config_type="experiment",
        )

        assert not result.is_valid
        assert any("complexity" in str(e).lower() for e in result.errors)

    def test_validate_template_valid(self):
        """Validates valid template config."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "Custom Template",
                "description": "A custom template",
                "variables": ["data", "count"],
                "content": "Generate {{ count }} personas from {{ data }}",
            },
            config_type="template",
        )

        assert result.is_valid

    def test_validate_template_unclosed_variable(self):
        """Reports unclosed Jinja2 variable."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "Bad Template",
                "content": "Generate {{ count personas",
            },
            config_type="template",
        )

        assert not result.is_valid
        assert any("Unclosed" in str(e) for e in result.errors)

    def test_validate_workflow_valid(self):
        """Validates valid workflow config."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "Custom Workflow",
                "steps": [
                    {"name": "step1", "template": "template1"},
                    {"name": "step2", "template": "template2"},
                ],
            },
            config_type="workflow",
        )

        assert result.is_valid

    def test_validate_workflow_no_steps(self):
        """Reports workflow without steps."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "Empty Workflow",
                "steps": [],
            },
            config_type="workflow",
        )

        assert not result.is_valid
        assert any("minItems" in str(e) or "steps" in str(e) for e in result.errors)

    def test_validate_workflow_duplicate_step_names(self):
        """Reports duplicate step names."""
        validator = ConfigValidator()
        result = validator.validate_data(
            {
                "name": "Workflow",
                "steps": [
                    {"name": "step1"},
                    {"name": "step1"},  # Duplicate
                ],
            },
            config_type="workflow",
        )

        assert not result.is_valid
        assert any("Duplicate" in str(e) for e in result.errors)

    def test_validate_file_from_path(self):
        """Validates file from path."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "experiment.yaml"
            path.write_text(
                yaml.dump(
                    {
                        "name": "test-experiment",
                        "provider": "openai",
                        "model": "gpt-4o",
                    }
                )
            )

            validator = ConfigValidator()
            result = validator.validate_file(path)

            assert result.is_valid
            assert result.config_type == "experiment"

    def test_validate_all_directory(self):
        """Validates all files in directory."""
        with TemporaryDirectory() as tmpdir:
            # Create valid config
            valid = Path(tmpdir) / "valid.yaml"
            valid.write_text(yaml.dump({"name": "test", "provider": "openai"}))

            # Create invalid config
            invalid = Path(tmpdir) / "invalid.yaml"
            invalid.write_text(yaml.dump({"invalid": "config"}))

            validator = ConfigValidator()
            results = validator.validate_all(Path(tmpdir))

            assert len(results) == 2

    def test_register_custom_provider(self):
        """Custom providers pass validation."""
        validator = ConfigValidator()
        validator.register_custom_provider("custom-cloud")

        result = validator.validate_data(
            {
                "name": "test",
                "provider": "custom-cloud",
            },
            config_type="experiment",
        )

        # Should not report unknown provider error
        assert not any("Unknown provider" in str(e) for e in result.errors)


class TestValidateConfigFunction:
    """Tests for validate_config convenience function."""

    def test_validates_file(self):
        """Validates file using convenience function."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.yaml"
            path.write_text(yaml.dump({"name": "test"}))

            result = validate_config(path)
            assert result is not None
