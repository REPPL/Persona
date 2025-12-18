# F-037: Table Output Formats

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-006 |
| **Milestone** | v0.4.0 |
| **Priority** | P1 |
| **Category** | Output |

## Problem Statement

Users need to compare personas side-by-side and integrate persona data into reports, spreadsheets, and academic papers. Current outputs don't support tabular comparison or LaTeX for academic use.

## Design Approach

- Support multiple table formats: ASCII, Markdown, CSV, LaTeX
- Generate comparison tables across personas
- Support attribute-based views (all goals, all pain points, etc.)
- Configurable columns and rows

### Table Formats

| Format | Use Case | Example |
|--------|----------|---------|
| ASCII | Terminal display | `persona show --table` |
| Markdown | Documentation | GitHub, wikis |
| CSV | Spreadsheets | Excel, Google Sheets |
| LaTeX | Academic papers | Journals, conferences |

## Implementation Tasks

- [ ] Create TableFormatter base class
- [ ] Implement ASCIITableFormatter
- [ ] Implement MarkdownTableFormatter
- [ ] Implement CSVTableFormatter
- [ ] Implement LaTeXTableFormatter
- [ ] Add comparison table generation
- [ ] Add `--table-format` CLI option
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All four formats render correctly
- [ ] Comparison tables align personas correctly
- [ ] CSV imports cleanly into Excel
- [ ] LaTeX compiles without errors
- [ ] Test coverage ≥ 80%

## Dependencies

- F-005: Output formatting

---

## Related Documentation

- [Milestone v0.4.0](../../milestones/v0.4.0.md)
- [F-005: Output Formatting](F-005-output-formatting.md)
