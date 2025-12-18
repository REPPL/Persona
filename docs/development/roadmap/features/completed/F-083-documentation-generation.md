# F-083: Documentation Generation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-008 |
| **Milestone** | v1.0.0 |
| **Priority** | P2 |
| **Category** | Docs |

## Problem Statement

Documentation must stay synchronised with code. Automated generation from docstrings, schemas, and code ensures accuracy and reduces maintenance burden.

## Design Approach

- Generate API reference from docstrings
- Generate CLI reference from Typer
- Generate schema documentation
- Build documentation site
- Integrate with CI/CD

### Documentation Sources

| Source | Output |
|--------|--------|
| Python docstrings | API reference |
| Typer commands | CLI reference |
| Pydantic models | Schema documentation |
| JSON schemas | Configuration reference |
| Markdown files | User guides |

### Generation Tools

```yaml
# pyproject.toml
[project.optional-dependencies]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.24",
    "typer-cli>=0.0.13",
]
```

### MkDocs Configuration

```yaml
# mkdocs.yml
site_name: Persona Documentation
theme:
  name: material
  palette:
    primary: indigo

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            show_root_heading: true

nav:
  - Home: index.md
  - Tutorials: tutorials/
  - Guides: guides/
  - Reference:
    - CLI: reference/cli.md
    - API: reference/api.md
    - Schemas: reference/schemas.md
  - Development: development/
```

### Generation Commands

```bash
# Generate CLI reference
typer persona.cli.main utils docs --output docs/reference/cli.md

# Generate API reference (via mkdocstrings plugin)
mkdocs build

# Serve locally
mkdocs serve
```

## Implementation Tasks

- [x] Set up MkDocs
- [x] Configure mkdocstrings
- [x] Generate CLI reference
- [x] Generate API reference
- [x] Generate schema docs
- [x] Set up GitHub Pages
- [x] Add to CI/CD pipeline
- [x] Write documentation guide
- [x] Test documentation build

## Success Criteria

- [x] All docs auto-generated
- [x] Documentation site builds
- [x] GitHub Pages deployed
- [x] CI checks doc generation
- [x] Docs stay in sync

## Dependencies

- F-087: Python SDK (for API docs)
- F-082: Help system (CLI docs)

---

## Related Documentation

- [Milestone v1.0.0](../../milestones/v1.0.0.md)
- [Documentation Standards](../../../README.md)

---

**Status**: Complete
