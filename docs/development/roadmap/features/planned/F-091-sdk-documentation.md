# F-091: SDK Documentation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-008 |
| **Milestone** | v0.9.0 |
| **Priority** | P1 |
| **Category** | API |

## Problem Statement

The Python SDK and REST API need comprehensive documentation for developers to integrate Persona into their applications effectively.

## Design Approach

- Auto-generate API reference from docstrings
- Write integration guides
- Create example notebooks
- Document error handling
- Provide code snippets for common tasks

### Documentation Structure

```
docs/
├── tutorials/
│   ├── sdk-quickstart.md        # 5-minute quickstart
│   └── api-integration.md       # Full integration guide
├── guides/
│   ├── sdk-patterns.md          # Common SDK patterns
│   ├── async-generation.md      # Async usage guide
│   ├── error-handling.md        # Handling SDK errors
│   └── webhooks-setup.md        # Webhook configuration
├── reference/
│   ├── sdk-api.md               # Auto-generated API docs
│   ├── rest-api.md              # REST endpoint reference
│   └── error-codes.md           # Error code reference
└── examples/
    └── notebooks/
        ├── sdk-basics.ipynb
        ├── batch-generation.ipynb
        └── multi-model.ipynb
```

### API Reference (Auto-Generated)

```markdown
## PersonaGenerator

Generate personas from data sources.

### Methods

#### `generate(config: PersonaConfig) -> GenerationResult`

Generate personas based on configuration.

**Parameters:**
- `config` (PersonaConfig): Generation configuration

**Returns:**
- `GenerationResult`: Generated personas and metadata

**Raises:**
- `ValidationError`: Invalid configuration
- `ProviderError`: LLM API failure
- `BudgetExceededError`: Cost limit exceeded

**Example:**
```python
generator = PersonaGenerator(experiment=exp)
result = generator.generate(PersonaConfig(count=3))
```
```

### Code Examples

```python
# Quick Start Example
from persona import PersonaGenerator, Experiment

# Create experiment
exp = Experiment.create(
    name="quickstart",
    data_sources=["interviews.csv"],
    provider="anthropic",
    model="claude-sonnet-4-5-20250929"
)

# Generate personas
generator = PersonaGenerator(experiment=exp)
result = generator.generate(count=3)

# Export results
result.to_json("output/")
print(f"Generated {len(result.personas)} personas")
```

## Implementation Tasks

- [ ] Write SDK quickstart tutorial
- [ ] Write API integration guide
- [ ] Set up auto-generated API docs
- [ ] Create example notebooks
- [ ] Document all error codes
- [ ] Write async usage guide
- [ ] Write webhook setup guide
- [ ] Add code snippets throughout
- [ ] Review and edit all docs

## Success Criteria

- [ ] Quickstart under 5 minutes
- [ ] API reference complete
- [ ] All errors documented
- [ ] Examples work correctly
- [ ] User feedback positive

## Dependencies

- F-087: Python SDK
- F-088: Async support
- F-089: REST API
- F-090: Webhooks

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [F-087: Python SDK](F-087-python-sdk.md)
- [Documentation Standards](../../../development/README.md)

