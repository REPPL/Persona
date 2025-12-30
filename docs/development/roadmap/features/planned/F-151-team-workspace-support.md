# F-151: Team Workspace Support

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-151 |
| **Title** | Team Workspace Support |
| **Priority** | P0 (Critical) |
| **Category** | Collaboration |
| **Milestone** | [v2.0.0](../../milestones/v2.0.0.md) |
| **Status** | Planned |
| **Dependencies** | F-124 (Experiment Management), ADR-0036 (Multi-Tenancy) |

---

## Problem Statement

Persona is currently single-user focused. Teams need:
- Shared experiments and persona collections
- Collaborative generation workflows
- Centralised configuration management
- Audit trails for team activity
- Isolation between projects/teams

Without workspaces, teams resort to manual file sharing, losing provenance and collaboration benefits.

---

## Design Approach

Implement project-based multi-tenancy per [ADR-0036](../../decisions/adrs/ADR-0036-multi-tenancy-architecture.md), where workspaces provide logical isolation while sharing infrastructure.

---

## Key Capabilities

### 1. Workspace Management

Create, configure, and manage team workspaces.

```bash
# Create workspace
persona workspace create "Product Research" --description "Q1 2025 user research"

# List workspaces
persona workspace list

# Switch workspace
persona workspace use product-research

# Show current workspace
persona workspace current
```

**Output:**
```
Workspaces
==========

  ACTIVE  NAME              MEMBERS  PERSONAS  CREATED
  ────────────────────────────────────────────────────
  *       product-research  5        47        2025-01-15
          marketing-team    3        23        2025-01-10
          engineering       8        156       2024-12-01

Current: product-research
```

### 2. Workspace Configuration

Workspace-level settings and defaults.

```yaml
# workspace.yaml
workspace:
  name: product-research
  description: Q1 2025 user research

  defaults:
    provider: anthropic
    model: claude-sonnet-4-20250514
    output_format: yaml

  constraints:
    max_personas_per_generation: 10
    allowed_providers: [anthropic, openai]
    require_pii_scan: true

  storage:
    backend: s3
    bucket: company-personas
    prefix: product-research/
```

### 3. Shared Resources

Share experiments, personas, and configurations.

```bash
# Share experiment with workspace
persona experiment share exp-001 --workspace product-research

# Share persona collection
persona share collection ./personas/ --workspace product-research

# View shared resources
persona workspace resources
```

**Shared Resource Types:**
- Experiments (including lineage)
- Persona collections
- Configuration templates
- Schema definitions
- Quality baselines

### 4. Workspace Activity Feed

Track team activity within workspace.

```bash
persona workspace activity --days 7
```

**Output:**
```
Workspace Activity: product-research
════════════════════════════════════════════════════════════════════

2025-01-20 14:32  alice@company.com   Generated 5 personas from interviews.json
2025-01-20 11:15  bob@company.com     Created experiment "January cohort"
2025-01-19 16:45  alice@company.com   Validated 12 personas (all passed)
2025-01-19 09:30  carol@company.com   Shared configuration template "standard"

Showing 4 of 23 activities (--all for complete history)
```

### 5. Workspace Templates

Create workspaces from templates.

```bash
# List templates
persona workspace templates

# Create from template
persona workspace create --template research-project "New Study"
```

**Built-in Templates:**
- `research-project` - Academic research with ethics compliance
- `product-team` - Product development workflow
- `marketing` - Marketing persona generation
- `enterprise` - Full compliance features enabled

---

## Implementation Tasks

### Phase 1: Core Workspace

- [ ] Implement Workspace model and storage
- [ ] Create workspace CLI commands (`create`, `list`, `use`, `current`)
- [ ] Add workspace context to all operations
- [ ] Implement workspace configuration schema
- [ ] Add workspace isolation to data layer

### Phase 2: Sharing

- [ ] Implement resource sharing within workspaces
- [ ] Add experiment sharing functionality
- [ ] Implement persona collection sharing
- [ ] Create configuration template sharing
- [ ] Add shared resource discovery

### Phase 3: Activity & Audit

- [ ] Implement activity tracking
- [ ] Create activity feed display
- [ ] Add activity filtering and search
- [ ] Integrate with audit log system
- [ ] Export activity reports

### Phase 4: Templates

- [ ] Design template schema
- [ ] Create built-in templates
- [ ] Implement template creation from existing workspace
- [ ] Add template marketplace discovery

---

## CLI Commands

```bash
# Workspace management
persona workspace create NAME [--description TEXT] [--template NAME]
persona workspace list [--all]
persona workspace use NAME
persona workspace current
persona workspace delete NAME [--force]
persona workspace archive NAME

# Workspace configuration
persona workspace config show
persona workspace config set KEY VALUE
persona workspace config reset

# Sharing
persona workspace share RESOURCE --with USER
persona workspace unshare RESOURCE --from USER
persona workspace resources [--type TYPE]

# Activity
persona workspace activity [--days N] [--user USER] [--all]
persona workspace activity export --format csv

# Templates
persona workspace templates [--source marketplace|builtin|custom]
persona workspace template create NAME --from WORKSPACE
```

---

## Success Criteria

- [ ] Workspaces provide complete isolation
- [ ] Multi-user access works correctly
- [ ] Activity tracking captures all operations
- [ ] Templates accelerate workspace creation
- [ ] Migration from single-user seamless
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
# Global config with workspace support
persona:
  default_workspace: product-research

workspaces:
  product-research:
    storage:
      backend: s3
      bucket: company-personas

  personal:
    storage:
      backend: local
      path: ~/.persona/workspaces/personal
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data isolation breach | Low | Critical | Strict workspace boundaries, audit |
| Migration complexity | Medium | High | Automated migration, validation |
| Performance degradation | Medium | Medium | Lazy loading, caching |
| UX complexity | Medium | Medium | Sensible defaults, good CLI UX |

---

## Related Documentation

- [v2.0.0 Milestone](../../milestones/v2.0.0.md)
- [F-124: Experiment Management](../completed/F-124-experiment-management.md)
- [R-021: Multi-User Collaboration](../../../research/R-021-multi-user-collaboration.md)
- [ADR-0036: Multi-Tenancy Architecture](../../../decisions/adrs/ADR-0036-multi-tenancy-architecture.md)
- [F-152: Role-Based Access Control](F-152-role-based-access-control.md)

---

**Status**: Planned
