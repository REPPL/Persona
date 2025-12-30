# ADR-0034: v2.0.0 Breaking Changes Policy

## Status

Planned

## Context

Persona v2.0.0 will be a major version allowing breaking changes. A policy is needed to:
- Define what constitutes a breaking change
- Establish migration requirements
- Set communication standards
- Balance innovation with user stability

Major versions are rare opportunities to clean up technical debt and improve APIs.

## Decision

Adopt a **structured breaking changes policy** for v2.0.0 with clear categories, migration support, and communication requirements.

### Breaking Change Categories

| Category | Description | Requirements |
|----------|-------------|--------------|
| **API** | Function signatures, return types | Migration guide, deprecation period |
| **CLI** | Command names, flags, output format | Migration guide, aliases |
| **Config** | Key names, structure, defaults | Auto-migration tool |
| **Behaviour** | Changed semantics, defaults | Documentation, opt-in/out |
| **Removal** | Features, options removed | Deprecation period, alternatives |

### Migration Requirements

Every breaking change MUST include:

1. **Documentation** - Clear explanation of what changed and why
2. **Migration Guide** - Step-by-step upgrade instructions
3. **Tooling** - Automated migration where possible
4. **Testing** - Verification of migration path

### Communication Timeline

```
v1.14.0 (N-3)
└── Announce v2.0.0 timeline
    └── Document planned breaking changes
        └── Deprecate affected features

v1.15.0 (N-2)
└── Release migration tools
    └── Beta documentation
        └── Community feedback period

v1.16.0 (N-1)
└── Final deprecation warnings
    └── Migration dry-run available
        └── Freeze breaking change list

v2.0.0
└── Breaking changes applied
    └── Migration tools updated
        └── Support for v1.x continues (6 months)
```

### Acceptable Breaking Changes

**API Changes:**
- Remove deprecated functions
- Change function signatures (with migration path)
- Modify return types
- Rename modules/classes

**CLI Changes:**
- Rename commands (with aliases for transition)
- Change default behaviours
- Remove deprecated flags
- Modify output formats

**Configuration Changes:**
- Restructure configuration schema
- Change default values
- Remove deprecated keys
- Consolidate overlapping options

**Behaviour Changes:**
- Improve default quality settings
- Change error handling semantics
- Update default providers/models
- Modify output formatting

### Forbidden Breaking Changes

Even in major versions, some changes require extraordinary justification:

- Removing data/lineage without export option
- Breaking persisted experiment format without migration
- Removing plugin system compatibility
- Changing licence terms

### Migration Tool Requirements

```python
class MigrationTool:
    def check(self, project_path: Path) -> MigrationReport:
        """Analyse project for breaking changes."""
        return MigrationReport(
            config_changes=[...],
            code_changes=[...],
            plugin_compatibility=[...],
            estimated_effort="low|medium|high"
        )

    def migrate(
        self,
        project_path: Path,
        dry_run: bool = True,
        backup: bool = True
    ) -> MigrationResult:
        """Apply migrations to project."""
```

**CLI:**
```bash
# Check for breaking changes
persona upgrade check --from v1.16.0 --to v2.0.0

# Apply migrations
persona upgrade migrate --backup

# Verify migration
persona upgrade verify
```

### Version Support Policy

| Version | Support Level | Duration |
|---------|---------------|----------|
| v2.x (current) | Full | Active development |
| v1.x (previous) | Security only | 6 months after v2.0.0 |
| v0.x | None | End of life |

## Consequences

**Positive:**
- Clear expectations for users
- Structured migration path
- Freedom to improve APIs
- Technical debt reduction

**Negative:**
- Migration effort for users
- Parallel version support burden
- Communication overhead

## Alternatives Considered

### No Major Versions

**Description:** Never make breaking changes, only additions.

**Pros:** Maximum stability.

**Cons:** Accumulated technical debt, API bloat.

**Why Not Chosen:** Need ability to evolve.

### Frequent Breaking Changes

**Description:** More frequent major versions (yearly).

**Pros:** Faster evolution.

**Cons:** Migration fatigue, ecosystem fragmentation.

**Why Not Chosen:** Stability important for research tools.

### Feature Flags Only

**Description:** Use flags to enable new behaviour.

**Pros:** No breaking changes.

**Cons:** Complex configuration, technical debt.

**Why Not Chosen:** Eventually need to clean up.

---

## Related Documentation

- [ADR-0033: Deprecation Policy](ADR-0033-deprecation-policy.md)
- [F-143: Migration Guide Generator](../../roadmap/features/planned/F-143-migration-guide-generator.md)
- [CHANGELOG](../../../../CHANGELOG.md)

---

**Status**: Planned
