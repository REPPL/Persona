# State of the Art: Project Organisation

## Executive Summary

This document analyses best practices for CLI project organisation, comparing registry-based approaches with directory-centric approaches. The analysis informed Persona's v1.7.5 project management system.

---

## Approaches Compared

### 1. Directory-Centric (Traditional)

**Pattern:** Projects are identified by their directory path. Configuration lives within the project.

```bash
cd ~/projects/my-research
tool generate --from ./data/interviews.csv
```

**Pros:**
- Simple mental model
- Self-contained projects
- Easy version control

**Cons:**
- Must navigate to project directory
- No cross-project defaults
- Can't reference projects by name

**Examples:** Most traditional CLI tools (git, npm, cargo)

### 2. Registry-Based (Modern)

**Pattern:** Projects are registered in a central config file with symbolic names.

```bash
# From any directory
tool generate --from my-research
```

**Pros:**
- Reference projects by name from anywhere
- Central configuration for defaults
- Multiple projects easily accessible

**Cons:**
- Additional setup required
- Central point of failure
- Registry can become stale

**Examples:** eval (LLM evaluation tool), conda environments

### 3. Hybrid (Recommended)

**Pattern:** Support both registry lookups and direct paths.

```bash
# Registry lookup
tool generate --from my-research

# Direct path (still works)
tool generate --from ./data/interviews.csv
```

**Pros:**
- Flexibility for different workflows
- Gradual adoption possible
- Best of both approaches

---

## Design Patterns

### Configuration Cascade

Three-level precedence (highest to lowest):
1. **Runtime flags** - Explicit CLI options
2. **Project config** - Per-project settings
3. **Global config** - User defaults

```yaml
# ~/.config/tool/config.yaml (global)
defaults:
  provider: anthropic
  count: 3

# ~/projects/my-research/project.yaml (project)
defaults:
  provider: openai  # Overrides global
  count: 5
```

### XDG Base Directory Specification

Linux standard for config file locations:

| Variable | Default | Purpose |
|----------|---------|---------|
| XDG_CONFIG_HOME | ~/.config | Configuration files |
| XDG_DATA_HOME | ~/.local/share | Data files |
| XDG_CACHE_HOME | ~/.cache | Cache files |
| XDG_STATE_HOME | ~/.local/state | State/logs |

**Cross-platform adaptation:**
- Linux: XDG directories
- macOS: ~/Library/* or ~/.tool
- Windows: %APPDATA%/tool

### Project Templates

Pre-defined directory structures:

**Minimal Template:**
```
project/
├── config.yaml
├── data/
└── output/
```

**Research Template:**
```
project/
├── config.yaml
├── data/
│   ├── raw/
│   └── processed/
├── config/
│   ├── prompts/
│   └── models/
├── output/
│   ├── results/
│   └── exports/
└── templates/
```

### Output Organisation

Hierarchical structure for reproducibility:

```
output/
├── manifest.json          # Index of all runs
└── {data-type}/
    └── {provider}/
        └── {model}/
            └── {session-id}/
                ├── result.json
                └── export.csv
```

---

## Implementation Patterns

### Registry File Format

```yaml
version: "1.0"
defaults:
  provider: anthropic
  model: claude-sonnet-4-20250514
  count: 3
projects:
  my-research: /path/to/my-research
  demo: /path/to/examples/demo
```

### Project Metadata

```yaml
name: my-research
description: "User research study"
created_at: "2025-12-16T00:00:00"
template: research
version: "1.0"

defaults:
  provider: openai
  count: 5

data_sources:
  - name: interviews
    path: data/raw/interviews.csv
    type: qualitative
```

### Reference Resolution

```python
def resolve(reference: str) -> ProjectContext:
    # Check for data source suffix
    if ":" in reference and not reference.startswith("/"):
        reference, source = reference.rsplit(":", 1)

    # Path vs name detection
    if reference.startswith("/") or reference.startswith("./"):
        return resolve_path(reference)
    else:
        return resolve_registry(reference)
```

---

## Recommendations

### For Persona v1.7.5

1. **Implement registry system** with XDG support
2. **Support both paths and names** for flexibility
3. **Provide two templates** (basic and research)
4. **Maintain backwards compatibility** with legacy format

### Future Enhancements

1. **Project sharing** - Export/import project configs
2. **Multi-project operations** - Batch commands
3. **Project discovery** - Auto-detect projects in workspace
4. **Template extensibility** - User-defined templates

---

## Related Documentation

- [v1.7.5 DevLog](../development/process/devlogs/v1.7.5-devlog.md)
- [v1.7.5 Retrospective](../development/process/retrospectives/v1.7.5-retrospective.md)

---

## References

- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- [eval project](https://github.com/example/eval) - Registry implementation reference

---

**Status**: Implemented in v1.7.5
