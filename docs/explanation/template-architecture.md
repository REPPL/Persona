# Template-Driven Architecture

Understanding the three-layer template hierarchy that powers persona generation.

## Overview

Persona uses a template-driven architecture where prompts, output formats, and processing logic are all defined in templates. This enables customisation without code changes.

## The Three-Layer Hierarchy

```
┌─────────────────────────────────────────────┐
│         Experiment Overrides                │
│         (One-time modifications)            │
├─────────────────────────────────────────────┤
│         User Templates                      │
│         (Custom, project-specific)          │
├─────────────────────────────────────────────┤
│         System Templates                    │
│         (Built-in, tested, maintained)      │
└─────────────────────────────────────────────┘
```

### Layer 1: System Templates

Built-in templates maintained by the Persona project.

**Location:** `persona/templates/`

**Characteristics:**
- Tested with each release
- Cover common use cases
- Stable and reliable
- Cannot be modified (use overrides instead)

**Included templates:**
- `default` - General-purpose persona generation
- `ux-research` - UX research focus
- `marketing` - Marketing persona emphasis
- `academic` - Academic research format
- `empathy-map` - Boag empathy mapping method

### Layer 2: User Templates

Custom templates for specific projects or organisations.

**Location:** `~/.config/persona/templates/`

**Characteristics:**
- Created by users
- Persist across projects
- Can extend or replace system templates
- Shareable with team

**Example structure:**
```
~/.config/persona/templates/
├── my-company-standard.yaml
├── product-team-format.yaml
└── research-detailed.yaml
```

### Layer 3: Experiment Overrides

One-time modifications for specific experiments.

**Location:** `experiments/<name>/config.yaml`

**Characteristics:**
- Highest priority
- Specific to one experiment
- Temporary adjustments
- Don't affect other experiments

## Template Resolution

When generating personas, Persona resolves templates in order:

```
1. Check experiment config for overrides
2. Check user templates directory
3. Fall back to system templates
4. Merge with defaults
```

## Template Structure

### Prompt Templates

```yaml
# template: my-template.yaml
name: my-custom-template
version: "1.0"
extends: default  # Optional: inherit from another template

prompt:
  system: |
    You are an expert in creating user personas from research data.
    Focus on actionable insights for product development.

  user: |
    Based on the following research data, generate {{ persona_count }}
    distinct user personas.

    ## Research Data
    {{ data }}

    ## Requirements
    - Each persona should be clearly distinct
    - Include demographic information
    - Focus on goals and pain points
    - Provide representative quotes

output:
  format: json
  schema: persona-v1
```

### Output Templates

```yaml
# Output format configuration
output:
  format: json  # or: markdown, html, yaml

  json:
    schema: persona-v1
    pretty: true
    include_metadata: true

  markdown:
    template: |
      # {{ name }}

      ## Demographics
      | Attribute | Value |
      |-----------|-------|
      {% for key, value in demographics.items() %}
      | {{ key }} | {{ value }} |
      {% endfor %}

      ## Goals
      {% for goal in goals %}
      - {{ goal }}
      {% endfor %}
```

## Template Variables

### Available Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ data }}` | Combined input data | Interview transcripts |
| `{{ persona_count }}` | Requested persona count | 3 |
| `{{ experiment_name }}` | Current experiment | "Q4 Research" |
| `{{ provider }}` | LLM provider | "anthropic" |
| `{{ model }}` | Model name | "claude-3-sonnet" |
| `{{ timestamp }}` | Generation time | "2024-12-15T10:30:00Z" |

### Custom Variables

Define custom variables in experiment config:

```yaml
# experiments/my-experiment/config.yaml
template: my-custom-template
variables:
  target_audience: "B2B SaaS users"
  industry: "Financial services"
  focus_areas:
    - security
    - compliance
    - efficiency
```

Use in template:

```yaml
prompt:
  user: |
    Generate personas for {{ target_audience }} in the
    {{ industry }} industry, focusing on:
    {% for area in focus_areas %}
    - {{ area }}
    {% endfor %}
```

## Jinja2 Features

Templates use Jinja2 templating with full feature support:

### Conditionals

```yaml
prompt:
  user: |
    {% if include_demographics %}
    Include detailed demographic information.
    {% endif %}

    {% if evidence_linking %}
    For each attribute, cite the source quote.
    {% endif %}
```

### Loops

```yaml
output:
  markdown:
    template: |
      {% for persona in personas %}
      ## {{ persona.name }}
      {{ persona.description }}

      {% endfor %}
```

### Filters

```yaml
prompt:
  user: |
    Research data ({{ data | length }} characters):
    {{ data | truncate(5000) }}
```

## Creating Custom Templates

### Step 1: Start from Existing

```bash
# Copy system template as starting point
persona template copy default my-custom

# Edit the template
edit ~/.config/persona/templates/my-custom.yaml
```

### Step 2: Modify as Needed

```yaml
# my-custom.yaml
name: my-custom
extends: default  # Inherit base settings

# Override specific parts
prompt:
  system: |
    You are a specialist in creating personas for enterprise software.
    # ... custom instructions
```

### Step 3: Validate

```bash
# Validate template syntax
persona template validate my-custom

# Preview with sample data
persona template preview my-custom --sample
```

### Step 4: Use

```bash
# Use in experiment
persona generate --from my-experiment --template my-custom
```

## Template Composition

Templates can be composed from multiple sources:

```yaml
# Compose from multiple templates
name: composite-template

include:
  - base: default
  - prompts: ux-research
  - output: marketing

# Then override specific parts
prompt:
  user: |
    {{ include.prompts.user }}

    Additional instructions specific to this template...
```

## Sharing Templates

### Export

```bash
# Export template for sharing
persona template export my-custom --output my-template.yaml
```

### Import

```bash
# Import shared template
persona template import shared-template.yaml --name team-standard
```

### Template Registry

For team-wide templates:

```bash
# Configure template registry
persona config set templates.registry "https://templates.example.com"

# List available templates
persona template list --remote

# Install from registry
persona template install company-standard
```

## Best Practices

### Do

- Start with system templates, modify incrementally
- Test templates with sample data before production
- Document custom variables and their purpose
- Version your templates alongside experiments
- Share successful templates with your team

### Don't

- Modify system templates directly (use overrides)
- Create overly complex templates
- Hard-code values that should be variables
- Forget to validate before use

## Troubleshooting

### Template Not Found

```bash
# List available templates
persona template list

# Check template paths
persona config get templates.paths
```

### Variable Not Replaced

```bash
# Debug template rendering
persona template render my-template --debug
```

### Syntax Errors

```bash
# Validate template
persona template validate my-template

# Output:
# Line 15: Unclosed block tag ({% if ...)
```

---

## Related Documentation

- [F-003: Prompt Templating](../development/roadmap/features/planned/F-003-prompt-templating.md)
- [F-023: Persona Templates](../development/roadmap/features/planned/F-023-persona-templates.md)
- [CLI Reference: template commands](../reference/cli-reference.md)

