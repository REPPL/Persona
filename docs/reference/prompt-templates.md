# Prompt Templates Reference

Technical specifications for Jinja2-based prompt templating in Persona.

## Overview

Persona uses Jinja2 templates for all LLM prompts, enabling customisation, versioning, and separation of prompts from application logic. Templates are stored as external files with YAML workflow definitions.

---

## Directory Structure

```
config/prompts/
├── README.md                    # Prompts documentation
├── base/
│   └── persona.jinja2           # Base template with inheritance
├── workflows/
│   ├── single-step.yaml         # Default workflow
│   ├── research-personas.yaml   # Research-focused workflow
│   └── evaluation.yaml          # Evaluation workflow
└── templates/
    ├── system-prompt.jinja2     # System prompt template
    ├── user-prompt.jinja2       # User prompt template
    └── evaluation/
        ├── bias-check.jinja2    # Bias evaluation prompt
        └── fidelity-check.jinja2 # Fidelity evaluation prompt
```

---

## Workflow Definition

Workflows define the sequence of LLM calls with their associated templates.

### Schema

```yaml
# Workflow YAML schema
name: string                    # Workflow identifier
description: string             # Human-readable description
version: string                 # Semantic version

steps:
  - name: string                # Step identifier
    system_template: string     # Path to system prompt template
    user_template: string       # Path to user prompt template
    variables:                  # Required and optional variables
      - name: string
        required: boolean
        default: any
    output:                     # Output configuration
      format: json | text
      schema: string            # JSON schema path (if format: json)
```

### Example Workflow

```yaml
# config/prompts/workflows/single-step.yaml
name: single-step
description: Basic single-step persona generation
version: "1.0"

steps:
  - name: generate
    system_template: templates/system-prompt.jinja2
    user_template: templates/user-prompt.jinja2
    variables:
      - name: user_data
        required: true
        description: User research data to analyse
      - name: persona_count
        required: true
        default: 3
        description: Number of personas to generate
      - name: detail_level
        required: false
        default: detailed
        description: Output detail level (minimal | detailed)
    output:
      format: json
      schema: schemas/persona-output.json
```

---

## Template Syntax

### Basic Variables

```jinja2
{# Simple variable substitution #}
Generate {{ persona_count }} distinct personas.

{# With default value #}
{{ detail_level | default('detailed') }}

{# Conditional content #}
{% if detail_level == 'detailed' %}
Include demographic details, goals, and frustrations.
{% endif %}
```

### Available Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `default` | Provide fallback value | `{{ var \| default('value') }}` |
| `upper` | Uppercase text | `{{ name \| upper }}` |
| `lower` | Lowercase text | `{{ name \| lower }}` |
| `title` | Title case | `{{ name \| title }}` |
| `trim` | Remove whitespace | `{{ text \| trim }}` |
| `truncate` | Limit length | `{{ text \| truncate(100) }}` |
| `wordcount` | Count words | `{{ text \| wordcount }}` |
| `indent` | Add indentation | `{{ text \| indent(4) }}` |

### Custom Persona Filters

```jinja2
{# Format data as bullet points #}
{{ data | to_bullets }}

{# Extract quotes from interview data #}
{{ data | extract_quotes }}

{# Summarise long text #}
{{ data | summarise(max_words=200) }}

{# Format as markdown table #}
{{ data | to_table }}
```

### Template Inheritance

```jinja2
{# base/persona.jinja2 - Base template #}
You are a UX researcher with expertise in persona development.

{% block guidelines %}
## Guidelines
- Ground all personas in evidence
- Create distinct, non-overlapping personas
{% endblock %}

{% block output_requirements %}
## Output Requirements
{% endblock %}

{% block constraints %}
{% endblock %}
```

```jinja2
{# templates/detailed-prompt.jinja2 - Extends base #}
{% extends "base/persona.jinja2" %}

{% block output_requirements %}
{{ super() }}
Include for each persona:
- Demographic details
- Professional background
- Goals and motivations
- Pain points and frustrations
- Behavioural patterns
{% endblock %}
```

---

## Built-in Variables

### System Variables

| Variable | Type | Description |
|----------|------|-------------|
| `_model` | `str` | Current LLM model name |
| `_provider` | `str` | Current provider (openai, anthropic, etc.) |
| `_timestamp` | `datetime` | Generation timestamp |
| `_version` | `str` | Persona version |

### Data Variables

| Variable | Type | Description |
|----------|------|-------------|
| `user_data` | `str` | Raw input data |
| `data_format` | `str` | Input format (csv, json, md) |
| `data_summary` | `str` | Auto-generated data summary |
| `record_count` | `int` | Number of input records |

### Configuration Variables

| Variable | Type | Description |
|----------|------|-------------|
| `persona_count` | `int` | Number of personas to generate |
| `detail_level` | `str` | Output detail (minimal, detailed) |
| `complexity_level` | `str` | Persona complexity (simple, standard, complex) |
| `output_format` | `str` | Output format (json, markdown, narrative) |

---

## Constraint DSL

For prompt fidelity scoring, constraints can be defined using a YAML-based DSL.

### Schema

```yaml
# Constraint definition schema
constraints:
  - id: string                  # Unique constraint identifier
    type: string                # Constraint type (see below)
    target: string              # JSONPath to target field
    condition: any              # Type-specific condition
    severity: error | warning   # Violation severity
    message: string             # Human-readable error message
```

### Constraint Types

#### `required`
Field must be present and non-empty.

```yaml
- id: name-required
  type: required
  target: $.personas[*].name
  severity: error
  message: Persona name is required
```

#### `length`
Text length constraints.

```yaml
- id: bio-length
  type: length
  target: $.personas[*].bio
  condition:
    min: 50
    max: 500
  severity: warning
  message: Bio should be 50-500 characters
```

#### `count`
Array length constraints.

```yaml
- id: goal-count
  type: count
  target: $.personas[*].goals
  condition:
    min: 2
    max: 5
  severity: error
  message: Each persona must have 2-5 goals
```

#### `pattern`
Regex pattern matching.

```yaml
- id: quote-format
  type: pattern
  target: $.personas[*].quotes[*]
  condition: '^".*"$'
  severity: warning
  message: Quotes should be wrapped in quotation marks
```

#### `enum`
Value from allowed set.

```yaml
- id: valid-role
  type: enum
  target: $.personas[*].role_type
  condition:
    - primary
    - secondary
    - edge_case
  severity: error
  message: Role type must be primary, secondary, or edge_case
```

#### `numeric`
Numeric range constraints.

```yaml
- id: age-range
  type: numeric
  target: $.personas[*].demographics.age
  condition:
    min: 18
    max: 99
  severity: warning
  message: Age should be between 18 and 99
```

### Complete Constraint File

```yaml
# config/constraints/persona-output.yaml
version: "1.0"
description: Standard persona output constraints

constraints:
  # Required fields
  - id: name-required
    type: required
    target: $.personas[*].name
    severity: error
    message: Persona name is required

  - id: bio-required
    type: required
    target: $.personas[*].bio
    severity: error
    message: Persona bio is required

  # Structural constraints
  - id: persona-count
    type: count
    target: $.personas
    condition:
      min: 1
      max: 10
    severity: error
    message: Must generate 1-10 personas

  - id: goals-present
    type: count
    target: $.personas[*].goals
    condition:
      min: 2
      max: 5
    severity: warning
    message: Each persona should have 2-5 goals

  # Content constraints
  - id: bio-length
    type: length
    target: $.personas[*].bio
    condition:
      min: 100
      max: 1000
    severity: warning
    message: Bio should be 100-1000 characters

  - id: evidence-present
    type: required
    target: $.personas[*].evidence
    severity: error
    message: Personas must include source evidence
```

---

## Fidelity Scoring

### API Usage

```python
from persona.core.quality import FidelityScorer

scorer = FidelityScorer(
    constraints_file="config/constraints/persona-output.yaml"
)

result = scorer.score(
    output=generated_personas,
    prompt_template="templates/user-prompt.jinja2",
    variables={"persona_count": 3}
)

# Returns:
# {
#     "score": 0.85,
#     "violations": [
#         {
#             "constraint_id": "bio-length",
#             "target": "$.personas[0].bio",
#             "severity": "warning",
#             "message": "Bio should be 100-1000 characters",
#             "actual": 87
#         }
#     ],
#     "passed": 12,
#     "failed": 2,
#     "warnings": 1
# }
```

### CLI Usage

```bash
# Check fidelity against constraints
persona fidelity check output/personas.json \
  --constraints config/constraints/persona-output.yaml

# Generate fidelity report
persona fidelity report output/personas.json --format markdown

# Check during generation
persona generate --from data.csv \
  --check-fidelity \
  --constraints config/constraints/persona-output.yaml
```

---

## Template Management

### Listing Templates

```bash
# List all available templates
persona templates list

# Show template details
persona templates show templates/system-prompt.jinja2

# Validate template syntax
persona templates validate templates/*.jinja2
```

### Creating Custom Templates

```bash
# Create from built-in template
persona templates copy system-prompt custom/my-system.jinja2

# Create blank template
persona templates create custom/my-template.jinja2
```

### Template Validation

```python
from persona.core.prompts import TemplateValidator

validator = TemplateValidator()
result = validator.validate("templates/my-prompt.jinja2")

# Returns:
# {
#     "valid": True,
#     "errors": [],
#     "warnings": [
#         "Variable 'foo' is defined but never used"
#     ],
#     "variables": ["user_data", "persona_count"],
#     "extends": "base/persona.jinja2"
# }
```

---

## Configuration

### Default Configuration

```yaml
# persona.yaml
prompts:
  directory: config/prompts
  default_workflow: single-step

  validation:
    strict: true
    allow_undefined: false

  caching:
    enabled: true
    ttl: 3600  # seconds

  constraints:
    directory: config/constraints
    default: persona-output.yaml
```

---

## Related Documentation

- [Prompt Templating Research](../development/research/R-007-prompt-templating.md)
- [Prompt Fidelity Feature](../development/roadmap/features/planned/F-122-prompt-fidelity-scoring.md)
- [Configuration Reference](configuration-reference.md)

---

**Status**: Reference document for existing and planned features
