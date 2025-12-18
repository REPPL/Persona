# F-018: Context-Aware Help

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Cases** | UC-001, UC-002, UC-003 |
| **Milestone** | v0.1.0 |
| **Priority** | P1 |
| **Category** | CLI |

## Problem Statement

Standard `--help` flags show static command documentation. Users benefit from help that adapts to their context: showing relevant examples, detecting common errors, and suggesting next steps based on current state.

## Design Approach

- Enhanced `--help` output with examples
- Error messages include suggested commands
- Detect missing configuration and guide setup
- Show relevant commands based on workflow stage
- Quick-start hints for new users

## Implementation Tasks

- [ ] Enhance Typer help with Rich formatting
- [ ] Add examples section to each command help
- [ ] Implement error suggestion system
- [ ] Detect first-run state and show onboarding
- [ ] Add `persona help <topic>` for detailed guides
- [ ] Create contextual suggestions after operations
- [ ] Write help content tests

## Success Criteria

- [ ] Help shows practical examples
- [ ] Errors suggest corrective actions
- [ ] New users guided through setup
- [ ] Help adapts to user's workflow stage
- [ ] Test coverage ≥ 80%

## Help Enhancements

| Scenario | Behaviour |
|----------|-----------|
| First run | Show quick-start guide |
| Missing API key | Explain how to configure |
| No experiments | Suggest `create experiment` |
| After generation | Show how to view results |
| Unknown command | Suggest similar commands |

## Example Output

```
$ persona generate --from missing/

Error: Data source 'missing/' not found

Did you mean:
  • Create an experiment first: persona create experiment my-project
  • Use an existing experiment: persona list experiments
  • Specify a valid path: persona generate --from ./data/
```

## Dependencies

- F-008: CLI interface (provides framework)
- F-015: CLI core commands (commands to reference)
- F-016: Interactive Rich UI (formatting)

---

## Related Documentation

- [F-008: CLI Interface](F-008-cli-interface.md)
- [F-016: Interactive Rich UI](F-016-interactive-rich-ui.md)
- [Getting Started Tutorial](../../../../tutorials/01-getting-started.md)
