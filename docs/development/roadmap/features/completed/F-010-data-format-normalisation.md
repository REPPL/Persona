# F-010: Data Format Normalisation

## Overview

| Attribute | Value |
|-----------|-------|
| **Milestone** | v0.1.0 |
| **Priority** | P0 |
| **Category** | Data |

## Problem Statement

Different data formats have varying structures and conventions. Before sending to LLMs, all input data must be normalised to a consistent format that maximises LLM comprehension and enables reliable token counting.

## Design Approach

- Convert all formats to unified internal representation
- Preserve semantic meaning during normalisation
- Handle encoding issues gracefully
- Strip irrelevant metadata
- Ensure consistent line endings and whitespace

## Implementation Tasks

- [ ] Define internal normalised format specification
- [ ] Implement CSV to text normalisation
- [ ] Implement JSON flattening/formatting
- [ ] Implement Markdown cleaning
- [ ] Handle character encoding (UTF-8 normalisation)
- [ ] Add whitespace normalisation
- [ ] Preserve meaningful structure (headers, lists)
- [ ] Write unit tests for each format

## Success Criteria

- [ ] All supported formats normalise consistently
- [ ] No data loss during normalisation
- [ ] Encoding issues handled gracefully
- [ ] Normalised output readable by LLMs
- [ ] Test coverage ≥ 80%

## Dependencies

- F-001: Data loading (provides raw data)

---

## Related Documentation

- [F-001: Data Loading](F-001-data-loading.md)
- [F-004: Persona Generation](F-004-persona-generation.md)
