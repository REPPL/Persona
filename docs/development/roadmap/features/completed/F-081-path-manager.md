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

- [x] Create PathManager class
- [x] Implement platform detection
- [x] Define standard directories
- [x] Add path resolution methods
- [x] Implement safety validation
- [x] Replace ad-hoc path code
- [x] Add environment variable support
- [x] Write unit tests
- [x] Write cross-platform tests

## Success Criteria

- [x] All paths use PathManager
- [x] Works on all platforms
- [x] Standard directories correct
- [x] Path validation prevents traversal
- [x] Test coverage ≥ 90%

## Implementation Note

PathManager is implemented in `src/persona/core/platform.py` and provides:
- `get_config_dir()`, `get_data_dir()`, `get_cache_dir()`, `get_log_dir()`, `get_temp_dir()`
- `PathManager` class with all standard directory properties
- Platform detection (`IS_WINDOWS`, `IS_MACOS`, `IS_LINUX`)
- Path utilities (`normalise_path()`, `ensure_dir()`, `is_executable()`, etc.)

## Dependencies

- F-079: Platform independence

---

## Related Documentation

- [Milestone v1.0.0](../../milestones/v1.0.0.md)
- [Configuration Reference](../../../../reference/configuration-reference.md)

---

**Status**: Complete
