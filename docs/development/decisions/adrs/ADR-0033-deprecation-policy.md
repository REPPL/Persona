# ADR-0033: Deprecation Policy

## Status

Planned

## Context

As Persona evolves, APIs, features, and behaviours will need to change. A clear deprecation policy is needed to:
- Give users time to migrate before breaking changes
- Maintain backwards compatibility where possible
- Communicate changes clearly
- Balance innovation with stability

Without a policy, changes may surprise users or force immediate migration.

## Decision

Adopt a **phased deprecation policy** with minimum notice periods and clear communication.

### Deprecation Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| **Announcement** | Release N | Deprecation warning added |
| **Warning Period** | N to N+2 | Warnings on usage |
| **Removal** | Release N+3 | Feature removed |

Minimum 3 minor versions (~6 months) from announcement to removal.

### Deprecation Markers

```python
import warnings
from functools import wraps

def deprecated(
    version: str,
    removal_version: str,
    alternative: str | None = None
):
    """Mark a function as deprecated."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            msg = f"{fn.__name__} is deprecated since v{version}"
            if alternative:
                msg += f". Use {alternative} instead"
            msg += f". Will be removed in v{removal_version}"
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return fn(*args, **kwargs)
        wrapper.__deprecated__ = {
            "since": version,
            "removal": removal_version,
            "alternative": alternative
        }
        return wrapper
    return decorator

# Usage
@deprecated(
    version="1.12.0",
    removal_version="1.15.0",
    alternative="generate_async()"
)
def generate_sync(data: str) -> Persona:
    """Synchronous generation (deprecated)."""
    return asyncio.run(generate_async(data))
```

### CLI Deprecation

```python
# CLI command deprecation
@app.command(
    deprecated=True,
    help="[DEPRECATED] Use 'persona generate' instead"
)
def gen(data: Path):
    console.print(
        "[yellow]Warning: 'gen' is deprecated. "
        "Use 'persona generate' instead. "
        "Will be removed in v1.15.0.[/yellow]"
    )
    generate(data)
```

### Configuration Deprecation

```yaml
# Old config (deprecated)
llm:
  model: claude-sonnet-4-20250514  # Deprecated, use provider.model

# New config
provider:
  name: anthropic
  model: claude-sonnet-4-20250514
```

```python
class ConfigMigrator:
    def migrate(self, config: dict) -> dict:
        warnings_issued = []

        # Check for deprecated keys
        if "llm" in config:
            warnings_issued.append(
                "Config key 'llm' is deprecated. "
                "Migrate to 'provider' structure. "
                "Will be removed in v1.15.0."
            )
            # Auto-migrate
            config = self._migrate_llm_to_provider(config)

        return config, warnings_issued
```

### Documentation Requirements

Every deprecation MUST include:

1. **Deprecation notice** in docstring/help text
2. **Migration guide** in documentation
3. **Changelog entry** with migration instructions
4. **Warning message** at runtime

### Migration Guide Template

```markdown
## Migrating from `old_feature` to `new_feature`

**Deprecated in:** v1.12.0
**Removed in:** v1.15.0

### Why This Change?
[Explanation of why the change was made]

### Migration Steps

1. Replace `old_feature(x)` with `new_feature(x, param=True)`
2. Update configuration from `old_key` to `new_key`
3. Run tests to verify behaviour

### Example

Before:
```python
result = old_feature(data)
```

After:
```python
result = new_feature(data, param=True)
```

### Compatibility

The old API will continue to work until v1.15.0 with deprecation warnings.
```

### Breaking Change Categories

| Category | Notice Period | Example |
|----------|---------------|---------|
| **API signature change** | 3 versions | Parameter added/removed |
| **Behaviour change** | 2 versions | Different output format |
| **CLI change** | 3 versions | Command renamed |
| **Config change** | 3 versions | Key renamed |
| **Removal** | 3 versions | Feature removed entirely |

### Exceptions

Immediate removal allowed for:
- Security vulnerabilities
- Legal compliance
- Critical bugs where deprecation is unsafe

## Consequences

**Positive:**
- Users have time to migrate
- Clear communication of changes
- Backwards compatibility where feasible
- Predictable upgrade path

**Negative:**
- Slower feature evolution
- Maintenance burden for deprecated code
- Documentation overhead

## Alternatives Considered

### Semantic Versioning Only

**Description:** Breaking changes only in major versions.

**Pros:** Standard, clear.

**Cons:** Major versions may be years apart.

**Why Not Chosen:** Too slow for v1.x development.

### No Deprecation Period

**Description:** Remove immediately in next version.

**Pros:** Clean codebase, fast iteration.

**Cons:** Breaks user code without warning.

**Why Not Chosen:** User trust important.

### Permanent Backwards Compatibility

**Description:** Never remove, only add.

**Pros:** Never breaks anything.

**Cons:** Bloated codebase, confusing API.

**Why Not Chosen:** Need ability to evolve.

---

## Related Documentation

- [ADR-0034: v2.0.0 Breaking Changes Policy](ADR-0034-breaking-changes-policy.md)
- [CHANGELOG](../../../../CHANGELOG.md)

---

**Status**: Planned
