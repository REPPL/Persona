# ADR-0001: Hybrid Specification Approach

## Status

Accepted

## Context

Persona is a rewrite of PersonaZero applying lessons from ragd development. We need a specification approach that:
- Links user needs to implementation
- Enables autonomous agent implementation
- Maintains human oversight
- Validates user experience

## Decision

Adopt a three-layer hybrid specification approach:

```
Layer 1: USE CASES (Why)
    ↓ derive
Layer 2: FEATURE SPECS (What)
    ↓ validate
Layer 3: TUTORIALS (How users experience it)
```

**Workflow:**
1. Define Use Case (human)
2. Derive Feature Specs (human + agent)
3. Draft Tutorial (agent)
4. Implement Features (agent)
5. Validate via Tutorial (human)
6. Milestone Review (human)

## Consequences

**Positive:**
- Clear traceability from user needs to implementation
- Tutorials validate user experience
- Features have clear purpose
- Autonomous implementation with human oversight

**Negative:**
- More documentation upfront
- Requires discipline to maintain layers

---

## Related Documentation

- [Use Cases](../../../use-cases/)
- [Features](../../roadmap/features/)
- [Tutorials](../../../tutorials/)
