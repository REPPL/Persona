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
│   ├── api.md                   # Auto-generated API docs
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
generator = PersonaGenerator(provider="anthropic")
result = generator.generate("./data/", PersonaConfig(count=3))
```
```

### Code Examples

```python
# Quick Start Example
from persona import PersonaGenerator, PersonaConfig

# Create generator
generator = PersonaGenerator(
    provider="anthropic",
    model="claude-sonnet-4-5-20250929"
)

# Generate personas
config = PersonaConfig(count=3)
result = generator.generate("./interviews/", config=config)

# Export results
result.to_json("output/")
print(f"Generated {len(result.personas)} personas")
```

## Implementation Tasks

- [x] Write SDK quickstart tutorial
- [x] Set up auto-generated API docs (mkdocstrings)
- [x] Document all error codes
- [x] Write error handling guide
- [x] Write SDK patterns guide
- [x] Add code snippets throughout
- [ ] Create example notebooks (deferred)
- [ ] Write REST API guide (deferred - REST API not yet implemented)
- [ ] Write webhook setup guide (deferred - webhooks not yet implemented)

## Success Criteria

- [x] Quickstart under 5 minutes
- [x] API reference complete
- [x] All errors documented
- [x] Examples work correctly
- [ ] User feedback positive (requires release)

## Dependencies

- F-087: Python SDK (existing)
- F-088: Async support (existing)

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [SDK Quickstart](../../../tutorials/sdk-quickstart.md)
- [SDK Patterns](../../../guides/sdk-patterns.md)
- [Error Handling](../../../guides/error-handling.md)
- [Error Codes Reference](../../../reference/error-codes.md)

---

**Status**: Complete
