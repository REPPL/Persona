"""
Tests for persona templates functionality (F-023).
"""

from pathlib import Path

import pytest
from persona.core.templates import (
    PersonaTemplate,
    TemplateCategory,
    TemplateField,
    TemplateManager,
)


class TestTemplateCategory:
    """Tests for TemplateCategory enum."""

    def test_category_values(self):
        """Test category enum values."""
        assert TemplateCategory.UX.value == "ux"
        assert TemplateCategory.MARKETING.value == "marketing"
        assert TemplateCategory.ACADEMIC.value == "academic"
        assert TemplateCategory.PRODUCT.value == "product"
        assert TemplateCategory.CUSTOM.value == "custom"


class TestTemplateField:
    """Tests for TemplateField dataclass."""

    def test_basic_field(self):
        """Test creating a basic field."""
        field = TemplateField(
            name="goals",
            label="Goals",
            description="User goals",
        )

        assert field.name == "goals"
        assert field.label == "Goals"
        assert field.required is True
        assert field.field_type == "text"

    def test_field_with_options(self):
        """Test field with all options."""
        field = TemplateField(
            name="items",
            label="Items",
            description="List of items",
            required=False,
            field_type="list",
            default=[],
            examples=["Item 1", "Item 2"],
        )

        assert field.required is False
        assert field.field_type == "list"
        assert field.default == []
        assert len(field.examples) == 2

    def test_to_dict(self):
        """Test conversion to dictionary."""
        field = TemplateField(
            name="name",
            label="Name",
            description="Persona name",
        )

        data = field.to_dict()

        assert data["name"] == "name"
        assert data["label"] == "Name"
        assert data["required"] is True

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "name": "goals",
            "label": "Goals",
            "description": "User goals",
            "type": "list",
            "required": True,
        }

        field = TemplateField.from_dict(data)

        assert field.name == "goals"
        assert field.field_type == "list"


class TestPersonaTemplate:
    """Tests for PersonaTemplate dataclass."""

    def test_basic_template(self):
        """Test creating a basic template."""
        template = PersonaTemplate(
            id="test",
            name="Test Template",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )

        assert template.id == "test"
        assert template.name == "Test Template"
        assert len(template.fields) == 2
        assert template.category == TemplateCategory.CUSTOM

    def test_required_fields(self):
        """Test required_fields property."""
        template = PersonaTemplate(
            id="test",
            name="Test",
            fields=[
                TemplateField(name="id", label="ID", required=True),
                TemplateField(name="name", label="Name", required=True),
                TemplateField(name="notes", label="Notes", required=False),
            ],
        )

        assert len(template.required_fields) == 2
        assert len(template.optional_fields) == 1

    def test_get_field(self):
        """Test getting a field by name."""
        template = PersonaTemplate(
            id="test",
            name="Test",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )

        field = template.get_field("name")
        assert field is not None
        assert field.label == "Name"

        missing = template.get_field("nonexistent")
        assert missing is None

    def test_validate_valid(self):
        """Test validation of valid template."""
        template = PersonaTemplate(
            id="test",
            name="Test Template",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )

        errors = template.validate()
        assert len(errors) == 0

    def test_validate_missing_id(self):
        """Test validation catches missing ID."""
        template = PersonaTemplate(
            id="",
            name="Test",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )

        errors = template.validate()
        assert any("ID is required" in e for e in errors)

    def test_validate_missing_name(self):
        """Test validation catches missing name."""
        template = PersonaTemplate(
            id="test",
            name="",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )

        errors = template.validate()
        assert any("name is required" in e for e in errors)

    def test_validate_no_fields(self):
        """Test validation catches no fields."""
        template = PersonaTemplate(
            id="test",
            name="Test",
            fields=[],
        )

        errors = template.validate()
        assert any("at least one field" in e for e in errors)

    def test_validate_duplicate_fields(self):
        """Test validation catches duplicate field names."""
        template = PersonaTemplate(
            id="test",
            name="Test",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
                TemplateField(name="name", label="Name Again"),
            ],
        )

        errors = template.validate()
        assert any("Duplicate" in e for e in errors)

    def test_validate_missing_required_fields(self):
        """Test validation catches missing id/name fields."""
        template = PersonaTemplate(
            id="test",
            name="Test",
            fields=[
                TemplateField(name="other", label="Other"),
            ],
        )

        errors = template.validate()
        assert any("id" in e for e in errors)
        assert any("name" in e for e in errors)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        template = PersonaTemplate(
            id="test",
            name="Test Template",
            category=TemplateCategory.UX,
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )

        data = template.to_dict()

        assert data["id"] == "test"
        assert data["name"] == "Test Template"
        assert data["category"] == "ux"
        assert len(data["fields"]) == 2

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "id": "test",
            "name": "Test Template",
            "category": "marketing",
            "fields": [
                {"name": "id", "label": "ID"},
                {"name": "name", "label": "Name"},
            ],
        }

        template = PersonaTemplate.from_dict(data)

        assert template.id == "test"
        assert template.category == TemplateCategory.MARKETING
        assert len(template.fields) == 2

    def test_to_json(self):
        """Test JSON export."""
        template = PersonaTemplate(
            id="test",
            name="Test",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )

        json_str = template.to_json()
        assert '"id": "test"' in json_str
        assert '"name": "Test"' in json_str

    def test_to_yaml(self):
        """Test YAML export."""
        template = PersonaTemplate(
            id="test",
            name="Test",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )

        yaml_str = template.to_yaml()
        assert "id: test" in yaml_str


class TestTemplateManager:
    """Tests for TemplateManager class."""

    def test_init_loads_system_templates(self):
        """Test initialisation loads system templates."""
        manager = TemplateManager()

        assert "default" in manager.templates
        assert "ux-research" in manager.templates
        assert "marketing" in manager.templates
        assert "academic" in manager.templates
        assert "product" in manager.templates

    def test_list_templates(self):
        """Test listing all templates."""
        manager = TemplateManager()
        templates = manager.list_templates()

        assert len(templates) >= 5
        # Should be sorted by name
        names = [t.name for t in templates]
        assert names == sorted(names)

    def test_list_templates_by_category(self):
        """Test filtering templates by category."""
        manager = TemplateManager()
        ux_templates = manager.list_templates(category=TemplateCategory.UX)

        assert len(ux_templates) >= 1
        assert all(t.category == TemplateCategory.UX for t in ux_templates)

    def test_get_template(self):
        """Test getting a template by ID."""
        manager = TemplateManager()
        template = manager.get_template("ux-research")

        assert template is not None
        assert template.id == "ux-research"
        assert template.is_system is True

    def test_get_template_not_found(self):
        """Test getting non-existent template."""
        manager = TemplateManager()
        template = manager.get_template("nonexistent")

        assert template is None

    def test_get_default_template(self):
        """Test getting default template."""
        manager = TemplateManager()
        template = manager.get_default_template()

        assert template is not None
        assert template.id == "default"

    def test_save_template(self, tmp_path: Path):
        """Test saving a template."""
        manager = TemplateManager(user_templates_dir=tmp_path)

        template = PersonaTemplate(
            id="custom",
            name="Custom Template",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )

        path = manager.save_template(template)

        assert path.exists()
        assert "custom" in manager.templates

    def test_save_template_validation_fails(self, tmp_path: Path):
        """Test saving invalid template fails."""
        manager = TemplateManager(user_templates_dir=tmp_path)

        template = PersonaTemplate(
            id="",  # Invalid: no ID
            name="Test",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )

        with pytest.raises(ValueError, match="validation failed"):
            manager.save_template(template)

    def test_load_template(self, tmp_path: Path):
        """Test loading a template from file."""
        # Create template file
        template_file = tmp_path / "test.yaml"
        template_file.write_text(
            """
id: test-load
name: Test Load Template
fields:
  - name: id
    label: ID
  - name: name
    label: Name
"""
        )

        manager = TemplateManager()
        template = manager.load_template(template_file)

        assert template.id == "test-load"
        assert len(template.fields) == 2

    def test_load_template_not_found(self, tmp_path: Path):
        """Test loading non-existent template."""
        manager = TemplateManager()

        with pytest.raises(FileNotFoundError):
            manager.load_template(tmp_path / "nonexistent.yaml")

    def test_import_template(self, tmp_path: Path):
        """Test importing a template."""
        # Create template file
        template_file = tmp_path / "import.yaml"
        template_file.write_text(
            """
id: imported
name: Imported Template
fields:
  - name: id
    label: ID
  - name: name
    label: Name
"""
        )

        manager = TemplateManager()
        template = manager.import_template(template_file)

        assert template.id == "imported"
        assert "imported" in manager.templates
        assert template.is_system is False

    def test_export_template(self, tmp_path: Path):
        """Test exporting a template."""
        manager = TemplateManager()
        export_path = tmp_path / "export.yaml"

        manager.export_template("ux-research", export_path)

        assert export_path.exists()
        content = export_path.read_text()
        assert "ux-research" in content

    def test_export_template_json(self, tmp_path: Path):
        """Test exporting template as JSON."""
        manager = TemplateManager()
        export_path = tmp_path / "export.json"

        manager.export_template("default", export_path, format="json")

        assert export_path.exists()
        content = export_path.read_text()
        assert '"id": "default"' in content

    def test_export_template_not_found(self, tmp_path: Path):
        """Test exporting non-existent template."""
        manager = TemplateManager()

        with pytest.raises(KeyError):
            manager.export_template("nonexistent", tmp_path / "out.yaml")

    def test_delete_template(self, tmp_path: Path):
        """Test deleting a user template."""
        manager = TemplateManager(user_templates_dir=tmp_path)

        # Create a user template
        template = PersonaTemplate(
            id="deleteme",
            name="Delete Me",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
        )
        manager.save_template(template)

        assert "deleteme" in manager.templates

        result = manager.delete_template("deleteme")

        assert result is True
        assert "deleteme" not in manager.templates

    def test_delete_system_template_fails(self):
        """Test deleting system template fails."""
        manager = TemplateManager()

        with pytest.raises(ValueError, match="Cannot delete system"):
            manager.delete_template("default")

    def test_delete_template_not_found(self):
        """Test deleting non-existent template."""
        manager = TemplateManager()
        result = manager.delete_template("nonexistent")

        assert result is False

    def test_reload_user_templates(self, tmp_path: Path):
        """Test reloading user templates."""
        manager = TemplateManager(user_templates_dir=tmp_path)

        # Create template file directly
        template_file = tmp_path / "reload.yaml"
        template_file.write_text(
            """
id: reloaded
name: Reloaded Template
fields:
  - name: id
    label: ID
  - name: name
    label: Name
"""
        )

        count = manager.reload_user_templates()

        assert count == 1
        assert "reloaded" in manager.templates

    def test_user_templates_override_system(self, tmp_path: Path):
        """Test user templates override system templates."""
        manager = TemplateManager(user_templates_dir=tmp_path)

        # Create user template with same ID as system template
        template = PersonaTemplate(
            id="default",
            name="Custom Default",
            fields=[
                TemplateField(name="id", label="ID"),
                TemplateField(name="name", label="Name"),
            ],
            is_system=False,
        )

        manager._user_templates["default"] = template

        # User version should be returned
        result = manager.get_template("default")
        assert result.name == "Custom Default"

    def test_ux_template_has_expected_fields(self):
        """Test UX template has expected fields."""
        manager = TemplateManager()
        template = manager.get_template("ux-research")

        field_names = [f.name for f in template.fields]
        assert "archetype" in field_names
        assert "mental_model" in field_names
        assert "tech_comfort" in field_names

    def test_marketing_template_has_expected_fields(self):
        """Test marketing template has expected fields."""
        manager = TemplateManager()
        template = manager.get_template("marketing")

        field_names = [f.name for f in template.fields]
        assert "segment" in field_names
        assert "buying_behaviour" in field_names
        assert "media_consumption" in field_names

    def test_academic_template_has_expected_fields(self):
        """Test academic template has expected fields."""
        manager = TemplateManager()
        template = manager.get_template("academic")

        field_names = [f.name for f in template.fields]
        assert "context" in field_names
        assert "motivations" in field_names
        assert "quotes" in field_names

    def test_product_template_has_expected_fields(self):
        """Test product template has expected fields."""
        manager = TemplateManager()
        template = manager.get_template("product")

        field_names = [f.name for f in template.fields]
        assert "use_cases" in field_names
        assert "feature_priorities" in field_names
        assert "success_metrics" in field_names

    def test_system_templates_are_valid(self):
        """Test all system templates pass validation."""
        manager = TemplateManager()

        for template in manager.list_templates():
            errors = template.validate()
            assert len(errors) == 0, f"Template {template.id} has errors: {errors}"
