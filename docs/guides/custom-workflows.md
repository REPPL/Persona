# Custom Workflows Guide

Create and manage custom workflows for specialised persona generation.

## Overview

Workflows define how Persona generates personas - the steps, templates, models, and settings used. While built-in workflows cover common cases, custom workflows let you:

- Optimise for specific domains (healthcare, education, enterprise)
- Create multi-step generation pipelines
- Use different models for different stages
- Standardise generation across your team

## Built-in Workflows

Persona includes four built-in workflows:

| Workflow | Purpose | Temperature | Max Tokens |
|----------|---------|-------------|------------|
| `default` | Standard generation | 0.7 | 4,096 |
| `research` | Detailed with reasoning | 0.5 | 8,192 |
| `quick` | Fast, minimal output | 0.8 | 2,048 |
| `healthcare` | Healthcare domain | 0.6 | 6,144 |

**List available workflows:**

```bash
persona workflow list
```

**View workflow details:**

```bash
persona workflow show default
persona workflow show research --json
```

---

## Using Workflows

### In Generation Commands

```bash
# Use default workflow
persona generate --from data.csv

# Use specific workflow
persona generate --from data.csv --workflow research

# Use custom workflow
persona generate --from data.csv --workflow my-custom-workflow
```

### In Configuration

```yaml
# persona.yaml
defaults:
  workflow: research
```

---

## Creating Custom Workflows

### Quick Creation

Create a workflow from the command line:

```bash
persona workflow create my-workflow \
  --name "My Custom Workflow" \
  --description "Tailored for product research" \
  --provider anthropic \
  --tags "product,research"
```

This creates `~/.persona/workflows/my-workflow.yaml`.

### Manual Creation

Create a YAML file directly for more control:

```yaml
# ~/.persona/workflows/enterprise-personas.yaml
id: enterprise-personas
name: Enterprise Persona Generation
description: B2B enterprise customer personas with buying committee roles
author: Your Team
version: "1.0.0"
tags:
  - enterprise
  - b2b
  - sales

# Default settings (can be overridden per-step)
provider: anthropic
model: claude-sonnet-4-20250514
temperature: 0.6
max_tokens: 6144

# Generation steps
steps:
  - name: generate
    template: builtin/default
    output: personas

# Default variables available to templates
variables:
  complexity: complex
  detail_level: detailed
  include_reasoning: true
```

---

## Workflow Locations

Workflows are loaded from three locations (in priority order):

| Location | Scope | Path |
|----------|-------|------|
| Project | Current project only | `.persona/workflows/` |
| User | All your projects | `~/.persona/workflows/` |
| Built-in | Everyone | Bundled with Persona |

**Create project-level workflow:**

```bash
persona workflow create team-standard \
  --name "Team Standard" \
  --project
```

This saves to `.persona/workflows/team-standard.yaml` for version control with your project.

---

## Multi-Step Workflows

Chain multiple generation steps for complex pipelines.

### Example: Extract-Consolidate-Validate

```yaml
# ~/.persona/workflows/research-grade.yaml
id: research-grade
name: Research-Grade Pipeline
description: Three-step research methodology
version: "1.0.0"
tags:
  - research
  - academic

provider: anthropic
temperature: 0.5
max_tokens: 8192

steps:
  # Step 1: Extract themes from data
  - name: extract
    template: builtin/extract-themes
    model: claude-sonnet-4-20250514
    output: themes

  # Step 2: Synthesise themes into draft personas
  - name: synthesise
    template: builtin/default
    model: claude-opus-4-20250514
    input: themes  # Uses output from 'extract' step
    output: draft_personas

  # Step 3: Validate and refine
  - name: validate
    template: builtin/validate
    model: claude-sonnet-4-20250514
    input: draft_personas
    output: personas

variables:
  complexity: complex
  detail_level: detailed
  include_reasoning: true
```

### Step Chaining Rules

1. **First step** cannot have an `input` field
2. **Subsequent steps** reference previous `output` names via `input`
3. **Output names** must be unique within the workflow
4. **Final step** output is the workflow result

---

## Per-Step Configuration

Override defaults for specific steps:

```yaml
steps:
  - name: initial-analysis
    template: builtin/default
    provider: openai           # Override provider
    model: gpt-4o              # Override model
    temperature: 0.3           # Lower temperature for analysis
    max_tokens: 4096
    output: analysis
    variables:                 # Step-specific variables
      focus: "pain points"

  - name: persona-synthesis
    template: builtin/default
    provider: anthropic        # Different provider
    model: claude-opus-4-20250514
    temperature: 0.7           # Higher for creativity
    max_tokens: 8192
    input: analysis
    output: personas
```

---

## Domain-Specific Examples

### Healthcare Workflow

```yaml
id: patient-journey
name: Patient Journey Personas
description: Healthcare personas with HIPAA considerations
tags:
  - healthcare
  - patient-experience

provider: anthropic
model: claude-sonnet-4-20250514
temperature: 0.5
max_tokens: 6144

steps:
  - name: generate
    template: builtin/healthcare
    output: personas

variables:
  complexity: complex
  detail_level: detailed
  include_reasoning: true
  focus_areas:
    - treatment_journey
    - care_coordination
    - health_literacy
```

### SaaS Product Workflow

```yaml
id: saas-users
name: SaaS User Personas
description: B2B SaaS user personas with role-based segmentation
tags:
  - saas
  - b2b
  - product

provider: anthropic
temperature: 0.7
max_tokens: 4096

steps:
  - name: generate
    template: builtin/default
    output: personas

variables:
  complexity: moderate
  detail_level: standard
  include_reasoning: false
  segments:
    - admin
    - power_user
    - casual_user
```

### Academic Research Workflow

```yaml
id: academic-study
name: Academic Research Personas
description: Research-grade personas with full provenance
tags:
  - academic
  - research

provider: anthropic
model: claude-opus-4-20250514
temperature: 0.4
max_tokens: 12288

steps:
  - name: generate
    template: builtin/default
    output: personas

variables:
  complexity: complex
  detail_level: detailed
  include_reasoning: true
  citation_style: apa
  evidence_threshold: high
```

---

## Validation

Always validate workflows before use:

```bash
persona workflow validate my-workflow
```

**Common validation errors:**

| Error | Cause | Fix |
|-------|-------|-----|
| Unknown input reference | Step references non-existent output | Check `input` matches previous `output` |
| Invalid template | Template not found | Use `builtin/` prefix or create custom template |
| Invalid ID format | ID contains invalid characters | Use letters, numbers, dots, underscores, hyphens |

---

## Managing Workflows

### List All Workflows

```bash
# All workflows
persona workflow list

# Filter by source
persona workflow list --source user
persona workflow list --source project

# Filter by tag
persona workflow list --tag healthcare
```

### Remove a Workflow

```bash
persona workflow remove my-workflow

# Skip confirmation
persona workflow remove my-workflow --force
```

**Note:** Built-in workflows cannot be removed.

---

## Best Practices

### 1. Start with Built-in, Then Customise

```bash
# See what the research workflow does
persona workflow show research

# Create your own based on it
persona workflow create my-research \
  --name "My Research Workflow" \
  --template builtin/default
```

### 2. Use Project-Level for Team Standards

```bash
# Create in project directory for version control
persona workflow create team-standard \
  --name "Team Standard" \
  --project
```

Commit `.persona/workflows/` to share with your team.

### 3. Tag for Organisation

```yaml
tags:
  - healthcare
  - patient-experience
  - v2
```

Then filter: `persona workflow list --tag healthcare`

### 4. Version Your Workflows

```yaml
id: enterprise-v2
version: "2.0.0"
```

Keep old versions for reproducibility.

### 5. Document with Descriptions

```yaml
description: |
  Enterprise B2B personas optimised for sales enablement.
  Includes buying committee roles and decision criteria.
  Updated for 2025 market research methodology.
```

---

## Troubleshooting

### Workflow Not Found

```
Error: Workflow 'my-workflow' not found.
```

**Check:**
1. Workflow exists: `persona workflow list`
2. Correct location: `~/.persona/workflows/` or `.persona/workflows/`
3. Valid YAML syntax: `persona workflow validate my-workflow`

### Step Chain Error

```
Error: Step 'synthesise' references unknown input 'theme'.
Available outputs: {'themes'}
```

**Fix:** Correct the `input` field to match the exact `output` name from the previous step.

### Template Not Found

```
Error: Template 'custom/my-template' not found.
```

**Fix:** Use `builtin/default` or create the custom template in your prompts directory.

---

## Related Documentation

- [Configuration Reference](../reference/configuration-reference.md)
- [Prompt Templates Reference](../reference/prompt-templates.md)
- [CLI Reference](../reference/cli-reference.md)
- [Persona Generation Guide](persona-generation.md)
