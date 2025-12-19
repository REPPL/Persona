# F-131: TypedDict for Persona Structures

**Milestone:** v1.11.0 - Code Quality & Architecture

**Category:** Type Safety

**Priority:** Medium

---

## Problem Statement

Extensive use of `dict[str, Any]` throughout the codebase:
- 243+ occurrences of `dict[str, Any]`
- Reduces type safety in hybrid pipeline and quality modules
- IDE autocomplete and type checking are ineffective
- Runtime errors not caught at development time

---

## Solution

Create typed dictionaries for persona data:

```python
from typing import TypedDict, NotRequired

class PersonaDict(TypedDict):
    """Typed dictionary for persona data."""
    name: str
    age: NotRequired[int]
    occupation: NotRequired[str]
    background: str
    goals: list[str]
    frustrations: list[str]
    behaviours: list[str]
    motivations: list[str]

class RefinedPersonaDict(PersonaDict):
    """Persona with refinement metadata."""
    refinement_notes: NotRequired[str]
    quality_score: NotRequired[float]
```

---

## Implementation Tasks

- [ ] Create `src/persona/core/types/persona.py`
- [ ] Define PersonaDict with all persona fields
- [ ] Define RefinedPersonaDict for pipeline output
- [ ] Define DraftPersonaDict for intermediate stages
- [ ] Update hybrid stages to use typed dicts
- [ ] Update generation pipeline to use typed dicts
- [ ] Add type checking to CI (mypy strict mode)

---

## Success Criteria

- [ ] Core persona structures use TypedDict
- [ ] mypy passes with stricter type checking
- [ ] IDE autocomplete works for persona fields
- [ ] No regression in existing functionality

---

## Dependencies

None

---

## Related Documentation

- [v1.11.0 Milestone](../../milestones/v1.11.0.md)

---

**Status**: Planned
