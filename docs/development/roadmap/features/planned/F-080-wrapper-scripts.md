# F-080: Wrapper Scripts

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001 |
| **Milestone** | v1.0.0 |
| **Priority** | P2 |
| **Category** | Platform |

## Problem Statement

Users need convenient ways to invoke Persona from the command line. Platform-appropriate wrapper scripts simplify invocation.

## Design Approach

- Unix shell script (persona)
- Windows batch script (persona.cmd)
- Windows PowerShell script (persona.ps1)
- Auto-detect Python environment
- Handle virtual environments

### Unix Script (persona)

```bash
#!/usr/bin/env bash
# Persona CLI wrapper

# Find Python interpreter
if [ -n "$VIRTUAL_ENV" ]; then
    PYTHON="$VIRTUAL_ENV/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
else
    PYTHON="python"
fi

# Run Persona
exec "$PYTHON" -m persona "$@"
```

### Windows Batch (persona.cmd)

```batch
@echo off
REM Persona CLI wrapper for Windows

if defined VIRTUAL_ENV (
    set PYTHON=%VIRTUAL_ENV%\Scripts\python.exe
) else (
    set PYTHON=python
)

%PYTHON% -m persona %*
```

### Windows PowerShell (persona.ps1)

```powershell
# Persona CLI wrapper for PowerShell

$Python = if ($env:VIRTUAL_ENV) {
    "$env:VIRTUAL_ENV\Scripts\python.exe"
} else {
    "python"
}

& $Python -m persona $args
```

### Installation Locations

| Platform | Location | Path |
|----------|----------|------|
| Unix | User scripts | `~/.local/bin/persona` |
| Unix | System | `/usr/local/bin/persona` |
| Windows | User | `%USERPROFILE%\AppData\Local\persona` |
| Windows | System | `%ProgramFiles%\persona` |

## Implementation Tasks

- [ ] Create Unix shell script
- [ ] Create Windows batch script
- [ ] Create PowerShell script
- [ ] Add virtual environment detection
- [ ] Create installer for scripts
- [ ] Add to PATH instructions
- [ ] Document installation
- [ ] Test on all platforms

## Success Criteria

- [ ] Scripts work on all platforms
- [ ] Virtual environment detected
- [ ] Clear installation instructions
- [ ] Scripts installed by pip
- [ ] Test coverage ≥ 80%

## Dependencies

- F-079: Platform independence

---

## Related Documentation

- [Milestone v1.0.0](../../milestones/v1.0.0.md)
- [Getting Started](../../../../tutorials/01-getting-started.md)

