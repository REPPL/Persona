"""
Custom workflow configuration.

This module provides workflow management for custom multi-step workflows.
"""

from pathlib import Path
from typing import Any, ClassVar

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class WorkflowStep(BaseModel):
    """A single step in a multi-step workflow."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Step name")
    template: str = Field(..., description="Template reference (builtin/name or custom/name)")
    model: str | None = Field(default=None, description="Model to use for this step")
    provider: str | None = Field(default=None, description="Provider for this step")
    input: str | None = Field(default=None, description="Input from previous step output")
    output: str | None = Field(default=None, description="Output name for next steps")
    temperature: float | None = Field(default=None, description="Sampling temperature")
    max_tokens: int | None = Field(default=None, description="Maximum tokens")
    variables: dict[str, Any] = Field(default_factory=dict, description="Step-specific variables")


class WorkflowConfig(BaseModel):
    """Configuration for a custom workflow."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    id: str = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(default="", description="Workflow description")
    author: str = Field(default="", description="Workflow author")
    version: str = Field(default="1.0.0", description="Workflow version")
    tags: list[str] = Field(default_factory=list, description="Tags for categorisation")

    # Default settings (can be overridden per-step)
    provider: str = Field(default="anthropic", description="Default provider")
    model: str | None = Field(default=None, description="Default model")
    temperature: float = Field(default=0.7, description="Default temperature")
    max_tokens: int = Field(default=4096, description="Default max tokens")

    # Steps
    steps: list[WorkflowStep] = Field(default_factory=list, description="Workflow steps")

    # Variables available to all steps
    variables: dict[str, Any] = Field(default_factory=dict, description="Default variables")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate workflow ID format."""
        import re
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9._-]*$", v):
            raise ValueError(
                "Workflow ID must start with a letter and contain only "
                "letters, numbers, dots, underscores, and hyphens"
            )
        return v

    @model_validator(mode="after")
    def validate_step_chain(self) -> "WorkflowConfig":
        """Validate step input/output chain."""
        if not self.steps:
            return self

        outputs = set()
        for step in self.steps:
            # Check input exists
            if step.input and step.input not in outputs:
                raise ValueError(
                    f"Step '{step.name}' references unknown input '{step.input}'. "
                    f"Available outputs: {outputs or 'none'}"
                )
            # Register output
            if step.output:
                outputs.add(step.output)

        return self

    @classmethod
    def from_yaml(cls, path: Path) -> "WorkflowConfig":
        """Load workflow from YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValueError(f"Empty workflow file: {path}")

        return cls(**data)

    def to_yaml(self, path: Path) -> None:
        """Save workflow to YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)

        data = self.model_dump(mode="json", exclude_none=True)

        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    def get_step(self, name: str) -> WorkflowStep | None:
        """Get a step by name."""
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def get_step_settings(self, step: WorkflowStep) -> dict[str, Any]:
        """Get effective settings for a step (merging defaults)."""
        return {
            "provider": step.provider or self.provider,
            "model": step.model or self.model,
            "temperature": step.temperature if step.temperature is not None else self.temperature,
            "max_tokens": step.max_tokens or self.max_tokens,
            "variables": {**self.variables, **step.variables},
        }


class WorkflowInfo(BaseModel):
    """Information about a workflow."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    id: str = Field(..., description="Workflow identifier")
    path: Path | None = Field(default=None, description="Path to workflow file")
    source: str = Field(..., description="Source: 'builtin', 'user', or 'project'")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(default="", description="Workflow description")
    step_count: int = Field(default=0, description="Number of steps")
    tags: list[str] = Field(default_factory=list, description="Tags")


class CustomWorkflowLoader:
    """
    Loader for custom workflow configurations.

    Searches for workflows in:
    1. Built-in workflows (defined in code)
    2. User workflows (~/.persona/workflows/)
    3. Project workflows (.persona/workflows/)

    Project workflows override user workflows, which override built-ins.
    """

    DEFAULT_USER_DIR: ClassVar[Path] = Path.home() / ".persona" / "workflows"
    DEFAULT_PROJECT_DIR: ClassVar[Path] = Path(".persona") / "workflows"

    # Built-in workflow definitions
    BUILTIN_WORKFLOWS: ClassVar[dict[str, dict[str, Any]]] = {
        "default": {
            "id": "default",
            "name": "Default Workflow",
            "description": "Standard single-step persona generation",
            "provider": "anthropic",
            "temperature": 0.7,
            "max_tokens": 4096,
            "steps": [
                {
                    "name": "generate",
                    "template": "builtin/default",
                    "output": "personas",
                },
            ],
            "variables": {
                "complexity": "moderate",
                "detail_level": "standard",
                "include_reasoning": False,
            },
            "tags": ["default", "single-step"],
        },
        "research": {
            "id": "research",
            "name": "Research Workflow",
            "description": "Research-focused workflow with detailed reasoning",
            "provider": "anthropic",
            "temperature": 0.5,
            "max_tokens": 8192,
            "steps": [
                {
                    "name": "generate",
                    "template": "builtin/default",
                    "output": "personas",
                },
            ],
            "variables": {
                "complexity": "complex",
                "detail_level": "detailed",
                "include_reasoning": True,
            },
            "tags": ["research", "detailed"],
        },
        "quick": {
            "id": "quick",
            "name": "Quick Workflow",
            "description": "Fast generation with minimal output",
            "provider": "openai",
            "temperature": 0.8,
            "max_tokens": 2048,
            "steps": [
                {
                    "name": "generate",
                    "template": "builtin/default",
                    "output": "personas",
                },
            ],
            "variables": {
                "complexity": "simple",
                "detail_level": "minimal",
                "include_reasoning": False,
            },
            "tags": ["quick", "minimal"],
        },
        "healthcare": {
            "id": "healthcare",
            "name": "Healthcare Workflow",
            "description": "Healthcare-focused persona generation",
            "provider": "anthropic",
            "temperature": 0.6,
            "max_tokens": 6144,
            "steps": [
                {
                    "name": "generate",
                    "template": "builtin/healthcare",
                    "output": "personas",
                },
            ],
            "variables": {
                "complexity": "complex",
                "detail_level": "detailed",
                "include_reasoning": True,
            },
            "tags": ["healthcare", "patient-experience"],
        },
    }

    def __init__(
        self,
        user_dir: Path | None = None,
        project_dir: Path | None = None,
    ) -> None:
        """
        Initialise the workflow loader.

        Args:
            user_dir: Override user workflow directory.
            project_dir: Override project workflow directory.
        """
        self._user_dir = user_dir or self.DEFAULT_USER_DIR
        self._project_dir = project_dir or self.DEFAULT_PROJECT_DIR
        self._cache: dict[str, WorkflowInfo] = {}

    def list_workflows(
        self,
        source: str | None = None,
        tag: str | None = None,
    ) -> list[str]:
        """
        List available workflow IDs.

        Args:
            source: Filter by source ('builtin', 'user', 'project').
            tag: Filter by tag.

        Returns:
            List of workflow IDs.
        """
        workflows = []

        for workflow_id, info in self._discover_all().items():
            if source and info.source != source:
                continue
            if tag and tag not in info.tags:
                continue
            workflows.append(workflow_id)

        return sorted(set(workflows))

    def exists(self, workflow_id: str) -> bool:
        """Check if a workflow exists."""
        return workflow_id in self._discover_all()

    def get_info(self, workflow_id: str) -> WorkflowInfo:
        """
        Get information about a workflow.

        Args:
            workflow_id: Workflow identifier.

        Returns:
            WorkflowInfo object.

        Raises:
            FileNotFoundError: If workflow not found.
        """
        workflows = self._discover_all()
        if workflow_id not in workflows:
            raise FileNotFoundError(f"Workflow not found: {workflow_id}")
        return workflows[workflow_id]

    def load(self, workflow_id: str) -> WorkflowConfig:
        """
        Load a workflow configuration.

        Args:
            workflow_id: Workflow identifier.

        Returns:
            WorkflowConfig object.

        Raises:
            FileNotFoundError: If workflow not found.
        """
        info = self.get_info(workflow_id)

        if info.source == "builtin":
            return WorkflowConfig(**self.BUILTIN_WORKFLOWS[workflow_id])

        if info.path:
            return WorkflowConfig.from_yaml(info.path)

        raise FileNotFoundError(f"Workflow not found: {workflow_id}")

    def save(
        self,
        config: WorkflowConfig,
        user_level: bool = True,
        overwrite: bool = False,
    ) -> Path:
        """
        Save a workflow configuration.

        Args:
            config: WorkflowConfig to save.
            user_level: Save to user directory (True) or project (False).
            overwrite: Overwrite existing workflow.

        Returns:
            Path to saved workflow file.

        Raises:
            FileExistsError: If workflow exists and overwrite is False.
        """
        target_dir = self._user_dir if user_level else self._project_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        path = target_dir / f"{config.id}.yaml"

        if path.exists() and not overwrite:
            raise FileExistsError(f"Workflow already exists: {path}")

        config.to_yaml(path)

        # Clear cache
        self._cache.clear()

        return path

    def delete(self, workflow_id: str) -> bool:
        """
        Delete a custom workflow.

        Args:
            workflow_id: Workflow identifier.

        Returns:
            True if deleted, False if not found or is built-in.
        """
        info = self._discover_all().get(workflow_id)

        if not info:
            return False

        if info.source == "builtin":
            return False

        if info.path:
            try:
                info.path.unlink()
                self._cache.clear()
                return True
            except Exception:
                return False

        return False

    def validate_workflow(self, workflow_id: str) -> tuple[bool, list[str]]:
        """
        Validate a workflow configuration.

        Args:
            workflow_id: Workflow identifier.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []

        try:
            config = self.load(workflow_id)
        except FileNotFoundError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Invalid workflow: {e}"]

        # Check steps have templates
        from persona.core.config.template import TemplateLoader
        template_loader = TemplateLoader()

        for step in config.steps:
            # Parse template reference
            template_ref = step.template
            if template_ref.startswith("builtin/"):
                template_id = template_ref[8:]
            elif template_ref.startswith("custom/"):
                template_id = template_ref[7:]
            else:
                template_id = template_ref

            if not template_loader.exists(template_id):
                errors.append(f"Step '{step.name}': Template '{template_id}' not found")

        return len(errors) == 0, errors

    def _discover_all(self) -> dict[str, WorkflowInfo]:
        """Discover all available workflows."""
        if self._cache:
            return self._cache

        workflows: dict[str, WorkflowInfo] = {}

        # Add built-in workflows
        for workflow_id, data in self.BUILTIN_WORKFLOWS.items():
            workflows[workflow_id] = WorkflowInfo(
                id=workflow_id,
                path=None,
                source="builtin",
                name=data.get("name", workflow_id),
                description=data.get("description", ""),
                step_count=len(data.get("steps", [])),
                tags=data.get("tags", []),
            )

        # Discover custom workflows (later overrides earlier)
        for source, directory in [
            ("user", self._user_dir),
            ("project", self._project_dir),
        ]:
            if directory.exists():
                for path in directory.glob("*.yaml"):
                    try:
                        with open(path, encoding="utf-8") as f:
                            data = yaml.safe_load(f)

                        if not data:
                            continue

                        workflow_id = data.get("id", path.stem)
                        workflows[workflow_id] = WorkflowInfo(
                            id=workflow_id,
                            path=path,
                            source=source,
                            name=data.get("name", workflow_id),
                            description=data.get("description", ""),
                            step_count=len(data.get("steps", [])),
                            tags=data.get("tags", []),
                        )
                    except Exception:
                        continue

        self._cache = workflows
        return workflows


def get_builtin_workflows() -> dict[str, WorkflowInfo]:
    """
    Get built-in workflows.

    Returns:
        Dict of workflow_id -> WorkflowInfo.
    """
    loader = CustomWorkflowLoader()
    result = {}
    for workflow_id, info in loader._discover_all().items():
        if info.source == "builtin":
            result[workflow_id] = info
    return result
