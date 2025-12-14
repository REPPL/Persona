"""
Template management functionality.

This module provides the TemplateManager class for managing persona
templates across different domains and formats.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import json
import yaml


class TemplateCategory(Enum):
    """Categories for persona templates."""

    UX = "ux"
    MARKETING = "marketing"
    ACADEMIC = "academic"
    PRODUCT = "product"
    CUSTOM = "custom"


@dataclass
class TemplateField:
    """
    Definition of a field in a persona template.

    Attributes:
        name: Field identifier.
        label: Human-readable label.
        description: Field description for prompts.
        required: Whether field is required.
        field_type: Type of field (text, list, dict).
        default: Default value if not provided.
        examples: Example values for this field.
    """

    name: str
    label: str
    description: str = ""
    required: bool = True
    field_type: str = "text"
    default: Any = None
    examples: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "required": self.required,
            "type": self.field_type,
            "default": self.default,
            "examples": self.examples,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TemplateField":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            label=data["label"],
            description=data.get("description", ""),
            required=data.get("required", True),
            field_type=data.get("type", "text"),
            default=data.get("default"),
            examples=data.get("examples", []),
        )


@dataclass
class PersonaTemplate:
    """
    Template for generating personas in a specific format.

    Attributes:
        id: Unique template identifier.
        name: Human-readable template name.
        description: Template description.
        category: Template category.
        version: Template version.
        fields: List of field definitions.
        prompt_additions: Additional prompt text for LLM.
        output_format: Preferred output format.
        is_system: Whether this is a built-in template.
    """

    id: str
    name: str
    description: str = ""
    category: TemplateCategory = TemplateCategory.CUSTOM
    version: str = "1.0.0"
    fields: list[TemplateField] = field(default_factory=list)
    prompt_additions: str = ""
    output_format: str = "json"
    is_system: bool = False

    @property
    def required_fields(self) -> list[TemplateField]:
        """Return only required fields."""
        return [f for f in self.fields if f.required]

    @property
    def optional_fields(self) -> list[TemplateField]:
        """Return only optional fields."""
        return [f for f in self.fields if not f.required]

    def get_field(self, name: str) -> TemplateField | None:
        """Get a field by name."""
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def validate(self) -> list[str]:
        """
        Validate the template configuration.

        Returns:
            List of validation error messages.
        """
        errors = []

        if not self.id:
            errors.append("Template ID is required")

        if not self.name:
            errors.append("Template name is required")

        if not self.fields:
            errors.append("Template must have at least one field")

        # Check for duplicate field names
        field_names = [f.name for f in self.fields]
        if len(field_names) != len(set(field_names)):
            errors.append("Duplicate field names found")

        # Check for id and name fields
        has_id = any(f.name == "id" for f in self.fields)
        has_name = any(f.name == "name" for f in self.fields)

        if not has_id:
            errors.append("Template must include 'id' field")
        if not has_name:
            errors.append("Template must include 'name' field")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version,
            "fields": [f.to_dict() for f in self.fields],
            "prompt_additions": self.prompt_additions,
            "output_format": self.output_format,
            "is_system": self.is_system,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PersonaTemplate":
        """Create from dictionary."""
        category_str = data.get("category", "custom")
        try:
            category = TemplateCategory(category_str)
        except ValueError:
            category = TemplateCategory.CUSTOM

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            category=category,
            version=data.get("version", "1.0.0"),
            fields=[TemplateField.from_dict(f) for f in data.get("fields", [])],
            prompt_additions=data.get("prompt_additions", ""),
            output_format=data.get("output_format", "json"),
            is_system=data.get("is_system", False),
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def to_yaml(self) -> str:
        """Convert to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False)


class TemplateManager:
    """
    Manages persona templates across system and user directories.

    Provides template discovery, loading, saving, and validation.

    Example:
        manager = TemplateManager()
        template = manager.get_template("ux-research")
        print(f"Using: {template.name}")
    """

    # Default template file extension
    TEMPLATE_EXTENSION = ".yaml"

    def __init__(
        self,
        user_templates_dir: Path | None = None,
    ) -> None:
        """
        Initialise the template manager.

        Args:
            user_templates_dir: Directory for user templates.
        """
        self._user_dir = user_templates_dir
        self._system_templates: dict[str, PersonaTemplate] = {}
        self._user_templates: dict[str, PersonaTemplate] = {}

        # Load built-in templates
        self._load_system_templates()

    @property
    def templates(self) -> dict[str, PersonaTemplate]:
        """Return all available templates (system + user)."""
        # User templates override system templates
        all_templates = dict(self._system_templates)
        all_templates.update(self._user_templates)
        return all_templates

    def list_templates(
        self,
        category: TemplateCategory | None = None,
    ) -> list[PersonaTemplate]:
        """
        List all available templates.

        Args:
            category: Filter by category.

        Returns:
            List of templates.
        """
        templates = list(self.templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        return sorted(templates, key=lambda t: t.name)

    def get_template(self, template_id: str) -> PersonaTemplate | None:
        """
        Get a template by ID.

        Args:
            template_id: Template identifier.

        Returns:
            Template if found, None otherwise.
        """
        return self.templates.get(template_id)

    def get_default_template(self) -> PersonaTemplate:
        """Get the default template."""
        return self._system_templates.get("default", self._create_default_template())

    def save_template(
        self,
        template: PersonaTemplate,
        path: Path | None = None,
    ) -> Path:
        """
        Save a template to file.

        Args:
            template: Template to save.
            path: Optional save path (uses user dir if not provided).

        Returns:
            Path where template was saved.

        Raises:
            ValueError: If template validation fails.
        """
        errors = template.validate()
        if errors:
            raise ValueError(f"Template validation failed: {'; '.join(errors)}")

        if path is None:
            if self._user_dir is None:
                raise ValueError("No user templates directory configured")
            self._user_dir.mkdir(parents=True, exist_ok=True)
            path = self._user_dir / f"{template.id}{self.TEMPLATE_EXTENSION}"

        with open(path, "w") as f:
            yaml.dump(template.to_dict(), f, default_flow_style=False)

        # Add to user templates
        self._user_templates[template.id] = template

        return path

    def load_template(self, path: Path) -> PersonaTemplate:
        """
        Load a template from file.

        Args:
            path: Path to template file.

        Returns:
            Loaded template.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file is invalid.
        """
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")

        with open(path) as f:
            if path.suffix == ".json":
                data = json.load(f)
            else:
                data = yaml.safe_load(f)

        template = PersonaTemplate.from_dict(data)

        errors = template.validate()
        if errors:
            raise ValueError(f"Invalid template: {'; '.join(errors)}")

        return template

    def import_template(self, path: Path) -> PersonaTemplate:
        """
        Import a template from file into user templates.

        Args:
            path: Path to template file.

        Returns:
            Imported template.
        """
        template = self.load_template(path)
        template.is_system = False

        self._user_templates[template.id] = template

        return template

    def export_template(
        self,
        template_id: str,
        path: Path,
        format: str = "yaml",
    ) -> Path:
        """
        Export a template to file.

        Args:
            template_id: Template to export.
            path: Destination path.
            format: Output format (yaml or json).

        Returns:
            Path where template was exported.

        Raises:
            KeyError: If template not found.
        """
        template = self.get_template(template_id)
        if template is None:
            raise KeyError(f"Template not found: {template_id}")

        with open(path, "w") as f:
            if format == "json":
                json.dump(template.to_dict(), f, indent=2)
            else:
                yaml.dump(template.to_dict(), f, default_flow_style=False)

        return path

    def delete_template(self, template_id: str) -> bool:
        """
        Delete a user template.

        Args:
            template_id: Template to delete.

        Returns:
            True if deleted, False if not found.

        Raises:
            ValueError: If trying to delete a system template.
        """
        if template_id in self._system_templates:
            raise ValueError("Cannot delete system templates")

        if template_id in self._user_templates:
            del self._user_templates[template_id]

            # Remove file if it exists
            if self._user_dir:
                path = self._user_dir / f"{template_id}{self.TEMPLATE_EXTENSION}"
                if path.exists():
                    path.unlink()

            return True

        return False

    def reload_user_templates(self) -> int:
        """
        Reload user templates from disk.

        Returns:
            Number of templates loaded.
        """
        self._user_templates.clear()

        if self._user_dir is None or not self._user_dir.exists():
            return 0

        count = 0
        for path in self._user_dir.glob(f"*{self.TEMPLATE_EXTENSION}"):
            try:
                template = self.load_template(path)
                self._user_templates[template.id] = template
                count += 1
            except (ValueError, yaml.YAMLError):
                # Skip invalid templates
                pass

        return count

    def _load_system_templates(self) -> None:
        """Load built-in system templates."""
        # Default template
        self._system_templates["default"] = self._create_default_template()

        # UX Research template
        self._system_templates["ux-research"] = self._create_ux_template()

        # Marketing template
        self._system_templates["marketing"] = self._create_marketing_template()

        # Academic template
        self._system_templates["academic"] = self._create_academic_template()

        # Product template
        self._system_templates["product"] = self._create_product_template()

    def _create_default_template(self) -> PersonaTemplate:
        """Create the default persona template."""
        return PersonaTemplate(
            id="default",
            name="Default Persona",
            description="Standard persona format suitable for most use cases.",
            category=TemplateCategory.CUSTOM,
            is_system=True,
            fields=[
                TemplateField(
                    name="id",
                    label="ID",
                    description="Unique identifier for the persona",
                    required=True,
                ),
                TemplateField(
                    name="name",
                    label="Name",
                    description="Representative name for the persona",
                    required=True,
                ),
                TemplateField(
                    name="summary",
                    label="Summary",
                    description="Brief overview of the persona",
                    required=True,
                ),
                TemplateField(
                    name="goals",
                    label="Goals",
                    description="What the persona is trying to achieve",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="pain_points",
                    label="Pain Points",
                    description="Frustrations and challenges faced",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="behaviours",
                    label="Behaviours",
                    description="Key behaviours and patterns",
                    field_type="list",
                    required=False,
                ),
                TemplateField(
                    name="demographics",
                    label="Demographics",
                    description="Relevant demographic information",
                    field_type="dict",
                    required=False,
                ),
            ],
        )

    def _create_ux_template(self) -> PersonaTemplate:
        """Create UX research persona template."""
        return PersonaTemplate(
            id="ux-research",
            name="UX Research Persona",
            description="Persona format optimised for UX research and design.",
            category=TemplateCategory.UX,
            is_system=True,
            prompt_additions=(
                "Focus on user experience aspects: mental models, workflow patterns, "
                "technology comfort, and interface preferences."
            ),
            fields=[
                TemplateField(
                    name="id",
                    label="ID",
                    description="Unique identifier",
                    required=True,
                ),
                TemplateField(
                    name="name",
                    label="Name",
                    description="Representative name",
                    required=True,
                ),
                TemplateField(
                    name="archetype",
                    label="Archetype",
                    description="User archetype (e.g., Power User, Novice)",
                    required=True,
                ),
                TemplateField(
                    name="goals",
                    label="Goals",
                    description="User goals and objectives",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="frustrations",
                    label="Frustrations",
                    description="UX pain points and frustrations",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="mental_model",
                    label="Mental Model",
                    description="How the user thinks about the system",
                    required=True,
                ),
                TemplateField(
                    name="tech_comfort",
                    label="Technology Comfort",
                    description="Level of technology comfort (1-5)",
                    required=True,
                ),
                TemplateField(
                    name="preferred_channels",
                    label="Preferred Channels",
                    description="Preferred interaction channels",
                    field_type="list",
                    required=False,
                ),
                TemplateField(
                    name="accessibility_needs",
                    label="Accessibility Needs",
                    description="Any accessibility requirements",
                    field_type="list",
                    required=False,
                ),
            ],
        )

    def _create_marketing_template(self) -> PersonaTemplate:
        """Create marketing persona template."""
        return PersonaTemplate(
            id="marketing",
            name="Marketing Persona",
            description="Persona format for marketing and audience targeting.",
            category=TemplateCategory.MARKETING,
            is_system=True,
            prompt_additions=(
                "Focus on marketing-relevant aspects: buying behaviour, "
                "brand preferences, media consumption, and decision factors."
            ),
            fields=[
                TemplateField(
                    name="id",
                    label="ID",
                    description="Unique identifier",
                    required=True,
                ),
                TemplateField(
                    name="name",
                    label="Name",
                    description="Representative name",
                    required=True,
                ),
                TemplateField(
                    name="segment",
                    label="Segment",
                    description="Market segment this persona represents",
                    required=True,
                ),
                TemplateField(
                    name="demographics",
                    label="Demographics",
                    description="Age, income, location, occupation",
                    field_type="dict",
                    required=True,
                ),
                TemplateField(
                    name="goals",
                    label="Goals",
                    description="Customer goals and desires",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="pain_points",
                    label="Pain Points",
                    description="Problems and frustrations",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="buying_behaviour",
                    label="Buying Behaviour",
                    description="How they make purchase decisions",
                    required=True,
                ),
                TemplateField(
                    name="media_consumption",
                    label="Media Consumption",
                    description="Preferred media and channels",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="brand_affinity",
                    label="Brand Affinity",
                    description="Brands they trust and use",
                    field_type="list",
                    required=False,
                ),
                TemplateField(
                    name="objections",
                    label="Common Objections",
                    description="Typical objections to purchase",
                    field_type="list",
                    required=False,
                ),
            ],
        )

    def _create_academic_template(self) -> PersonaTemplate:
        """Create academic research persona template."""
        return PersonaTemplate(
            id="academic",
            name="Academic Research Persona",
            description="Persona format for academic and HCI research.",
            category=TemplateCategory.ACADEMIC,
            is_system=True,
            prompt_additions=(
                "Focus on research-relevant aspects: theoretical grounding, "
                "observable behaviours, and empirical evidence from the data."
            ),
            fields=[
                TemplateField(
                    name="id",
                    label="ID",
                    description="Unique identifier",
                    required=True,
                ),
                TemplateField(
                    name="name",
                    label="Name",
                    description="Pseudonymous name",
                    required=True,
                ),
                TemplateField(
                    name="description",
                    label="Description",
                    description="Rich description of the persona",
                    required=True,
                ),
                TemplateField(
                    name="goals",
                    label="Goals",
                    description="Research-relevant goals",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="behaviours",
                    label="Behaviours",
                    description="Observable behaviours from data",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="context",
                    label="Context",
                    description="Situational context and environment",
                    required=True,
                ),
                TemplateField(
                    name="motivations",
                    label="Motivations",
                    description="Underlying motivations and needs",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="data_sources",
                    label="Data Sources",
                    description="Participant IDs contributing to this persona",
                    field_type="list",
                    required=False,
                ),
                TemplateField(
                    name="quotes",
                    label="Representative Quotes",
                    description="Key quotes from source data",
                    field_type="list",
                    required=False,
                ),
            ],
        )

    def _create_product_template(self) -> PersonaTemplate:
        """Create product development persona template."""
        return PersonaTemplate(
            id="product",
            name="Product Development Persona",
            description="Persona format for product teams and feature planning.",
            category=TemplateCategory.PRODUCT,
            is_system=True,
            prompt_additions=(
                "Focus on product-relevant aspects: feature priorities, "
                "use cases, workflow integration, and success metrics."
            ),
            fields=[
                TemplateField(
                    name="id",
                    label="ID",
                    description="Unique identifier",
                    required=True,
                ),
                TemplateField(
                    name="name",
                    label="Name",
                    description="Representative name",
                    required=True,
                ),
                TemplateField(
                    name="role",
                    label="Role",
                    description="Professional role or user type",
                    required=True,
                ),
                TemplateField(
                    name="goals",
                    label="Goals",
                    description="What they want to accomplish",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="pain_points",
                    label="Pain Points",
                    description="Current problems and frustrations",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="use_cases",
                    label="Use Cases",
                    description="Key scenarios and use cases",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="feature_priorities",
                    label="Feature Priorities",
                    description="Most important features for this persona",
                    field_type="list",
                    required=True,
                ),
                TemplateField(
                    name="success_metrics",
                    label="Success Metrics",
                    description="How they measure success",
                    field_type="list",
                    required=False,
                ),
                TemplateField(
                    name="current_tools",
                    label="Current Tools",
                    description="Tools currently used",
                    field_type="list",
                    required=False,
                ),
            ],
        )
