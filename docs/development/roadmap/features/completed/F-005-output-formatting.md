# F-005: Output Formatting

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001 |
| **Milestone** | v0.1.0 |
| **Priority** | P0 |
| **Category** | Output |

## Problem Statement

Generated personas need to be saved in structured formats suitable for further use and analysis.

## Design Approach

- Structured output directory
- JSON for programmatic access
- Markdown for human reading
- Metadata file for generation context

## Implementation Tasks

- [ ] Create OutputManager class
- [ ] Implement directory structure creation
- [ ] Add JSON output formatter
- [ ] Add Markdown output formatter
- [ ] Create metadata.json schema
- [ ] Implement timestamped folders
- [ ] Write unit tests

## Success Criteria

- [ ] Output structure matches design
- [ ] JSON valid and parseable
- [ ] Markdown renders correctly
- [ ] Metadata captures all generation context
- [ ] Test coverage ≥ 80%

## Output Structure

```
outputs/YYYYMMDD_HHMMSS/
├── metadata.json       # Generation parameters
├── prompt.json         # Template used
├── files.txt           # Input files processed
├── full_output.txt     # Complete LLM response
└── personas/
    ├── 01/
    │   ├── persona.txt
    │   └── persona.json
    └── 02/
        └── ...
```

---

## Related Documentation

- [UC-001: Generate Personas](../../../../use-cases/briefs/UC-001-generate-personas.md)
- [ADR-0008: Structured JSON Output](../../../decisions/adrs/ADR-0008-structured-json-output.md)
