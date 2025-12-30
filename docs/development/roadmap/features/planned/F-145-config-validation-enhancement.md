# F-145: Configuration Validation Enhancement

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-145 |
| **Title** | Configuration Validation Enhancement |
| **Priority** | P1 (High) |
| **Category** | Developer Experience |
| **Milestone** | [v1.13.0](../../milestones/v1.13.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-055 (Config Validation) |

---

## Problem Statement

Current configuration validation:
- Shows generic error messages
- Doesn't suggest corrections
- Can't auto-fix common issues
- Doesn't explain why values are invalid

Users struggle to fix configuration problems quickly.

---

## Design Approach

Enhance validation with contextual errors, suggestions, and auto-repair capabilities.

---

## Key Capabilities

### 1. Contextual Error Messages

Provide specific, actionable error messages.

```bash
persona config validate
```

**Before (current):**
```
Error: Invalid configuration
```

**After (enhanced):**
```
Configuration Validation
════════════════════════════════════════════════════════════════

❌ Error at provider.model
   Value: "claude-3-opus"
   Issue: Unknown model identifier
   Valid options: claude-sonnet-4-20250514, claude-opus-4-20250514, gpt-4o, gpt-4o-mini

❌ Error at output.format
   Value: "yaml"
   Issue: 'format' is deprecated since v1.13.0
   Migration: Rename to 'output_format'

⚠️ Warning at cache.ttl
   Value: "1d"
   Issue: String duration not supported, use seconds
   Suggestion: Change to 86400

Found 2 errors, 1 warning
Run 'persona config validate --fix' to auto-repair
```

### 2. Configuration Suggestions

Suggest fixes for common mistakes.

```python
class ConfigSuggester:
    def suggest(self, key: str, value: Any, error: ValidationError) -> Suggestion | None:
        # Typo detection
        if error.type == "unknown_key":
            similar = self.find_similar_keys(key)
            if similar:
                return Suggestion(
                    message=f"Did you mean '{similar}'?",
                    fix=lambda c: self.rename_key(c, key, similar)
                )

        # Type coercion
        if error.type == "wrong_type":
            coerced = self.try_coerce(value, error.expected_type)
            if coerced is not None:
                return Suggestion(
                    message=f"Convert to {error.expected_type.__name__}?",
                    fix=lambda c: self.set_value(c, key, coerced)
                )

        # Deprecated key
        if error.type == "deprecated":
            return Suggestion(
                message=f"Rename to '{error.replacement}'",
                fix=lambda c: self.migrate_key(c, key, error.replacement)
            )

        return None
```

### 3. Auto-Fix Capability

Automatically repair fixable issues.

```bash
# Show what would be fixed
persona config validate --fix --dry-run

# Apply fixes
persona config validate --fix

# Apply fixes with backup
persona config validate --fix --backup
```

**Output:**
```
Auto-Fix Preview
════════════════════════════════════════════════════════════════

The following changes will be made to persona.yaml:

1. Rename 'output.format' → 'output.output_format'
   - output:
   -   format: json
   + output:
   +   output_format: json

2. Convert 'cache.ttl' from "1d" to 86400
   - cache:
   -   ttl: "1d"
   + cache:
   +   ttl: 86400

3. Fix typo 'porvider' → 'provider'
   - porvider:
   + provider:

Apply these changes? [y/N]
```

### 4. Interactive Configuration Repair

Guide users through fixing issues interactively.

```bash
persona config fix --interactive
```

**Output:**
```
Interactive Configuration Repair
════════════════════════════════════════════════════════════════

Issue 1/3: Unknown key 'porvider'

  Current: porvider:
             name: anthropic

  Options:
    [1] Rename to 'provider' (recommended)
    [2] Delete this section
    [3] Keep as-is (will cause error)
    [4] Skip

  Choice: 1

  ✅ Renamed 'porvider' to 'provider'

Issue 2/3: Deprecated key 'output.format'
...
```

### 5. Schema Export

Export configuration schema for IDE support.

```bash
# Export JSON Schema
persona config schema --format json > persona-schema.json

# Export with defaults
persona config schema --include-defaults > persona-schema.json
```

**Usage in editors:**
```yaml
# yaml-language-server: $schema=./persona-schema.json

provider:
  name: anthropic  # IDE provides autocompletion
```

---

## CLI Commands

```bash
# Validation
persona config validate [--fix] [--dry-run] [--backup]

# Interactive repair
persona config fix [--interactive]

# Show resolved configuration
persona config show [--resolved] [--format yaml|json]

# Compare configurations
persona config diff FILE1 FILE2

# Schema export
persona config schema [--format json|yaml] [--include-defaults]

# Reset to defaults
persona config reset [--key KEY]
```

---

## Implementation Tasks

### Phase 1: Enhanced Validation
- [ ] Create detailed error types
- [ ] Add field-level error messages
- [ ] Include valid options in errors
- [ ] Add validation context

### Phase 2: Suggestions
- [ ] Implement typo detection
- [ ] Add type coercion suggestions
- [ ] Create deprecation suggestions
- [ ] Build suggestion engine

### Phase 3: Auto-Fix
- [ ] Create fix registry
- [ ] Implement dry-run mode
- [ ] Add backup functionality
- [ ] Build fix applier

### Phase 4: Interactive Mode
- [ ] Create interactive prompts
- [ ] Add preview display
- [ ] Implement undo capability
- [ ] Add skip/keep options

### Phase 5: Schema Export
- [ ] Generate JSON Schema
- [ ] Add defaults to schema
- [ ] Include descriptions
- [ ] Create editor integration docs

---

## Success Criteria

- [ ] Error messages include specific field and value
- [ ] Suggestions provided for 80%+ of common errors
- [ ] Auto-fix resolves fixable issues correctly
- [ ] Interactive mode guides through all issues
- [ ] Schema enables IDE autocompletion
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
# Meta-configuration for validation
validation:
  strict: false  # Treat warnings as errors
  suggest_fixes: true
  auto_backup: true
  backup_directory: .persona/backups
```

---

## Related Documentation

- [v1.13.0 Milestone](../../milestones/v1.13.0.md)
- [F-055: Config Validation](../completed/F-055-config-validation.md)
- [F-143: Migration Guide Generator](F-143-migration-guide-generator.md)
- [ADR-0006: YAML-Based Configuration](../../../decisions/adrs/ADR-0006-yaml-configuration.md)

---

**Status**: Planned
