# F-135: Deprecated asyncio API Migration

**Milestone:** v1.11.0 - Code Quality & Architecture

**Category:** Maintenance

**Priority:** Low

---

## Problem Statement

`asyncio.get_event_loop()` is deprecated in Python 3.10+ and will be removed in Python 3.13.

Affected files:
- `src/persona/core/async_utils.py` (line 134)
- `src/persona/core/providers/base.py` (line 134)

---

## Solution

Replace deprecated calls with modern equivalents:
- `asyncio.get_running_loop()` - when inside async context
- `asyncio.new_event_loop()` - when creating new loop

---

## Implementation Tasks

- [ ] Find all deprecated asyncio calls
- [ ] Replace with modern equivalents
- [ ] Test on Python 3.12+
- [ ] Update minimum Python version documentation if needed

---

## Success Criteria

- [ ] No deprecated asyncio warnings
- [ ] Compatible with Python 3.12+
- [ ] Ready for Python 3.13 when released

---

## Dependencies

- F-132 (Event Loop Standardisation) - related async improvements

---

## Related Documentation

- [v1.11.0 Milestone](../../milestones/v1.11.0.md)
- [Python 3.10 asyncio changes](https://docs.python.org/3/library/asyncio-eventloop.html)

---

**Status**: Planned
