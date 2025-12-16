"""
Project management module.

Provides registry-based project management, allowing projects to be
referenced by name from anywhere on the filesystem.

Example:
    ```python
    from persona.core.project import (
        create_project,
        load_project,
        resolve_project,
        get_registry_manager,
    )

    # Create a new project
    manager = create_project(
        name="my-research",
        path=Path.cwd(),
        template="research",
        description="User research study",
    )

    # Load existing project
    manager = load_project(Path("./my-research"))

    # Resolve project by name
    ctx = resolve_project("my-research:interviews")
    print(ctx.project.name)
    print(ctx.data_source.path)
    ```
"""

from persona.core.project.context import (
    ProjectContext,
    is_project_reference,
    resolve_project,
)
from persona.core.project.manager import (
    ProjectManager,
    create_project,
    load_project,
)
from persona.core.project.models import (
    DataSource,
    DataSourceType,
    GlobalDefaults,
    ProjectDefaults,
    ProjectMetadata,
    ProjectRegistry,
    ProjectTemplate,
)
from persona.core.project.registry import (
    RegistryManager,
    get_project_path,
    get_registry_manager,
    get_registry_path,
    list_registered_projects,
)

__all__ = [
    # Models
    "DataSource",
    "DataSourceType",
    "GlobalDefaults",
    "ProjectDefaults",
    "ProjectMetadata",
    "ProjectRegistry",
    "ProjectTemplate",
    # Registry
    "RegistryManager",
    "get_project_path",
    "get_registry_manager",
    "get_registry_path",
    "list_registered_projects",
    # Manager
    "ProjectManager",
    "create_project",
    "load_project",
    # Context
    "ProjectContext",
    "is_project_reference",
    "resolve_project",
]
