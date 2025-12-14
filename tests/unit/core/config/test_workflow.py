"""Tests for custom workflow configuration."""

import tempfile
from pathlib import Path

import pytest

from persona.core.config.workflow import (
    WorkflowConfig,
    WorkflowStep,
    WorkflowInfo,
    CustomWorkflowLoader,
    get_builtin_workflows,
)


class TestWorkflowStep:
    """Tests for WorkflowStep model."""

    def test_minimal_step(self):
        """Test minimal step configuration."""
        step = WorkflowStep(
            name="generate",
            template="builtin/default",
        )
        assert step.name == "generate"
        assert step.template == "builtin/default"
        assert step.model is None
        assert step.input is None
        assert step.output is None

    def test_full_step(self):
        """Test step with all options."""
        step = WorkflowStep(
            name="synthesise",
            template="custom/synthesis",
            model="claude-opus-4-5-20251101",
            provider="anthropic",
            input="themes",
            output="personas",
            temperature=0.5,
            max_tokens=8192,
            variables={"focus": "healthcare"},
        )
        assert step.model == "claude-opus-4-5-20251101"
        assert step.input == "themes"
        assert step.output == "personas"


class TestWorkflowConfig:
    """Tests for WorkflowConfig model."""

    def test_minimal_config(self):
        """Test minimal workflow configuration."""
        config = WorkflowConfig(
            id="test-workflow",
            name="Test Workflow",
        )
        assert config.id == "test-workflow"
        assert config.name == "Test Workflow"
        assert config.provider == "anthropic"
        assert config.temperature == 0.7

    def test_full_config(self):
        """Test full workflow configuration."""
        config = WorkflowConfig(
            id="research-workflow",
            name="Research Workflow",
            description="Detailed research workflow",
            author="Test Author",
            version="2.0.0",
            tags=["research", "detailed"],
            provider="anthropic",
            model="claude-opus-4-5-20251101",
            temperature=0.5,
            max_tokens=8192,
            steps=[
                WorkflowStep(name="extract", template="builtin/default", output="themes"),
                WorkflowStep(name="synthesise", template="builtin/default", input="themes", output="personas"),
            ],
            variables={"complexity": "complex"},
        )
        assert config.version == "2.0.0"
        assert len(config.steps) == 2
        assert config.variables["complexity"] == "complex"

    def test_id_validation_valid(self):
        """Test valid workflow IDs."""
        valid_ids = ["workflow-1", "my_workflow", "test.workflow", "Workflow1"]
        for workflow_id in valid_ids:
            config = WorkflowConfig(id=workflow_id, name="Test")
            assert config.id == workflow_id

    def test_id_validation_invalid(self):
        """Test invalid workflow IDs."""
        invalid_ids = ["-workflow", "123workflow", ".workflow"]
        for workflow_id in invalid_ids:
            with pytest.raises(ValueError):
                WorkflowConfig(id=workflow_id, name="Test")

    def test_step_chain_validation_valid(self):
        """Test valid step chain."""
        config = WorkflowConfig(
            id="valid-chain",
            name="Valid Chain",
            steps=[
                WorkflowStep(name="step1", template="t", output="data1"),
                WorkflowStep(name="step2", template="t", input="data1", output="data2"),
                WorkflowStep(name="step3", template="t", input="data2"),
            ],
        )
        assert len(config.steps) == 3

    def test_step_chain_validation_invalid(self):
        """Test invalid step chain (missing input)."""
        with pytest.raises(ValueError):
            WorkflowConfig(
                id="invalid-chain",
                name="Invalid Chain",
                steps=[
                    WorkflowStep(name="step1", template="t", output="data1"),
                    WorkflowStep(name="step2", template="t", input="nonexistent"),
                ],
            )

    def test_get_step(self):
        """Test getting step by name."""
        config = WorkflowConfig(
            id="test",
            name="Test",
            steps=[
                WorkflowStep(name="step1", template="t"),
                WorkflowStep(name="step2", template="t"),
            ],
        )
        assert config.get_step("step1") is not None
        assert config.get_step("step1").name == "step1"
        assert config.get_step("nonexistent") is None

    def test_get_step_settings(self):
        """Test getting effective step settings."""
        config = WorkflowConfig(
            id="test",
            name="Test",
            provider="anthropic",
            model="claude-sonnet-4-5-20250929",
            temperature=0.7,
            max_tokens=4096,
            variables={"global": "value"},
            steps=[
                WorkflowStep(
                    name="override",
                    template="t",
                    model="claude-opus-4-5-20251101",
                    temperature=0.3,
                    variables={"step": "value"},
                ),
            ],
        )
        settings = config.get_step_settings(config.steps[0])
        assert settings["provider"] == "anthropic"
        assert settings["model"] == "claude-opus-4-5-20251101"  # Step override
        assert settings["temperature"] == 0.3  # Step override
        assert settings["variables"]["global"] == "value"
        assert settings["variables"]["step"] == "value"


class TestWorkflowConfigYaml:
    """Tests for WorkflowConfig YAML serialisation."""

    def test_from_yaml(self):
        """Test loading config from YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "workflow.yaml"
            path.write_text("""
id: test-workflow
name: Test Workflow
provider: openai
steps:
  - name: generate
    template: builtin/default
    output: personas
variables:
  complexity: simple
""")
            config = WorkflowConfig.from_yaml(path)

            assert config.id == "test-workflow"
            assert config.provider == "openai"
            assert len(config.steps) == 1

    def test_from_yaml_not_found(self):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            WorkflowConfig.from_yaml(Path("/nonexistent/path.yaml"))

    def test_to_yaml(self):
        """Test saving config to YAML file."""
        config = WorkflowConfig(
            id="test-workflow",
            name="Test Workflow",
            steps=[
                WorkflowStep(name="generate", template="builtin/default"),
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "workflow.yaml"
            config.to_yaml(path)

            assert path.exists()

            loaded = WorkflowConfig.from_yaml(path)
            assert loaded.id == config.id

    def test_yaml_round_trip(self):
        """Test config survives YAML round trip."""
        original = WorkflowConfig(
            id="round-trip",
            name="Round Trip Test",
            description="Testing round trip",
            provider="anthropic",
            temperature=0.5,
            steps=[
                WorkflowStep(name="step1", template="t", output="data"),
                WorkflowStep(name="step2", template="t", input="data"),
            ],
            variables={"key": "value"},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "workflow.yaml"
            original.to_yaml(path)
            loaded = WorkflowConfig.from_yaml(path)

            assert loaded.id == original.id
            assert loaded.temperature == original.temperature
            assert len(loaded.steps) == len(original.steps)
            assert loaded.variables == original.variables


class TestCustomWorkflowLoader:
    """Tests for CustomWorkflowLoader."""

    def test_default_search_paths(self):
        """Test default search paths."""
        loader = CustomWorkflowLoader()
        assert loader._user_dir == Path.home() / ".persona" / "workflows"
        assert loader._project_dir == Path(".persona") / "workflows"

    def test_list_workflows_builtin(self):
        """Test listing built-in workflows."""
        loader = CustomWorkflowLoader()
        workflows = loader.list_workflows()

        assert "default" in workflows
        assert "research" in workflows
        assert "quick" in workflows
        assert "healthcare" in workflows

    def test_list_workflows_by_source(self):
        """Test listing workflows filtered by source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            # Create custom workflow
            (user_dir / "custom.yaml").write_text("""
id: custom
name: Custom
steps:
  - name: step
    template: t
""")

            loader = CustomWorkflowLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            user_workflows = loader.list_workflows(source="user")
            assert "custom" in user_workflows
            assert "default" not in user_workflows

            builtin_workflows = loader.list_workflows(source="builtin")
            assert "default" in builtin_workflows
            assert "custom" not in builtin_workflows

    def test_list_workflows_by_tag(self):
        """Test listing workflows filtered by tag."""
        loader = CustomWorkflowLoader()
        healthcare_workflows = loader.list_workflows(tag="healthcare")
        assert "healthcare" in healthcare_workflows
        assert "quick" not in healthcare_workflows

    def test_exists(self):
        """Test exists check."""
        loader = CustomWorkflowLoader()
        assert loader.exists("default") is True
        assert loader.exists("nonexistent") is False

    def test_get_info(self):
        """Test getting workflow info."""
        loader = CustomWorkflowLoader()
        info = loader.get_info("default")

        assert info.id == "default"
        assert info.source == "builtin"
        assert info.step_count > 0

    def test_get_info_not_found(self):
        """Test getting info for nonexistent workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = CustomWorkflowLoader(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
            )

            with pytest.raises(FileNotFoundError):
                loader.get_info("nonexistent")

    def test_load_builtin(self):
        """Test loading built-in workflow."""
        loader = CustomWorkflowLoader()
        config = loader.load("default")

        assert config.id == "default"
        assert len(config.steps) > 0

    def test_load_custom(self):
        """Test loading custom workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()

            (user_dir / "custom.yaml").write_text("""
id: custom
name: Custom Workflow
provider: openai
steps:
  - name: generate
    template: builtin/default
""")

            loader = CustomWorkflowLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            config = loader.load("custom")
            assert config.id == "custom"
            assert config.provider == "openai"

    def test_save_workflow(self):
        """Test saving workflow configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"

            loader = CustomWorkflowLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            config = WorkflowConfig(
                id="saved-workflow",
                name="Saved Workflow",
                steps=[
                    WorkflowStep(name="step", template="t"),
                ],
            )

            path = loader.save(config, user_level=True)

            assert path == user_dir / "saved-workflow.yaml"
            assert path.exists()

    def test_save_workflow_exists(self):
        """Test saving workflow that already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "existing.yaml").write_text("id: existing\nname: E")

            loader = CustomWorkflowLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            config = WorkflowConfig(id="existing", name="New")

            with pytest.raises(FileExistsError):
                loader.save(config, user_level=True)

    def test_save_workflow_overwrite(self):
        """Test saving workflow with overwrite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "existing.yaml").write_text("id: existing\nname: Old")

            loader = CustomWorkflowLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            config = WorkflowConfig(id="existing", name="New")
            loader.save(config, user_level=True, overwrite=True)

            loaded = loader.load("existing")
            assert loaded.name == "New"

    def test_delete_workflow(self):
        """Test deleting a workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "to-delete.yaml").write_text("id: to-delete\nname: D")

            loader = CustomWorkflowLoader(
                user_dir=user_dir,
                project_dir=Path(tmpdir) / "project",
            )

            assert loader.exists("to-delete")
            result = loader.delete("to-delete")
            assert result is True
            assert not loader.exists("to-delete")

    def test_delete_builtin_workflow(self):
        """Test cannot delete built-in workflow."""
        loader = CustomWorkflowLoader()
        result = loader.delete("default")
        assert result is False
        assert loader.exists("default")

    def test_validate_workflow_valid(self):
        """Test validating valid workflow."""
        loader = CustomWorkflowLoader()
        is_valid, errors = loader.validate_workflow("default")

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_workflow_not_found(self):
        """Test validating nonexistent workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = CustomWorkflowLoader(
                user_dir=Path(tmpdir) / "user",
                project_dir=Path(tmpdir) / "project",
            )

            is_valid, errors = loader.validate_workflow("nonexistent")
            assert is_valid is False

    def test_project_workflows_override_user(self):
        """Test project workflows override user workflows."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            user_dir.mkdir()
            (user_dir / "override.yaml").write_text("id: override\nname: User")

            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()
            (project_dir / "override.yaml").write_text("id: override\nname: Project")

            loader = CustomWorkflowLoader(
                user_dir=user_dir,
                project_dir=project_dir,
            )

            info = loader.get_info("override")
            assert info.source == "project"

            config = loader.load("override")
            assert config.name == "Project"


class TestGetBuiltinWorkflows:
    """Tests for get_builtin_workflows function."""

    def test_returns_builtin_workflows(self):
        """Test returns only built-in workflows."""
        workflows = get_builtin_workflows()

        assert "default" in workflows
        assert "research" in workflows
        assert "quick" in workflows
        assert "healthcare" in workflows

        for workflow_id, info in workflows.items():
            assert info.source == "builtin"

    def test_workflows_have_info(self):
        """Test built-in workflows have proper info."""
        workflows = get_builtin_workflows()

        default = workflows["default"]
        assert default.name == "Default Workflow"
        assert default.step_count > 0
