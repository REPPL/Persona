"""
Tests for prompt templating functionality (F-003).
"""

import pytest
from pathlib import Path

from persona.core.prompts import PromptTemplate, Workflow, WorkflowLoader
from persona.core.prompts.template import DEFAULT_PERSONA_TEMPLATE


class TestPromptTemplate:
    """Tests for PromptTemplate class."""

    def test_create_template(self):
        """Test creating a template."""
        template = PromptTemplate("Hello {{ name }}!")
        assert template is not None
        assert template.template_string == "Hello {{ name }}!"

    def test_render_simple(self):
        """Test rendering with simple variable."""
        template = PromptTemplate("Hello {{ name }}!")
        result = template.render(name="World")
        assert result == "Hello World!"

    def test_render_multiple_variables(self):
        """Test rendering with multiple variables."""
        template = PromptTemplate("Generate {{ count }} personas from {{ source }}")
        result = template.render(count=3, source="interviews")
        assert result == "Generate 3 personas from interviews"

    def test_render_conditional(self):
        """Test rendering with conditional."""
        template = PromptTemplate(
            "{% if detailed %}Include details{% else %}Be brief{% endif %}"
        )

        result_detailed = template.render(detailed=True)
        assert result_detailed == "Include details"

        result_brief = template.render(detailed=False)
        assert result_brief == "Be brief"

    def test_render_loop(self):
        """Test rendering with loop."""
        template = PromptTemplate(
            "{% for item in items %}- {{ item }}\n{% endfor %}"
        )
        result = template.render(items=["a", "b", "c"])
        assert "- a" in result
        assert "- b" in result
        assert "- c" in result

    def test_render_missing_variable(self):
        """Test error when variable is missing."""
        template = PromptTemplate("Hello {{ name }}!")

        with pytest.raises(Exception):  # Jinja2 raises UndefinedError
            template.render()

    def test_get_variables(self):
        """Test getting template variables."""
        template = PromptTemplate("{{ a }} and {{ b }} and {{ c }}")
        variables = template.get_variables()

        assert "a" in variables
        assert "b" in variables
        assert "c" in variables

    def test_validate_success(self):
        """Test validation with all variables present."""
        template = PromptTemplate("{{ name }} is {{ age }}")

        assert template.validate(name="Alice", age=30) is True

    def test_validate_missing(self):
        """Test validation with missing variable."""
        template = PromptTemplate("{{ name }} is {{ age }}")

        with pytest.raises(ValueError) as excinfo:
            template.validate(name="Alice")

        assert "Missing required variables" in str(excinfo.value)
        assert "age" in str(excinfo.value)

    def test_from_file(self, tmp_path: Path):
        """Test loading template from file."""
        template_file = tmp_path / "template.j2"
        template_file.write_text("Hello {{ name }}!")

        template = PromptTemplate.from_file(template_file)
        result = template.render(name="File")

        assert result == "Hello File!"

    def test_from_file_not_found(self):
        """Test error when template file not found."""
        with pytest.raises(FileNotFoundError):
            PromptTemplate.from_file("/nonexistent/template.j2")

    def test_default_template_exists(self):
        """Test that default template is defined."""
        assert DEFAULT_PERSONA_TEMPLATE is not None
        assert "{{ count }}" in DEFAULT_PERSONA_TEMPLATE
        assert "{{ data }}" in DEFAULT_PERSONA_TEMPLATE


class TestWorkflow:
    """Tests for Workflow class."""

    def test_create_workflow(self):
        """Test creating a workflow."""
        workflow = Workflow(name="test")

        assert workflow.name == "test"
        assert workflow.provider == "anthropic"
        assert workflow.temperature == 0.7

    def test_render_prompt(self):
        """Test rendering workflow prompt."""
        template = PromptTemplate("Generate {{ count }} personas")
        workflow = Workflow(name="test", template=template)

        result = workflow.render_prompt(count=5)
        assert "5 personas" in result

    def test_render_prompt_with_defaults(self):
        """Test rendering with default variables."""
        template = PromptTemplate("{{ greeting }} {{ name }}")
        workflow = Workflow(
            name="test",
            template=template,
            variables={"greeting": "Hello"},
        )

        result = workflow.render_prompt(name="World")
        assert result == "Hello World"

    def test_render_prompt_override_defaults(self):
        """Test that provided values override defaults."""
        template = PromptTemplate("{{ greeting }} {{ name }}")
        workflow = Workflow(
            name="test",
            template=template,
            variables={"greeting": "Hello", "name": "Default"},
        )

        result = workflow.render_prompt(name="Override")
        assert result == "Hello Override"


class TestWorkflowLoader:
    """Tests for WorkflowLoader class."""

    def test_list_builtin(self):
        """Test listing built-in workflows."""
        loader = WorkflowLoader()
        workflows = loader.list_builtin()

        assert "default" in workflows
        assert "research" in workflows
        assert "quick" in workflows

    def test_load_builtin_default(self):
        """Test loading default workflow."""
        loader = WorkflowLoader()
        workflow = loader.load_builtin("default")

        assert workflow.name == "default"
        assert "moderate" in str(workflow.variables.get("complexity"))

    def test_load_builtin_research(self):
        """Test loading research workflow."""
        loader = WorkflowLoader()
        workflow = loader.load_builtin("research")

        assert workflow.name == "research"
        assert workflow.variables.get("include_reasoning") is True

    def test_load_builtin_quick(self):
        """Test loading quick workflow."""
        loader = WorkflowLoader()
        workflow = loader.load_builtin("quick")

        assert workflow.name == "quick"
        assert workflow.variables.get("complexity") == "simple"

    def test_load_builtin_unknown(self):
        """Test error for unknown workflow."""
        loader = WorkflowLoader()

        with pytest.raises(ValueError) as excinfo:
            loader.load_builtin("nonexistent")

        assert "Unknown built-in workflow" in str(excinfo.value)

    def test_load_from_file(self, tmp_path: Path):
        """Test loading workflow from YAML file."""
        workflow_file = tmp_path / "workflow.yaml"
        workflow_file.write_text("""
name: custom
description: Custom workflow
provider: openai
temperature: 0.5
variables:
  complexity: simple
""")

        loader = WorkflowLoader()
        workflow = loader.load(workflow_file)

        assert workflow.name == "custom"
        assert workflow.provider == "openai"
        assert workflow.temperature == 0.5
        assert workflow.variables["complexity"] == "simple"

    def test_load_from_file_not_found(self):
        """Test error when file not found."""
        loader = WorkflowLoader()

        with pytest.raises(FileNotFoundError):
            loader.load("/nonexistent/workflow.yaml")

    def test_load_empty_file(self, tmp_path: Path):
        """Test error for empty YAML file."""
        workflow_file = tmp_path / "empty.yaml"
        workflow_file.write_text("")

        loader = WorkflowLoader()

        with pytest.raises(ValueError) as excinfo:
            loader.load(workflow_file)

        assert "Empty workflow file" in str(excinfo.value)

    def test_create_from_dict(self):
        """Test creating workflow from dictionary."""
        loader = WorkflowLoader()
        workflow = loader.create_from_dict({
            "name": "dict-workflow",
            "provider": "gemini",
            "max_tokens": 2000,
        })

        assert workflow.name == "dict-workflow"
        assert workflow.provider == "gemini"
        assert workflow.max_tokens == 2000
