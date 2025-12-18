"""
Custom prompt template configuration.

This module provides template management for custom Jinja2 prompt templates.
"""

from pathlib import Path
from typing import ClassVar

from jinja2 import BaseLoader, Environment, meta
from pydantic import BaseModel, ConfigDict, Field


class TemplateMetadata(BaseModel):
    """Metadata for a prompt template."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    name: str = Field(..., description="Human-readable template name")
    description: str = Field(
        default="",
        description="Template description",
    )
    author: str = Field(
        default="",
        description="Template author",
    )
    version: str = Field(
        default="1.0.0",
        description="Template version",
    )
    extends: str | None = Field(
        default=None,
        description="Base template to extend",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorisation",
    )

    @classmethod
    def from_template(cls, template_content: str) -> "TemplateMetadata":
        """
        Extract metadata from template content.

        Looks for a YAML front matter block at the start:
        {# ---
        name: Template Name
        description: Description
        --- #}
        """
        import yaml

        lines = template_content.strip().split("\n")

        # Check for front matter
        if not lines[0].strip() == "{# ---":
            return cls(name="Unnamed Template")

        # Find end of front matter
        end_idx = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "--- #}":
                end_idx = i
                break

        if end_idx is None:
            return cls(name="Unnamed Template")

        # Parse YAML front matter
        yaml_content = "\n".join(lines[1:end_idx])
        try:
            data = yaml.safe_load(yaml_content)
            return cls(**data) if data else cls(name="Unnamed Template")
        except Exception:
            return cls(name="Unnamed Template")


class TemplateInfo(BaseModel):
    """Information about a template."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    id: str = Field(..., description="Template identifier (filename without extension)")
    path: Path = Field(..., description="Full path to the template file")
    source: str = Field(..., description="Source: 'builtin', 'user', or 'project'")
    metadata: TemplateMetadata = Field(
        default_factory=lambda: TemplateMetadata(name="Unnamed Template"),
        description="Template metadata",
    )
    variables: list[str] = Field(
        default_factory=list,
        description="Variables used in the template",
    )


class TemplateLoader:
    """
    Loader for custom prompt templates.

    Searches for templates in:
    1. Built-in templates (bundled with persona)
    2. User templates (~/.persona/templates/)
    3. Project templates (.persona/templates/)

    Project templates override user templates, which override built-ins.
    """

    DEFAULT_USER_DIR: ClassVar[Path] = Path.home() / ".persona" / "templates"
    DEFAULT_PROJECT_DIR: ClassVar[Path] = Path(".persona") / "templates"

    def __init__(
        self,
        user_dir: Path | None = None,
        project_dir: Path | None = None,
    ) -> None:
        """
        Initialise the template loader.

        Args:
            user_dir: Override user template directory.
            project_dir: Override project template directory.
        """
        self._user_dir = user_dir or self.DEFAULT_USER_DIR
        self._project_dir = project_dir or self.DEFAULT_PROJECT_DIR
        self._cache: dict[str, TemplateInfo] = {}

    @property
    def builtin_dir(self) -> Path:
        """Path to built-in templates."""
        return Path(__file__).parent.parent / "prompts" / "templates"

    def list_templates(
        self,
        source: str | None = None,
        tag: str | None = None,
    ) -> list[str]:
        """
        List available template IDs.

        Args:
            source: Filter by source ('builtin', 'user', 'project').
            tag: Filter by tag.

        Returns:
            List of template IDs.
        """
        templates = []

        # Collect from all sources
        for template_id, info in self._discover_all().items():
            if source and info.source != source:
                continue
            if tag and tag not in info.metadata.tags:
                continue
            templates.append(template_id)

        return sorted(set(templates))

    def exists(self, template_id: str) -> bool:
        """Check if a template exists."""
        return template_id in self._discover_all()

    def get_info(self, template_id: str) -> TemplateInfo:
        """
        Get information about a template.

        Args:
            template_id: Template identifier.

        Returns:
            TemplateInfo object.

        Raises:
            FileNotFoundError: If template not found.
        """
        templates = self._discover_all()
        if template_id not in templates:
            raise FileNotFoundError(f"Template not found: {template_id}")
        return templates[template_id]

    def load(self, template_id: str) -> str:
        """
        Load template content.

        Args:
            template_id: Template identifier.

        Returns:
            Template content as string.

        Raises:
            FileNotFoundError: If template not found.
        """
        info = self.get_info(template_id)
        return info.path.read_text(encoding="utf-8")

    def get_variables(self, template_id: str) -> list[str]:
        """
        Get variables used in a template.

        Args:
            template_id: Template identifier.

        Returns:
            List of variable names.
        """
        content = self.load(template_id)
        env = Environment(loader=BaseLoader())
        ast = env.parse(content)
        return list(meta.find_undeclared_variables(ast))

    def validate_template(
        self, template_id: str, **variables
    ) -> tuple[bool, list[str]]:
        """
        Validate a template with given variables.

        Args:
            template_id: Template identifier.
            **variables: Variables to validate.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []

        try:
            content = self.load(template_id)
        except FileNotFoundError as e:
            return False, [str(e)]

        # Check for required variables
        required = set(self.get_variables(template_id))
        provided = set(variables.keys())
        missing = required - provided

        if missing:
            errors.append(f"Missing variables: {', '.join(sorted(missing))}")

        # Try to render
        if not errors:
            try:
                env = Environment(loader=BaseLoader())
                template = env.from_string(content)
                template.render(**variables)
            except Exception as e:
                errors.append(f"Render error: {e}")

        return len(errors) == 0, errors

    def save(
        self,
        template_id: str,
        content: str,
        user_level: bool = True,
        overwrite: bool = False,
    ) -> Path:
        """
        Save a template.

        Args:
            template_id: Template identifier.
            content: Template content.
            user_level: Save to user directory (True) or project (False).
            overwrite: Overwrite existing template.

        Returns:
            Path to saved template.

        Raises:
            FileExistsError: If template exists and overwrite is False.
        """
        target_dir = self._user_dir if user_level else self._project_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        path = target_dir / f"{template_id}.j2"

        if path.exists() and not overwrite:
            raise FileExistsError(f"Template already exists: {path}")

        path.write_text(content, encoding="utf-8")

        # Clear cache
        self._cache.clear()

        return path

    def delete(self, template_id: str) -> bool:
        """
        Delete a custom template.

        Args:
            template_id: Template identifier.

        Returns:
            True if deleted, False if not found or is built-in.
        """
        info = self._discover_all().get(template_id)

        if not info:
            return False

        if info.source == "builtin":
            return False

        try:
            info.path.unlink()
            self._cache.clear()
            return True
        except Exception:
            return False

    def export_template(self, template_id: str, output_path: Path) -> Path:
        """
        Export a template to a file.

        Args:
            template_id: Template identifier.
            output_path: Output file path.

        Returns:
            Path to exported file.
        """
        content = self.load(template_id)
        output_path.write_text(content, encoding="utf-8")
        return output_path

    def import_template(
        self,
        source_path: Path,
        template_id: str | None = None,
        user_level: bool = True,
        overwrite: bool = False,
    ) -> str:
        """
        Import a template from a file.

        Args:
            source_path: Source file path.
            template_id: Custom template ID (uses filename if not provided).
            user_level: Save to user directory (True) or project (False).
            overwrite: Overwrite existing template.

        Returns:
            Imported template ID.
        """
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        content = source_path.read_text(encoding="utf-8")

        # Determine template ID
        if not template_id:
            template_id = source_path.stem

        self.save(template_id, content, user_level=user_level, overwrite=overwrite)
        return template_id

    def create_from_builtin(
        self,
        builtin_id: str,
        new_id: str,
        user_level: bool = True,
    ) -> Path:
        """
        Create a custom template based on a built-in.

        Args:
            builtin_id: Built-in template to copy.
            new_id: New template ID.
            user_level: Save to user directory.

        Returns:
            Path to new template.
        """
        info = self._discover_all().get(builtin_id)
        if not info or info.source != "builtin":
            raise FileNotFoundError(f"Built-in template not found: {builtin_id}")

        content = self.load(builtin_id)
        return self.save(new_id, content, user_level=user_level)

    def _discover_all(self) -> dict[str, TemplateInfo]:
        """Discover all available templates."""
        if self._cache:
            return self._cache

        templates: dict[str, TemplateInfo] = {}

        # Discover in order of precedence (later overrides earlier)
        for source, directory in [
            ("builtin", self.builtin_dir),
            ("user", self._user_dir),
            ("project", self._project_dir),
        ]:
            if directory.exists():
                for path in directory.glob("*.j2"):
                    template_id = path.stem
                    content = path.read_text(encoding="utf-8")

                    # Extract metadata and variables
                    metadata = TemplateMetadata.from_template(content)
                    env = Environment(loader=BaseLoader())
                    try:
                        ast = env.parse(content)
                        variables = list(meta.find_undeclared_variables(ast))
                    except Exception:
                        variables = []

                    templates[template_id] = TemplateInfo(
                        id=template_id,
                        path=path,
                        source=source,
                        metadata=metadata,
                        variables=variables,
                    )

        self._cache = templates
        return templates


def get_builtin_templates() -> dict[str, TemplateInfo]:
    """
    Get built-in templates.

    Returns:
        Dict of template_id -> TemplateInfo.
    """
    loader = TemplateLoader()
    result = {}
    for template_id, info in loader._discover_all().items():
        if info.source == "builtin":
            result[template_id] = info
    return result
