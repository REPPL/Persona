# F-049: Edit Experiment Command

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002 |
| **Milestone** | v0.5.0 |
| **Priority** | P2 |
| **Category** | CLI |

## Problem Statement

Users need to modify experiment configurations after creation (change model, adjust parameters, add data sources). Currently requires manual YAML editing.

## Design Approach

- Interactive editing of experiment config
- Support field-specific updates via CLI
- Validate changes before saving
- Maintain edit history
- Support batch updates

### CLI Interface

```bash
# Interactive editor
persona experiment edit my-experiment

# Direct field update
persona experiment edit my-experiment --set generation.model=gpt-5

# Add data source
persona experiment edit my-experiment --add-source ./new-data.csv
```

## Implementation Tasks

- [ ] Create ExperimentEditor class
- [ ] Implement interactive edit mode
- [ ] Add `--set` for direct updates
- [ ] Add `--add-source` and `--remove-source`
- [ ] Validate changes before save
- [ ] Track edit history
- [ ] Support rollback
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Interactive editing works
- [ ] Direct updates work correctly
- [ ] Invalid changes rejected
- [ ] Edit history maintained
- [ ] Test coverage ≥ 80%

## Dependencies

- F-006: Experiment management
- F-012: Experiment configuration

---

## Related Documentation

- [Milestone v0.5.0](../../milestones/v0.5.0.md)
- [CLI Reference](../../../../reference/cli-reference.md)

