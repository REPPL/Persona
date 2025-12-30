# F-143: Migration Guide Generator

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-143 |
| **Title** | Migration Guide Generator |
| **Priority** | P1 (High) |
| **Category** | Developer Experience |
| **Milestone** | [v1.13.0](../../milestones/v1.13.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | None |

---

## Problem Statement

When upgrading between Persona versions, users need to:
- Identify what changed between versions
- Understand if changes affect their usage
- Know how to migrate their code/configuration
- Track deprecation timelines

Currently, this requires manual changelog review and guesswork.

---

## Design Approach

Automatically generate migration guides by analysing API and configuration differences between versions.

---

## Key Capabilities

### 1. Migration Guide Generation

Generate comprehensive migration documentation.

```bash
# Generate migration guide
persona migrate guide --from v1.12.0 --to v1.13.0

# Output to file
persona migrate guide --from v1.12.0 --to v1.13.0 --output MIGRATION.md
```

**Output:**
```markdown
# Migration Guide: v1.12.0 → v1.13.0

## Breaking Changes

### API Changes

#### `generate()` function signature changed

**Before (v1.12.0):**
```python
def generate(data: str, count: int = 1) -> list[Persona]:
```

**After (v1.13.0):**
```python
def generate(data: str, count: int = 1, cache: bool = True) -> list[Persona]:
```

**Migration:** Add `cache=False` if you need to disable caching.

### Configuration Changes

#### `llm.model` moved to `provider.model`

**Before:**
```yaml
llm:
  model: claude-sonnet-4-20250514
```

**After:**
```yaml
provider:
  model: claude-sonnet-4-20250514
```

**Migration:** Run `persona migrate run` to auto-update configuration.

## Deprecations

| Item | Deprecated In | Removed In | Alternative |
|------|---------------|------------|-------------|
| `gen` command | v1.12.0 | v1.15.0 | `persona generate` |
| `--format` flag | v1.13.0 | v1.16.0 | `--output-format` |

## New Features

- Response caching layer (F-142)
- Plugin development CLI (F-141)
- Migration guide generator (this feature!)
```

### 2. Migration Check

Check if migration is needed and what would change.

```bash
# Check for migration needs
persona migrate check

# Check against specific version
persona migrate check --to v1.14.0
```

**Output:**
```
Migration Check: v1.12.0 → v1.13.0
══════════════════════════════════════════════════════════════

Configuration
─────────────
⚠️ 2 deprecated keys found:
   - llm.model → provider.model
   - output.format → output.output_format

Code (if using API)
───────────────────
⚠️ 1 signature change detected
   - generate() has new parameter: cache

Plugins
───────
✅ All plugins compatible

Recommendation: Run 'persona migrate run' to apply changes
```

### 3. Automatic Migration

Apply migrations automatically where safe.

```bash
# Run migration (dry run)
persona migrate run --dry-run

# Apply migration
persona migrate run

# Apply with backup
persona migrate run --backup
```

**Output:**
```
Applying Migration: v1.12.0 → v1.13.0
══════════════════════════════════════════════════════════════

Configuration Changes
─────────────────────
✅ Updated persona.yaml:
   - llm.model → provider.model
   - output.format → output.output_format

Backup created: .persona/backups/config-v1.12.0.yaml

Code Changes (manual required)
──────────────────────────────
⚠️ The following changes require manual update:
   - generate() calls may need cache parameter

Migration complete!
```

### 4. Deprecation Tracking

Track deprecation timelines across versions.

```bash
# List deprecations
persona migrate deprecations

# List deprecations affecting specific version
persona migrate deprecations --target v1.15.0
```

**Output:**
```
Active Deprecations
═══════════════════════════════════════════════════════════════

Scheduled for Removal in v1.15.0
────────────────────────────────
│ Item              │ Type    │ Deprecated │ Alternative        │
├───────────────────┼─────────┼────────────┼────────────────────┤
│ gen command       │ CLI     │ v1.12.0    │ persona generate   │
│ --verbose flag    │ CLI     │ v1.13.0    │ --log-level debug  │

Scheduled for Removal in v1.16.0
────────────────────────────────
│ Item              │ Type    │ Deprecated │ Alternative        │
├───────────────────┼─────────┼────────────┼────────────────────┤
│ --format flag     │ CLI     │ v1.13.0    │ --output-format    │
│ llm config key    │ Config  │ v1.13.0    │ provider           │
```

---

## CLI Commands

```bash
# Guide generation
persona migrate guide --from VERSION --to VERSION [--output FILE]

# Migration check
persona migrate check [--to VERSION]

# Apply migration
persona migrate run [--dry-run] [--backup]

# Deprecation tracking
persona migrate deprecations [--target VERSION]

# Version history
persona migrate history
```

---

## Implementation Tasks

### Phase 1: API Analysis
- [ ] Create API signature extractor
- [ ] Build version comparison engine
- [ ] Detect parameter changes
- [ ] Detect return type changes

### Phase 2: Configuration Analysis
- [ ] Create config schema differ
- [ ] Detect key renames
- [ ] Detect value type changes
- [ ] Build migration rules

### Phase 3: Guide Generation
- [ ] Create markdown template
- [ ] Implement breaking change formatter
- [ ] Implement deprecation formatter
- [ ] Add code examples

### Phase 4: Automatic Migration
- [ ] Implement config migrator
- [ ] Add backup functionality
- [ ] Create dry-run mode
- [ ] Add rollback support

### Phase 5: Deprecation Tracking
- [ ] Create deprecation registry
- [ ] Build timeline calculator
- [ ] Add version targeting
- [ ] Integrate with CLI warnings

---

## Success Criteria

- [ ] Migration guides accurately document breaking changes
- [ ] Config migration auto-updates valid configurations
- [ ] Deprecation timeline is accurate
- [ ] Backup/rollback works correctly
- [ ] Dry-run shows what would change
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
migration:
  auto_check: true  # Check on startup
  backup_on_migrate: true
  backup_directory: .persona/backups
```

---

## Related Documentation

- [v1.13.0 Milestone](../../milestones/v1.13.0.md)
- [ADR-0033: Deprecation Policy](../../../decisions/adrs/ADR-0033-deprecation-policy.md)
- [CHANGELOG](../../../../../CHANGELOG.md)

---

**Status**: Planned
