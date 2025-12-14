# F-025: Interactive Refinement

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001 |
| **Milestone** | v0.3.0 |
| **Priority** | P2 |
| **Category** | Generation |

## Problem Statement

CHI 2024 research on human-AI collaboration shows iterative refinement improves persona quality. Users may want to adjust generated personas without regenerating from scratch - making them more technical, adjusting demographics, or emphasising certain traits.

## Design Approach

- Conversational refinement interface
- Natural language instructions ("Make more technical")
- Preserve evidence links through refinement
- Track refinement history
- Support undo/redo

## Implementation Tasks

- [ ] Create `persona refine <id>` CLI command
- [ ] Implement conversational refinement loop
- [ ] Build refinement prompt templates
- [ ] Preserve and update evidence links
- [ ] Track refinement history in metadata
- [ ] Add undo functionality (restore previous version)
- [ ] Show diff between versions
- [ ] Support batch refinement instructions
- [ ] Write unit tests

## Success Criteria

- [ ] Natural language refinements work intuitively
- [ ] Evidence links maintained through refinement
- [ ] History enables reverting to any version
- [ ] Refinements accumulate sensibly
- [ ] Clear feedback on what changed
- [ ] Test coverage ≥ 80%

## Dependencies

- F-004: Persona generation
- F-024: Evidence linking
- F-006: Experiment management (versioning)

---

## Related Documentation

- [UC-001: Generate Personas](../../../../use-cases/briefs/UC-001-generate-personas.md)
- [F-004: Persona Generation](F-004-persona-generation.md)
- [F-024: Evidence Linking](F-024-evidence-linking.md)

