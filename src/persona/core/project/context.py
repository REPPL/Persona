"""
Project context resolution.

Provides context resolution for project-aware operations, resolving
project references from names, paths, or current directory.
"""

from pathlib import Path

from persona.core.project.manager import ProjectManager
from persona.core.project.models import DataSource, ProjectMetadata
from persona.core.project.registry import get_registry_manager


class ProjectContext:
    """Resolves and manages project context.

    Handles resolution of project references in the format:
    - project-name (looks up in registry)
    - project-name:source (project with specific data source)
    - /path/to/project (direct path)
    - ./relative/path (relative path)

    Example:
        ```python
        ctx = ProjectContext.resolve("my-research:interviews")
        print(ctx.project.name)  # "my-research"
        print(ctx.data_source.name)  # "interviews"
        ```
    """

    def __init__(
        self,
        project: ProjectMetadata,
        project_path: Path,
        data_source: DataSource | None = None,
    ):
        """Initialise project context.

        Args:
            project: Project metadata.
            project_path: Path to project directory.
            data_source: Optional specific data source.
        """
        self.project = project
        self.project_path = project_path
        self.data_source = data_source

    @classmethod
    def resolve(cls, reference: str) -> "ProjectContext":
        """Resolve a project reference to a context.

        Args:
            reference: Project reference in one of these formats:
                - "project-name" - Look up in registry
                - "project-name:source" - Project with specific data source
                - "/path/to/project" - Direct absolute path
                - "./relative/path" - Relative path

        Returns:
            ProjectContext instance.

        Raises:
            ValueError: If project cannot be resolved.
            FileNotFoundError: If project path doesn't exist.
        """
        # Check for data source suffix
        data_source_name: str | None = None
        if ":" in reference and not reference.startswith("/"):
            reference, data_source_name = reference.rsplit(":", 1)

        # Determine if this is a path or a name
        if reference.startswith("/") or reference.startswith("./") or reference.startswith(".."):
            # It's a path
            project_path = Path(reference).resolve()
        else:
            # It's a project name - look up in registry
            registry = get_registry_manager()
            project_path = registry.get_project_path(reference)

            if project_path is None:
                raise ValueError(
                    f"Project '{reference}' not found in registry. "
                    f"Register it with: persona project register {reference} /path/to/project"
                )

        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")

        # Load project
        manager = ProjectManager(project_path)
        metadata = manager.load(project_path)

        # Resolve data source if specified
        data_source: DataSource | None = None
        if data_source_name:
            data_source = manager.get_data_source(data_source_name)
            if data_source is None:
                available = [ds.name for ds in manager.list_data_sources()]
                raise ValueError(
                    f"Data source '{data_source_name}' not found in project. "
                    f"Available: {', '.join(available) if available else 'none'}"
                )

        return cls(
            project=metadata,
            project_path=project_path,
            data_source=data_source,
        )

    @classmethod
    def from_current_directory(cls) -> "ProjectContext | None":
        """Resolve project from current directory.

        Returns:
            ProjectContext if a project is found, None otherwise.
        """
        manager = ProjectManager()
        project_path = manager.detect_project()

        if project_path is None:
            return None

        try:
            metadata = manager.load(project_path)
            return cls(project=metadata, project_path=project_path)
        except Exception:
            return None

    def get_data_path(self) -> Path | None:
        """Get path to data source or data directory.

        Returns:
            Path to specific data source file, or data directory if no
            specific source was requested.
        """
        if self.data_source is not None:
            return self.data_source.get_absolute_path(self.project_path)

        # Return first data source if available
        manager = ProjectManager(self.project_path)
        try:
            manager.load()
            sources = manager.list_data_sources()
            if sources:
                return sources[0].get_absolute_path(self.project_path)
        except Exception:
            pass

        # Fall back to data directory
        data_dir = self.project_path / "data"
        if data_dir.exists():
            return data_dir
        return None

    def get_output_path(self) -> Path:
        """Get path to output directory.

        Returns:
            Path to output directory (creates if doesn't exist).
        """
        output_dir = self.project_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def get_config_path(self) -> Path | None:
        """Get path to config directory.

        Returns:
            Path to config directory if it exists, None otherwise.
        """
        config_dir = self.project_path / "config"
        if config_dir.exists():
            return config_dir
        return None


def resolve_project(reference: str | None = None) -> ProjectContext | None:
    """Resolve a project reference.

    Convenience function.

    Args:
        reference: Project reference or None for current directory.

    Returns:
        ProjectContext or None if not found.
    """
    if reference is None:
        return ProjectContext.from_current_directory()

    try:
        return ProjectContext.resolve(reference)
    except (ValueError, FileNotFoundError):
        return None


def is_project_reference(value: str) -> bool:
    """Check if a value looks like a project reference.

    Args:
        value: String to check.

    Returns:
        True if it looks like a project name (not a file path).
    """
    # If it contains path separators or file extensions, it's probably a path
    if "/" in value or "\\" in value:
        return False
    if "." in value and not ":" in value:
        # Has extension, probably a file
        return False

    # Check if it's registered
    registry = get_registry_manager()
    # Strip data source suffix for check
    name = value.split(":")[0] if ":" in value else value
    return registry.project_exists(name)
