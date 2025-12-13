# ADR-0005: Typer + Rich CLI Framework

## Status

Accepted

## Context

Persona needs a CLI that:
- Is intuitive for non-technical users
- Provides beautiful, informative output
- Supports scripting
- Has excellent developer ergonomics

## Decision

Use Typer for CLI framework and Rich for output:
- Typer: Modern CLI framework with type hints
- Rich: Beautiful terminal formatting
- Combination provides best-in-class UX

## Consequences

**Positive:**
- Excellent user experience
- Type hints for validation
- Automatic --help generation
- Progress bars, tables, panels

**Negative:**
- Two dependencies
- Rich requires compatible terminal

## Alternatives Considered

### Click
**Description:** Mature CLI framework used by Flask, Ansible, and many others.
**Pros:** Very mature, extensive documentation, large community.
**Cons:** More verbose than Typer, no native type hint support.
**Why Not Chosen:** Typer builds on Click with modern Python idioms.

### Cyclopts
**Description:** Newer CLI framework with type hints.
**Pros:** Clean syntax, modern design.
**Cons:** Smaller community, less battle-tested.
**Why Not Chosen:** Typer has larger ecosystem and community support.

### argparse
**Description:** Python standard library argument parser.
**Pros:** No dependencies, standard library.
**Cons:** Verbose, no automatic help from type hints, dated patterns.
**Why Not Chosen:** Poor developer experience compared to modern alternatives.

### Fire
**Description:** Google's CLI auto-generation library.
**Pros:** Minimal code, automatic CLI from functions/classes.
**Cons:** Less control over help text and argument handling.
**Why Not Chosen:** Typer provides better UX customisation.

## Research Reference

See [R-005: CLI Design Patterns](../../research/R-005-cli-design-patterns.md) for comprehensive analysis.

---

## Related Documentation

- [F-008: CLI Interface](../../roadmap/features/planned/F-008-cli-interface.md)
- [PersonaZero Analysis](../../lineage/personazero-analysis.md)
