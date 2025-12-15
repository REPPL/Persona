# Fidelity Constraint Examples

This directory contains example constraint YAML files demonstrating how to specify prompt fidelity requirements for different persona types.

## Available Examples

### tech_professional.yaml
Constraints for generating tech industry professional personas.

**Key features:**
- Occupation must include tech keywords (developer, engineer, architect)
- Age range: 25-55
- Professional tone with detailed complexity
- Career-focused goals and professional challenges

**Usage:**
```bash
persona fidelity persona.json --constraints examples/tech_professional.yaml
```

### healthcare_patient.yaml
Constraints for generating healthcare patient personas.

**Key features:**
- Comprehensive required fields including demographics
- Health-related keywords in pain points
- Age range: 18-85
- Empathetic tone with comprehensive detail
- Patient-centred language

**Usage:**
```bash
persona fidelity persona.json --constraints examples/healthcare_patient.yaml
```

### student.yaml
Constraints for generating student personas.

**Key features:**
- Simple required fields
- Academic and career-focused goal themes
- Age range: 16-25
- Casual tone with simple complexity
- Age-appropriate language

**Usage:**
```bash
persona fidelity persona.json --constraints examples/student.yaml
```

## Constraint File Structure

All constraint files follow this structure:

```yaml
name: Descriptive Name
description: What this constraint file is for

constraints:
  structure:
    required_fields: [list of required field names]
    field_types:
      field_name: type  # string, integer, list, dict

  content:
    occupation_keywords: [keywords for occupation field]
    goal_themes: [themes that should appear in goals]
    required_keywords:
      field_name: [keywords that must appear in this field]

  limits:
    age_range: [min, max]
    goal_count: [min, max]
    pain_point_count: [min, max]
    behaviour_count: [min, max]

  style:
    tone: professional|casual|empathetic|technical
    detail_level: simple|detailed|comprehensive
    custom_rules:
      - Custom rule 1
      - Custom rule 2
```

## Creating Custom Constraints

To create your own constraint file:

1. Copy one of the examples as a starting point
2. Modify the structure, content, limits, and style sections
3. Save with a descriptive name
4. Use with the `--constraints` flag

## Validation Rules

### Structure
- **required_fields**: Fields that must be present and non-empty
- **field_types**: Expected data types for specific fields

### Content
- **occupation_keywords**: Keywords that must appear in occupation
- **goal_themes**: Themes that should appear in goals list
- **required_keywords**: Keywords required in specific fields

### Limits
- **age_range**: [min, max] acceptable age
- **goal_count**: [min, max] number of goals
- **pain_point_count**: [min, max] number of pain points
- **behaviour_count**: [min, max] number of behaviours

### Style
- **tone**: Desired tone (professional, casual, empathetic, technical)
- **detail_level**: Complexity (simple, detailed, comprehensive)
- **custom_rules**: Free-form rules evaluated by LLM-as-Judge

## Notes

- All sections are optional - only specify what you need to validate
- Constraint files are validated when loaded
- Invalid YAML or missing required fields will raise errors
- Custom rules require LLM-as-Judge to be enabled
