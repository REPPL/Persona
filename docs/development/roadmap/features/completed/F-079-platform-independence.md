# F-079: Platform Independence

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-008 |
| **Milestone** | v1.0.0 |
| **Priority** | P0 |
| **Category** | Platform |

## Problem Statement

Persona must work reliably on Windows, macOS, and Linux. Platform-specific code creates maintenance burden and excludes users.

## Design Approach

- Use pathlib for all path operations
- Abstract platform differences
- Test on all three platforms
- Document platform-specific notes
- CI/CD for all platforms

### Platform Considerations

| Area | Windows | macOS | Linux |
|------|---------|-------|-------|
| Paths | `\` separator | `/` separator | `/` separator |
| Config | `%APPDATA%\persona` | `~/.persona` | `~/.persona` |
| Temp | `%TEMP%` | `/tmp` | `/tmp` |
| Shell | PowerShell/cmd | zsh/bash | bash |
| Python | py launcher | python3 | python3 |

### Path Handling

```python
from pathlib import Path

def get_config_dir() -> Path:
    """Get platform-appropriate config directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", "~"))
    else:
        base = Path.home()

    return base / ".persona"
```

### Platform Detection

```python
import platform

PLATFORM = platform.system().lower()  # 'windows', 'darwin', 'linux'
IS_WINDOWS = PLATFORM == "windows"
IS_MACOS = PLATFORM == "darwin"
IS_LINUX = PLATFORM == "linux"
```

## Implementation Tasks

- [x] Audit all path operations
- [x] Replace os.path with pathlib
- [x] Abstract config directory location
- [x] Handle line endings correctly
- [x] Test shell command execution
- [x] Set up CI for all platforms
- [x] Document platform differences
- [x] Write platform-specific tests

## Success Criteria

- [x] Works identically on all platforms
- [x] No platform-specific bugs
- [x] CI passes on all platforms
- [x] Documentation notes differences
- [x] Test coverage ≥ 80% per platform

## Dependencies

- None (foundational requirement)

---

## Related Documentation

- [Milestone v1.0.0](../../milestones/v1.0.0.md)
- [Getting Started](../../../../tutorials/01-getting-started.md)

---

**Status**: Complete
