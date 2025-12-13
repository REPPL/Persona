# R-007: Prompt Templating

## Executive Summary

Jinja2 remains the industry standard for LLM prompt templating, with growing adoption in frameworks like Microsoft Semantic Kernel and PromptFlow. The key insight is that **prompts should be external to code**—stored in files with metadata for versioning and management. The **Banks** library offers a Jinja2-based prompt language with first-class versioning, but for Persona's needs, native Jinja2 with YAML workflow definitions provides sufficient capability with fewer dependencies.

## Current State of the Art (2025)

### Industry Standards

Prompt templating has matured significantly:

1. **Jinja2** - De facto standard, rich syntax, template inheritance
2. **YAML + Jinja2** - Workflow definitions with embedded templates
3. **Prompt Management** - External storage, versioning, metadata

**Key Principle:** Separate prompts from application logic. This enables:
- Non-developers editing prompts
- Version control of prompt evolution
- A/B testing different prompts
- Easier prompt iteration

### Academic Research

No significant academic research specific to prompt templating. Best practices derive from software engineering (separation of concerns) and emerging LLM application patterns.

### Open Source Ecosystem

| Tool | Approach | Features |
|------|----------|----------|
| **Jinja2** | General templating | Filters, inheritance, macros |
| **Banks** | LLM-focused | Metadata, versioning, Jinja2-based |
| **Semantic Kernel** | Microsoft framework | Prompt functions, Jinja2 support |
| **PromptFlow** | Microsoft tooling | Visual editing, Jinja2 templates |
| **LangChain** | Framework | PromptTemplate, ChatPromptTemplate |

## Alternatives Analysis

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Native Jinja2** | Mature, no extra deps, full control | Manual metadata handling | **Recommended** |
| **Banks** | LLM-focused, versioning built-in | Extra dependency, newer | Consider for v0.5.0+ |
| **LangChain PromptTemplate** | Integrated with LangChain | Heavy dependency | Avoid |
| **f-strings** | Simple, native | No inheritance, hard to manage | Avoid |

## Recommendation

### Primary Approach

Use **native Jinja2** with YAML-based prompt definitions:

#### Directory Structure

```
config/prompts/
├── README.md
├── base/
│   └── persona.jinja2           # Base template with common structure
├── workflows/
│   ├── single-step.yaml         # Default single-step workflow
│   └── research-personas.yaml   # Research-focused workflow
└── templates/
    ├── system-prompt.jinja2     # System prompt template
    └── user-prompt.jinja2       # User prompt template
```

#### Workflow Definition

```yaml
# config/prompts/workflows/single-step.yaml
name: single-step
description: Basic single-step persona generation
version: "1.0"

steps:
  - name: generate
    system_template: system-prompt.jinja2
    user_template: user-prompt.jinja2
    variables:
      - user_data      # Required: user research data
      - persona_count  # Required: number of personas
      - detail_level   # Optional: minimal | detailed
```

#### Prompt Templates

```jinja2
{# config/prompts/templates/system-prompt.jinja2 #}
You are a UX researcher with expertise in persona development. Your task is to analyse qualitative user research data and identify distinct user personas.

## Guidelines
- Ground all personas in evidence from the provided data
- Create distinct, non-overlapping personas
- Include direct quotes where available in the data
- Focus on goals, frustrations, and behaviours

{% if detail_level == 'detailed' %}
## Detailed Output Requirements
Include for each persona:
- Demographic details
- Day-in-the-life scenario
- Technology usage patterns
- Decision-making factors
{% endif %}
```

```jinja2
{# config/prompts/templates/user-prompt.jinja2 #}
## Research Data

{{ user_data }}

## Task

Analyse the above research data and identify {{ persona_count }} distinct user personas.

Return your analysis as a JSON array with the following structure for each persona:
{
  "name": "A realistic name",
  "age": "Age or age range",
  "occupation": "Role or job title",
  "goals": ["Goal 1", "Goal 2"],
  "frustrations": ["Frustration 1", "Frustration 2"],
  "quote": "A characteristic statement",
  "evidence": ["Data point 1", "Data point 2"]
}
```

#### Template Engine

```python
# src/persona/core/prompts/engine.py
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import yaml

class PromptEngine:
    def __init__(self, templates_dir: Path):
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def load_workflow(self, workflow_name: str) -> dict:
        """Load workflow definition."""
        workflow_path = self.templates_dir / "workflows" / f"{workflow_name}.yaml"
        with open(workflow_path) as f:
            return yaml.safe_load(f)
    
    def render(self, template_name: str, **variables) -> str:
        """Render a template with variables."""
        template = self.env.get_template(template_name)
        return template.render(**variables)
    
    def render_workflow_step(
        self,
        workflow: dict,
        step_name: str,
        **variables
    ) -> tuple[str, str]:
        """Render system and user prompts for a workflow step."""
        step = next(s for s in workflow["steps"] if s["name"] == step_name)
        
        system_prompt = self.render(step["system_template"], **variables)
        user_prompt = self.render(step["user_template"], **variables)
        
        return system_prompt, user_prompt
```

#### Usage

```python
# In persona generation
engine = PromptEngine(Path("config/prompts/templates"))
workflow = engine.load_workflow("single-step")

system_prompt, user_prompt = engine.render_workflow_step(
    workflow=workflow,
    step_name="generate",
    user_data=loaded_data,
    persona_count=5,
    detail_level="detailed"
)
```

### Best Practices

1. **Keep templates concise** - Avoid complex logic in templates
2. **Use inheritance** - Base templates for common structure
3. **Document variables** - List required/optional variables in workflow YAML
4. **Version workflows** - Include version field for tracking changes
5. **Test templates** - Unit tests for template rendering

### Rationale

1. **Separation of Concerns** - Prompts editable without code changes
2. **Iteration Speed** - Non-developers can modify prompts
3. **Version Control** - Templates tracked alongside code
4. **Flexibility** - Jinja2 supports conditionals, loops, inheritance
5. **No Extra Dependencies** - Jinja2 already required by Persona

## Impact on Existing Decisions

### ADR Updates Required

**ADR-0004 (Jinja2 Templating)** should be updated to:
- Add Banks as alternative considered
- Document workflow definition pattern
- Specify directory structure

### Feature Spec Updates

**F-003 (Prompt Templating)** should specify:
- Template directory structure
- Workflow YAML schema
- PromptEngine API

**F-005 (Reusable Templates)** should specify:
- Template inheritance pattern
- Variable documentation requirements

## Sources

- [Jinja2 Prompting Guide](https://medium.com/@alecgg27895/jinja2-prompting-a-guide-on-using-jinja2-templates-for-prompt-management-in-genai-applications-e36e5c1243cf)
- [Banks Library (GitHub)](https://github.com/masci/banks)
- [Prompt Templates with Jinja2 (PromptLayer)](https://blog.promptlayer.com/prompt-templates-with-jinja2-2/)
- [Microsoft Semantic Kernel Jinja2 Templates](https://learn.microsoft.com/en-us/semantic-kernel/concepts/prompts/jinja2-prompt-templates)
- [Creating Dynamic Prompts with Jinja2](https://datascience.fm/creating-dynamic-prompts-with-jinja2-for-llm-queries/)

---

## Related Documentation

- [ADR-0004: Jinja2 Templating](../decisions/adrs/ADR-0004-jinja2-templating.md)
- [F-003: Prompt Templating](../roadmap/features/planned/F-003-prompt-templating.md)
- [System Design](../planning/architecture/system-design.md)
