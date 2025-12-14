# F-081: Path Manager for Cross-Platform

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-002 |
| **Milestone** | v1.0.0 |
| **Priority** | P1 |
| **Category** | Platform |

## Problem Statement

Path handling is error-prone across platforms. A centralised path manager ensures consistent, correct path operations throughout the codebase.

## Design Approach

- Centralised PathManager class
- Platform-aware path resolution
- Standard directory locations
- Path validation utilities
- Relative path conversion

### PathManager API

```python
from persona.core.paths import PathManager

pm = PathManager()

# Standard directories
pm.config_dir      # ~/.persona or %APPDATA%\persona
pm.cache_dir       # Platform-appropriate cache
pm.experiments_dir # Default experiments location
pm.temp_dir        # Platform-appropriate temp

# Path operations
pm.resolve("~/data/interviews")  # Expand ~ and resolve
pm.relative_to(path, base)       # Make path relative
pm.ensure_dir(path)              # Create if needed
pm.is_safe_path(path)            # Security validation
```

### Standard Directories

```python
@dataclass
class StandardPaths:
    config: Path      # Configuration files
    cache: Path       # Cached data (model lists, etc.)
    data: Path        # Default data directory
    experiments: Path # Experiments root
    logs: Path        # Log files
    temp: Path        # Temporary files
```

### Path Validation

```python
def is_safe_path(self, path: Path, allowed_roots: list[Path]) -> bool:
    """Check path is within allowed directories."""
    resolved = path.resolve()
    return any(
        resolved.is_relative_to(root)
        for root in allowed_roots
    )
```

## Implementation Tasks

- [ ] Create PathManager class
- [ ] Implement platform detection
- [ ] Define standard directories
- [ ] Add path resolution methods
- [ ] Implement safety validation
- [ ] Replace ad-hoc path code
- [ ] Add environment variable support
- [ ] Write unit tests
- [ ] Write cross-platform tests

## Success Criteria

- [ ] All paths use PathManager
- [ ] Works on all platforms
- [ ] Standard directories correct
- [ ] Path validation prevents traversal
- [ ] Test coverage ≥ 90%

## Dependencies

- F-079: Platform independence

---

## Related Documentation

- [Milestone v1.0.0](../../milestones/v1.0.0.md)
- [Configuration Reference](../../../reference/configuration-reference.md)

