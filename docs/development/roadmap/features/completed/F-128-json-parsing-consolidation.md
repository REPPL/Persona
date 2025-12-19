# F-128: JSON Parsing Utility Consolidation

**Milestone:** v1.11.0 - Code Quality & Architecture

**Category:** Refactoring

**Priority:** High

---

## Problem Statement

Three independent implementations of JSON extraction from LLM responses exist across:
- `src/persona/core/generation/parser.py` (lines 180-219)
- `src/persona/core/hybrid/stages/draft.py` (lines 141-216)
- `src/persona/core/hybrid/stages/refine.py` (lines 167-230)

Each implementation handles:
- Markdown code block removal
- JSON array/object parsing
- Partial JSON recovery
- Error fallback behaviour

This duplication creates maintenance burden and inconsistent error handling.

---

## Solution

Create unified `src/persona/core/utils/json_extractor.py`:

```python
class JSONExtractor:
    """Unified JSON extraction from LLM responses."""

    @staticmethod
    def extract_json_from_text(text: str) -> dict[str, Any] | list[Any]:
        """Extract JSON from text with markdown code blocks."""
        ...

    @staticmethod
    def extract_json_array(content: str) -> list[dict[str, Any]]:
        """Extract JSON array with fallback handling."""
        ...

    @staticmethod
    def strip_markdown_code_blocks(text: str) -> str:
        """Remove markdown code block markers."""
        ...
```

---

## Implementation Tasks

- [ ] Create `src/persona/core/utils/__init__.py`
- [ ] Create `src/persona/core/utils/json_extractor.py`
- [ ] Add comprehensive tests in `tests/unit/core/utils/test_json_extractor.py`
- [ ] Refactor `parser.py` to use JSONExtractor
- [ ] Refactor `draft.py` to use JSONExtractor
- [ ] Refactor `refine.py` to use JSONExtractor
- [ ] Verify all existing tests pass

---

## Success Criteria

- [ ] Single source of truth for JSON extraction logic
- [ ] All three modules use the shared utility
- [ ] No regression in existing functionality
- [ ] ~200 lines of code reduction

---

## Dependencies

None

---

## Related Documentation

- [v1.11.0 Milestone](../../milestones/v1.11.0.md)

---

**Status**: Planned
