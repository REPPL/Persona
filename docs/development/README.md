# Development Documentation

Developer documentation for the Persona project.

## Documentation Structure

| Section | Purpose | Audience |
|---------|---------|----------|
| [Lineage](lineage/) | PersonaZero analysis and lessons learned | All developers |
| [Planning](planning/) | Vision and architecture | Architects |
| [Roadmap](roadmap/) | Features and milestones | All developers |
| [Implementation](implementation/) | What was built | Maintainers |
| [Process](process/) | How it was built | Contributors |
| [Decisions](decisions/) | Architecture Decision Records | All developers |

## Hybrid Specification Approach

Persona uses a three-layer specification approach:

```
Layer 1: USE CASES (Why)
    ↓ derive
Layer 2: FEATURE SPECS (What)
    ↓ validate
Layer 3: TUTORIALS (How)
```

- **Use Cases** define user intent → [Use Cases](../use-cases/)
- **Feature Specs** define implementation → [Features](roadmap/features/)
- **Tutorials** validate user experience → [Tutorials](../tutorials/)

## Current Status

**Current Version:** v1.6.0 (112 features complete, 5 planned)

See [Roadmap](roadmap/) for complete milestone details.

## AI Transparency

This project operates with full AI transparency. See [AI Contributions](ai-contributions.md) for details.

---

## Related Documentation

- [Documentation Hub](../README.md)
- [Use Cases](../use-cases/)
- [AI Contributions](ai-contributions.md)
