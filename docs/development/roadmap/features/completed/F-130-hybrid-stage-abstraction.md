# F-130: Hybrid Pipeline Stage Abstraction

**Milestone:** v1.11.0 - Code Quality & Architecture

**Category:** Architecture

**Priority:** High

---

## Problem Statement

The hybrid pipeline's three stages (draft, filter, refine) are:
- Hardcoded in the main pipeline method
- Using different APIs and return types
- Tightly coupled to specific implementations
- Cannot be reordered or made optional without modifying pipeline

---

## Solution

Create abstract `PipelineStage` base class:

```python
from abc import ABC, abstractmethod

class PipelineStage(ABC):
    """Abstract base for hybrid pipeline stages."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stage name for logging."""
        ...

    @abstractmethod
    async def execute(
        self,
        input_data: StageInput,
        context: PipelineContext,
    ) -> StageOutput:
        """Execute stage with unified API."""
        ...

class DraftStage(PipelineStage):
    """Generate initial persona drafts."""
    ...

class FilterStage(PipelineStage):
    """Filter personas based on quality threshold."""
    ...

class RefineStage(PipelineStage):
    """Refine personas that need improvement."""
    ...
```

---

## Implementation Tasks

- [ ] Create `src/persona/core/hybrid/stages/base.py` with PipelineStage
- [ ] Define `StageInput` and `StageOutput` dataclasses
- [ ] Define `PipelineContext` for shared state
- [ ] Refactor DraftStage to inherit PipelineStage
- [ ] Refactor FilterStage to inherit PipelineStage
- [ ] Refactor RefineStage to inherit PipelineStage
- [ ] Update HybridPipeline to use stage composition
- [ ] Add stage reordering/skip configuration

---

## Success Criteria

- [ ] All stages implement common interface
- [ ] Stages can be composed in different orders
- [ ] Individual stages can be skipped via configuration
- [ ] No regression in existing functionality

---

## Dependencies

- F-128 (JSON Parsing Consolidation) - stages will use shared JSON extractor

---

## Related Documentation

- [v1.11.0 Milestone](../../milestones/v1.11.0.md)
- [F-116 Hybrid Pipeline](../completed/F-116-hybrid-local-frontier-pipeline.md)

---

**Status**: Planned
