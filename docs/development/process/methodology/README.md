# Development Methodology

Documentation of the development methodology used for Persona.

## Hybrid Specification Approach

Persona uses a three-layer specification approach (ADR-0001):

```
Layer 1: USE CASES (Why)
    ↓ derive
Layer 2: FEATURE SPECS (What)
    ↓ validate
Layer 3: TUTORIALS (How)
```

## Feature-Centric Roadmap

Features are the primary unit of work. Versions are bundles of features.

- **Features** = discrete pieces of value
- **Milestones** = bundles shipped together

## Testing Alongside Implementation

Tests are written with each feature, not deferred:
- Unit tests for each component
- Integration tests for workflows
- Minimum 80% coverage

## Documentation As You Go

Documentation is written before implementation begins:
- Feature specs define what to build
- Implementation records capture what was built
- Devlogs capture reasoning

---

## Related Documentation

- [Implementation Workflow](../workflow.md)
- [AI Contributions](../../ai-contributions.md)
