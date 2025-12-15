# F-059: Folder Processing

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-004 |
| **Milestone** | v0.7.0 |
| **Priority** | P1 |
| **Category** | Data |

## Problem Statement

Users often have interview transcripts or research data organised in folders. Manually specifying each file is tedious and error-prone. Persona should process entire folders automatically.

## Design Approach

- Accept folder paths as data sources
- Recursively discover supported files
- Support glob patterns for filtering
- Maintain file order (alphabetical or by date)
- Report discovered files before processing

### CLI Interface

```bash
# Process entire folder
persona generate --from ./interviews/

# Process with glob pattern
persona generate --from "./interviews/**/*.md"

# Multiple folders
persona generate --from ./round1/ --from ./round2/

# Exclude patterns
persona generate --from ./data/ --exclude "*.draft.md"
```

### File Discovery

```
./interviews/
├── participant-001.md  ✓ Included
├── participant-002.md  ✓ Included
├── notes.txt           ✗ Excluded (wrong type)
└── drafts/
    └── incomplete.md   ✓ Included (recursive)
```

## Implementation Tasks

- [ ] Create FolderScanner class
- [ ] Implement recursive file discovery
- [ ] Add glob pattern support
- [ ] Implement exclude patterns
- [ ] Add file ordering options
- [ ] Create discovery report output
- [ ] Support multiple folder inputs
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Folders processed recursively
- [ ] Glob patterns work correctly
- [ ] Exclude patterns filter files
- [ ] Clear report of discovered files
- [ ] Test coverage ≥ 80%

## Dependencies

- F-001: Multi-format data loading

---

## Related Documentation

- [Milestone v0.7.0](../../milestones/v0.7.0.md)
- [F-001: Data Loading](F-001-data-loading.md)

