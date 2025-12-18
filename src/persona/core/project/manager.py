"""
Project manager for CRUD operations.

Provides high-level operations for creating, loading, and managing
Persona projects.
"""

import json
from datetime import datetime
from pathlib import Path

import yaml

from persona.core.project.models import (
    DataSource,
    ProjectDefaults,
    ProjectMetadata,
    ProjectTemplate,
)
from persona.core.project.registry import get_registry_manager


class ProjectManager:
    """Manages Persona project lifecycle.

    Handles project creation, loading, configuration, and data source
    management.
    """

    def __init__(self, project_path: Path | None = None):
        """Initialise project manager.

        Args:
            project_path: Path to project directory. If None, attempts to
                         detect project in current directory.
        """
        self._project_path = project_path
        self._metadata: ProjectMetadata | None = None

    @property
    def project_path(self) -> Path | None:
        """Get project path."""
        return self._project_path

    @property
    def metadata(self) -> ProjectMetadata | None:
        """Get project metadata."""
        return self._metadata

    @property
    def project_file(self) -> Path | None:
        """Get path to project.yaml file."""
        if self._project_path is None:
            return None
        return self._project_path / "project.yaml"

    def detect_project(self, start_path: Path | None = None) -> Path | None:
        """Detect project directory by searching up from start path.

        Looks for project.yaml or persona.yaml files.

        Args:
            start_path: Directory to start search from. Defaults to cwd.

        Returns:
            Path to project directory, or None if not found.
        """
        current = start_path or Path.cwd()

        while current != current.parent:
            # Check for project.yaml (new format)
            if (current / "project.yaml").exists():
                return current
            # Check for persona.yaml (legacy format)
            if (current / "persona.yaml").exists():
                return current
            current = current.parent

        return None

    def load(self, project_path: Path | None = None) -> ProjectMetadata:
        """Load project metadata from disk.

        Args:
            project_path: Path to project directory. If None, uses
                         detect_project() to find it.

        Returns:
            ProjectMetadata instance.

        Raises:
            FileNotFoundError: If project file not found.
            ValueError: If project file is invalid.
        """
        if project_path is not None:
            self._project_path = project_path
        elif self._project_path is None:
            detected = self.detect_project()
            if detected is None:
                raise FileNotFoundError("No project found in current directory tree")
            self._project_path = detected

        # Try project.yaml first (new format)
        project_file = self._project_path / "project.yaml"
        if not project_file.exists():
            # Try persona.yaml (legacy format)
            project_file = self._project_path / "persona.yaml"

        if not project_file.exists():
            raise FileNotFoundError(f"Project file not found: {project_file}")

        with open(project_file) as f:
            data = yaml.safe_load(f) or {}

        self._metadata = ProjectMetadata.from_yaml_dict(data)
        return self._metadata

    def save(self) -> Path:
        """Save project metadata to disk.

        Returns:
            Path to saved project file.

        Raises:
            ValueError: If no project loaded.
        """
        if self._metadata is None or self._project_path is None:
            raise ValueError("No project loaded")

        project_file = self._project_path / "project.yaml"

        with open(project_file, "w") as f:
            yaml.dump(
                self._metadata.to_yaml_dict(),
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

        return project_file

    def create(
        self,
        name: str,
        path: Path,
        *,
        template: ProjectTemplate = ProjectTemplate.BASIC,
        description: str | None = None,
        defaults: ProjectDefaults | None = None,
        register: bool = True,
    ) -> ProjectMetadata:
        """Create a new project.

        Args:
            name: Project name.
            path: Directory to create project in.
            template: Project template to use.
            description: Optional project description.
            defaults: Optional default settings.
            register: Whether to register project in global registry.

        Returns:
            ProjectMetadata for the new project.

        Raises:
            FileExistsError: If project directory already exists.
        """
        project_dir = path / name

        if project_dir.exists():
            raise FileExistsError(f"Directory already exists: {project_dir}")

        # Create project metadata
        self._metadata = ProjectMetadata(
            name=name,
            description=description,
            created_at=datetime.now(),
            template=template,
            defaults=defaults or ProjectDefaults(),
        )
        self._project_path = project_dir

        # Create directory structure based on template
        self._create_structure(template)

        # Save project file
        self.save()

        # Register in global registry
        if register:
            registry = get_registry_manager()
            try:
                registry.register_project(name, project_dir)
            except ValueError:
                # Already registered, update path
                registry.update_project_path(name, project_dir)

        return self._metadata

    def _create_structure(self, template: ProjectTemplate) -> None:
        """Create project directory structure.

        Args:
            template: Template to use for structure.
        """
        if self._project_path is None:
            raise ValueError("No project path set")

        project_dir = self._project_path

        if template == ProjectTemplate.BASIC:
            self._create_basic_structure(project_dir)
        elif template == ProjectTemplate.RESEARCH:
            self._create_research_structure(project_dir)

    def _create_basic_structure(self, project_dir: Path) -> None:
        """Create basic template structure.

        Structure:
        project-name/
        ├── project.yaml
        ├── data/
        │   └── README.md
        ├── output/
        │   └── manifest.json
        └── README.md
        """
        # Create directories
        (project_dir / "data").mkdir(parents=True, exist_ok=True)
        (project_dir / "output").mkdir(parents=True, exist_ok=True)

        # Create data README
        data_readme = project_dir / "data" / "README.md"
        data_readme.write_text(
            "# Data Directory\n\n"
            "Place your input data files here.\n\n"
            "Supported formats:\n"
            "- CSV (.csv)\n"
            "- JSON (.json)\n"
            "- YAML (.yaml, .yml)\n"
            "- Plain text (.txt)\n"
            "- Markdown (.md)\n"
        )

        # Create output manifest
        manifest = project_dir / "output" / "manifest.json"
        manifest.write_text(json.dumps({"version": "1.0", "runs": []}, indent=2))

        # Create project README
        readme = project_dir / "README.md"
        name = self._metadata.name if self._metadata else project_dir.name
        desc = self._metadata.description if self._metadata else ""
        readme.write_text(
            f"# {name}\n\n" f"{desc}\n\n"
            if desc
            else f"# {name}\n\n"
            "## Getting Started\n\n"
            "1. Add your data files to `data/`\n"
            "2. Run `persona generate --from " + name + "`\n"
            "3. Find generated personas in `output/`\n\n"
            "## Project Structure\n\n"
            "```\n"
            f"{name}/\n"
            "├── project.yaml    # Project configuration\n"
            "├── data/           # Input data files\n"
            "├── output/         # Generated personas\n"
            "└── README.md       # This file\n"
            "```\n"
        )

    def _create_research_structure(self, project_dir: Path) -> None:
        """Create research template structure.

        Structure:
        project-name/
        ├── project.yaml
        ├── data/
        │   ├── raw/
        │   ├── processed/
        │   └── README.md
        ├── config/
        │   ├── prompts/
        │   │   └── README.md
        │   └── models/
        │       └── README.md
        ├── output/
        │   ├── personas/
        │   ├── exports/
        │   └── manifest.json
        ├── templates/
        │   └── README.md
        └── README.md
        """
        # Create all directories
        dirs = [
            "data/raw",
            "data/processed",
            "config/prompts",
            "config/models",
            "output/personas",
            "output/exports",
            "templates",
        ]
        for d in dirs:
            (project_dir / d).mkdir(parents=True, exist_ok=True)

        # Create data README
        data_readme = project_dir / "data" / "README.md"
        data_readme.write_text(
            "# Data Directory\n\n"
            "Organise your input data:\n\n"
            "- `raw/` - Original, unmodified data files\n"
            "- `processed/` - Cleaned or transformed data\n\n"
            "## Supported Formats\n\n"
            "- CSV (.csv)\n"
            "- JSON (.json)\n"
            "- YAML (.yaml, .yml)\n"
            "- Plain text (.txt)\n"
            "- Markdown (.md)\n"
        )

        # Create config READMEs
        prompts_readme = project_dir / "config" / "prompts" / "README.md"
        prompts_readme.write_text(
            "# Prompt Overrides\n\n"
            "Place custom prompt templates here to override defaults.\n\n"
            "Templates are Jinja2 files that receive:\n"
            "- `data` - The input data\n"
            "- `config` - Generation configuration\n"
        )

        models_readme = project_dir / "config" / "models" / "README.md"
        models_readme.write_text(
            "# Model Configuration\n\n"
            "Place per-model YAML configuration files here.\n\n"
            "Example `claude-sonnet.yaml`:\n"
            "```yaml\n"
            "temperature: 0.7\n"
            "max_tokens: 4096\n"
            "```\n"
        )

        # Create templates README
        templates_readme = project_dir / "templates" / "README.md"
        templates_readme.write_text(
            "# Custom Templates\n\n"
            "Place custom Jinja2 templates for persona generation here.\n\n"
            "These override the built-in templates.\n"
        )

        # Create output manifest
        manifest = project_dir / "output" / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "version": "1.0",
                    "runs": [],
                    "exports": [],
                },
                indent=2,
            )
        )

        # Create project README
        readme = project_dir / "README.md"
        name = self._metadata.name if self._metadata else project_dir.name
        desc = self._metadata.description if self._metadata else ""
        readme.write_text(
            f"# {name}\n\n" f"{desc}\n\n"
            if desc
            else f"# {name}\n\n"
            "## Getting Started\n\n"
            "1. Add raw data to `data/raw/`\n"
            "2. Optionally pre-process into `data/processed/`\n"
            "3. Configure prompts in `config/prompts/` (optional)\n"
            "4. Run `persona generate --from " + name + "`\n"
            "5. Find personas in `output/personas/`\n\n"
            "## Project Structure\n\n"
            "```\n"
            f"{name}/\n"
            "├── project.yaml           # Project configuration\n"
            "├── data/\n"
            "│   ├── raw/               # Original data files\n"
            "│   └── processed/         # Cleaned/transformed data\n"
            "├── config/\n"
            "│   ├── prompts/           # Prompt template overrides\n"
            "│   └── models/            # Per-model configurations\n"
            "├── output/\n"
            "│   ├── personas/          # Generated personas\n"
            "│   └── exports/           # Exported formats\n"
            "├── templates/             # Custom Jinja2 templates\n"
            "└── README.md              # This file\n"
            "```\n"
        )

    def add_data_source(
        self,
        name: str,
        path: str,
        *,
        source_type: str = "raw",
        description: str | None = None,
    ) -> DataSource:
        """Add a data source to the project.

        Args:
            name: Unique identifier for the data source.
            path: Relative path from project root.
            source_type: Type of data (qualitative, quantitative, mixed, raw).
            description: Optional description.

        Returns:
            The created DataSource.

        Raises:
            ValueError: If no project loaded or name already exists.
        """
        if self._metadata is None:
            raise ValueError("No project loaded")

        # Check for duplicate name
        for ds in self._metadata.data_sources:
            if ds.name == name:
                raise ValueError(f"Data source '{name}' already exists")

        from persona.core.project.models import DataSourceType

        data_source = DataSource(
            name=name,
            path=path,
            type=DataSourceType(source_type),
            description=description,
        )

        self._metadata.data_sources.append(data_source)
        self.save()

        return data_source

    def remove_data_source(self, name: str) -> bool:
        """Remove a data source from the project.

        Args:
            name: Data source name.

        Returns:
            True if removed, False if not found.
        """
        if self._metadata is None:
            raise ValueError("No project loaded")

        original_count = len(self._metadata.data_sources)
        self._metadata.data_sources = [
            ds for ds in self._metadata.data_sources if ds.name != name
        ]

        if len(self._metadata.data_sources) < original_count:
            self.save()
            return True
        return False

    def get_data_source(self, name: str) -> DataSource | None:
        """Get a data source by name.

        Args:
            name: Data source name.

        Returns:
            DataSource or None if not found.
        """
        if self._metadata is None:
            return None

        for ds in self._metadata.data_sources:
            if ds.name == name:
                return ds
        return None

    def list_data_sources(self) -> list[DataSource]:
        """List all data sources.

        Returns:
            List of DataSource objects.
        """
        if self._metadata is None:
            return []
        return list(self._metadata.data_sources)

    def update_defaults(
        self,
        *,
        provider: str | None = None,
        model: str | None = None,
        count: int | None = None,
        workflow: str | None = None,
    ) -> None:
        """Update project defaults.

        Args:
            provider: Default LLM provider.
            model: Default model.
            count: Default persona count.
            workflow: Default workflow.
        """
        if self._metadata is None:
            raise ValueError("No project loaded")

        if provider is not None:
            self._metadata.defaults.provider = provider
        if model is not None:
            self._metadata.defaults.model = model
        if count is not None:
            self._metadata.defaults.count = count
        if workflow is not None:
            self._metadata.defaults.workflow = workflow

        self.save()


def load_project(path: Path | None = None) -> ProjectManager:
    """Load a project from disk.

    Convenience function.

    Args:
        path: Path to project directory. Auto-detects if not provided.

    Returns:
        ProjectManager with loaded project.
    """
    manager = ProjectManager()
    manager.load(path)
    return manager


def create_project(
    name: str,
    path: Path,
    *,
    template: str = "basic",
    description: str | None = None,
    register: bool = True,
) -> ProjectManager:
    """Create a new project.

    Convenience function.

    Args:
        name: Project name.
        path: Directory to create project in.
        template: Template name ('basic' or 'research').
        description: Optional project description.
        register: Whether to register in global registry.

    Returns:
        ProjectManager with created project.
    """
    manager = ProjectManager()
    manager.create(
        name,
        path,
        template=ProjectTemplate(template),
        description=description,
        register=register,
    )
    return manager
