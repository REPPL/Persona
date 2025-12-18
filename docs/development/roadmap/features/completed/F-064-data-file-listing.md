# F-064: Data File Listing in Output

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002, UC-007 |
| **Milestone** | v0.7.0 |
| **Priority** | P2 |
| **Category** | Output |

## Problem Statement

Users need to know which data files were used to generate personas. This supports reproducibility, auditing, and understanding data lineage.

## Design Approach

- Record all input files in metadata
- Include file hashes for integrity
- Track file modification dates
- Support data lineage queries
- Include in generated README

### Metadata Structure

```json
{
  "data_sources": {
    "files": [
      {
        "path": "interviews/participant-001.md",
        "size_bytes": 15420,
        "modified": "2025-12-10T14:30:00Z",
        "sha256": "a3f2b1...",
        "format": "markdown",
        "tokens": 3850
      },
      {
        "path": "interviews/participant-002.md",
        "size_bytes": 12890,
        "modified": "2025-12-11T09:15:00Z",
        "sha256": "b4c3d2...",
        "format": "markdown",
        "tokens": 3210
      }
    ],
    "total_files": 2,
    "total_size_bytes": 28310,
    "total_tokens": 7060
  }
}
```

### README Section

```markdown
## Data Sources

This persona set was generated from 2 data files:

| File | Size | Modified | Tokens |
|------|------|----------|--------|
| participant-001.md | 15.4 KB | 2025-12-10 | 3,850 |
| participant-002.md | 12.9 KB | 2025-12-11 | 3,210 |

**Total:** 28.3 KB, 7,060 tokens
```

## Implementation Tasks

- [ ] Create DataSourceTracker class
- [ ] Record file metadata on load
- [ ] Calculate file hashes
- [ ] Count tokens per file
- [ ] Add to output metadata
- [ ] Generate README section
- [ ] Support relative paths
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All source files recorded
- [ ] File hashes calculated
- [ ] Token counts per file
- [ ] README includes data listing
- [ ] Test coverage ≥ 80%

## Dependencies

- F-001: Multi-format data loading
- F-041: Automatic README generation
- F-063: Token count tracking

---

## Related Documentation

- [Milestone v0.7.0](../../milestones/v0.7.0.md)
- [F-041: README Generation](F-041-automatic-readme-generation.md)
