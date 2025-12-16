"""
Project models for registry-based project management.

Provides Pydantic models for project metadata, configuration,
and data source definitions.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProjectTemplate(str, Enum):
    """Available project templates."""

    BASIC = "basic"
    RESEARCH = "research"


class DataSourceType(str, Enum):
    """Types of data sources."""

    QUALITATIVE = "qualitative"
    QUANTITATIVE = "quantitative"
    MIXED = "mixed"
    RAW = "raw"


class DataSource(BaseModel):
    """A data source within a project."""

    name: str = Field(..., description="Unique identifier for this data source")
    path: str = Field(..., description="Relative path from project root")
    type: DataSourceType = Field(
        default=DataSourceType.RAW,
        description="Type of data",
    )
    description: str | None = Field(default=None, description="Optional description")

    def get_absolute_path(self, project_root: Path) -> Path:
        """Get absolute path to the data source.

        Args:
            project_root: Root directory of the project.

        Returns:
            Absolute path to the data source file.
        """
        return project_root / self.path


class ProjectDefaults(BaseModel):
    """Default settings for a project."""

    provider: str = Field(default="anthropic", description="Default LLM provider")
    model: str | None = Field(
        default=None,
        description="Default model (uses provider default if not set)",
    )
    count: int = Field(default=3, description="Default persona count")
    workflow: str = Field(default="default", description="Default workflow")
    complexity: str = Field(default="moderate", description="Complexity level")
    detail_level: str = Field(default="standard", description="Detail level")


class ProjectMetadata(BaseModel):
    """Metadata for a Persona project.

    This represents the contents of project.yaml in each project directory.
    """

    name: str = Field(..., description="Project name (used as registry key)")
    description: str | None = Field(default=None, description="Project description")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the project was created",
    )
    template: ProjectTemplate = Field(
        default=ProjectTemplate.BASIC,
        description="Template used to create the project",
    )
    version: str = Field(default="1.0", description="Project file format version")

    defaults: ProjectDefaults = Field(
        default_factory=ProjectDefaults,
        description="Default generation settings",
    )

    data_sources: list[DataSource] = Field(
        default_factory=list,
        description="Registered data sources",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate project name is filesystem-safe."""
        if not v:
            raise ValueError("Project name cannot be empty")
        # Allow alphanumeric, hyphens, underscores
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Project name must contain only letters, numbers, hyphens, "
                "and underscores"
            )
        return v

    def to_yaml_dict(self) -> dict[str, Any]:
        """Convert to dictionary suitable for YAML serialisation.

        Returns:
            Dictionary with datetime converted to ISO format string.
        """
        data = self.model_dump()
        # Convert datetime to ISO format string
        data["created_at"] = self.created_at.isoformat()
        # Convert enums to their values
        data["template"] = self.template.value
        if self.data_sources:
            data["data_sources"] = [
                {**ds, "type": ds["type"]} for ds in data["data_sources"]
            ]
        return data

    @classmethod
    def from_yaml_dict(cls, data: dict[str, Any]) -> "ProjectMetadata":
        """Create from YAML dictionary.

        Args:
            data: Dictionary loaded from YAML.

        Returns:
            ProjectMetadata instance.
        """
        # Handle legacy format (project: name: xxx)
        if "project" in data and "name" in data["project"]:
            # Legacy format
            legacy = data["project"]
            new_data = {
                "name": legacy.get("name"),
                "description": legacy.get("description"),
            }
            if "defaults" in data:
                new_data["defaults"] = data["defaults"]
            data = new_data

        return cls.model_validate(data)


class RegistryEntry(BaseModel):
    """An entry in the project registry."""

    path: str = Field(..., description="Absolute path to project directory")

    def get_path(self) -> Path:
        """Get path as Path object."""
        return Path(self.path)


class GlobalDefaults(BaseModel):
    """Global defaults stored in the registry."""

    provider: str = Field(default="anthropic", description="Default LLM provider")
    model: str | None = Field(
        default=None,
        description="Default model (uses provider default if not set)",
    )
    count: int = Field(default=3, description="Default persona count")


class ProjectRegistry(BaseModel):
    """The project registry file structure.

    Stored at ~/.config/persona/config.yaml or ~/.persona/config.yaml.
    """

    version: str = Field(default="1.0", description="Registry file format version")
    defaults: GlobalDefaults = Field(
        default_factory=GlobalDefaults,
        description="Global defaults",
    )
    projects: dict[str, str] = Field(
        default_factory=dict,
        description="Map of project name to absolute path",
    )

    def get_project_path(self, name: str) -> Path | None:
        """Get path to a registered project.

        Args:
            name: Project name.

        Returns:
            Path to project directory, or None if not registered.
        """
        if name in self.projects:
            return Path(self.projects[name])
        return None

    def register(self, name: str, path: Path) -> None:
        """Register a project.

        Args:
            name: Project name.
            path: Absolute path to project directory.
        """
        self.projects[name] = str(path.resolve())

    def unregister(self, name: str) -> bool:
        """Unregister a project.

        Args:
            name: Project name.

        Returns:
            True if project was unregistered, False if not found.
        """
        if name in self.projects:
            del self.projects[name]
            return True
        return False

    def list_projects(self) -> list[tuple[str, Path]]:
        """List all registered projects.

        Returns:
            List of (name, path) tuples.
        """
        return [(name, Path(path)) for name, path in self.projects.items()]
