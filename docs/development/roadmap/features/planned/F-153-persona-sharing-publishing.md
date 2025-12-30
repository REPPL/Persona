# F-153: Persona Sharing & Publishing

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-153 |
| **Title** | Persona Sharing & Publishing |
| **Priority** | P1 (High) |
| **Category** | Collaboration |
| **Milestone** | [v2.0.0](../../milestones/v2.0.0.md) |
| **Status** | Planned |
| **Dependencies** | F-151 (Team Workspace), F-152 (RBAC) |

---

## Problem Statement

Generated personas have value beyond the generating team:
- Share with external stakeholders (clients, partners)
- Publish to internal design systems
- Distribute to development teams
- Archive for future reference
- Provide to research participants

Currently, sharing requires manual file export and loses provenance information.

---

## Design Approach

Provide multiple sharing mechanisms from private links to public publishing, with provenance preservation and access controls.

---

## Key Capabilities

### 1. Private Sharing Links

Generate secure, expiring links for external access.

```bash
# Create share link
persona share create ./personas/customer-sarah.yaml \
  --expires 7d \
  --access view \
  --password

# Output
Share link created:
  URL: https://persona.app/s/abc123xyz
  Expires: 2025-01-27 14:32 UTC
  Access: View only
  Password: Pr0t3ct3d! (share separately)

# List active shares
persona share list

# Revoke share
persona share revoke abc123xyz
```

### 2. Team Sharing

Share within organisation without external links.

```bash
# Share with another workspace
persona share workspace ./personas/ --to marketing-team

# Share with specific users
persona share user ./personas/customer-sarah.yaml \
  --to alice@company.com,bob@company.com

# View shared with me
persona share inbox
```

### 3. Publishing

Publish personas to accessible locations.

```bash
# Publish to internal registry
persona publish ./personas/ --to registry --collection "Q1 Research"

# Publish to design system
persona publish ./personas/ --to figma --project "Product Design"

# Publish to documentation
persona publish ./personas/ --to docs --format markdown
```

**Registry View:**
```
Persona Registry: company/q1-research
═══════════════════════════════════════════════════════════════════

Collection: Q1 Research
Published: 2025-01-20 by alice@company.com
Personas: 12

  NAME              AGE  OCCUPATION         DOWNLOADS
  ─────────────────────────────────────────────────────
  customer-sarah    32   Product Manager    47
  customer-james    45   Software Engineer  32
  customer-maria    28   UX Designer        28
  ...

Install: persona install company/q1-research
```

### 4. Export Formats

Export in various formats for different consumers.

```bash
# Export for presentation
persona export ./personas/ --format powerpoint --template stakeholder

# Export for design tools
persona export ./personas/ --format figma-json

# Export for development
persona export ./personas/ --format typescript --output src/personas/

# Export for documentation
persona export ./personas/ --format markdown --output docs/personas/
```

**TypeScript Export:**
```typescript
// src/personas/customer-sarah.ts
export const customerSarah: Persona = {
  id: "customer-sarah",
  name: "Sarah Chen",
  demographics: {
    age: 32,
    location: "London",
    occupation: "Product Manager"
  },
  goals: [
    "Save time on daily tasks",
    "Improve team collaboration"
  ],
  // ... full persona
  _metadata: {
    generated: "2025-01-15T10:30:00Z",
    generator: "persona/2.0.0",
    source: "interviews.json",
    lineage: "exp-001/gen-003"
  }
};
```

### 5. Provenance Preservation

Maintain lineage information in shared personas.

```yaml
# Shared persona with provenance
persona:
  name: Sarah Chen
  demographics:
    age: 32
    # ... persona content

_sharing:
  shared_by: alice@company.com
  shared_at: 2025-01-20T14:32:00Z
  share_id: abc123xyz
  permissions: view

_provenance:
  generated_at: 2025-01-15T10:30:00Z
  generator_version: persona/2.0.0
  source_hash: sha256:abc123...
  experiment_id: exp-001
  generation_id: gen-003
  workspace: product-research
```

---

## Implementation Tasks

### Phase 1: Private Sharing

- [ ] Implement share link generation
- [ ] Create share link storage and validation
- [ ] Add password protection option
- [ ] Implement expiry handling
- [ ] Create share viewer interface

### Phase 2: Team Sharing

- [ ] Implement workspace-to-workspace sharing
- [ ] Add user-level sharing
- [ ] Create share inbox functionality
- [ ] Add share notifications
- [ ] Implement share permissions

### Phase 3: Publishing

- [ ] Design registry schema
- [ ] Implement publish workflow
- [ ] Create collection management
- [ ] Add versioning for published personas
- [ ] Implement install/download tracking

### Phase 4: Export Formats

- [ ] Implement PowerPoint export
- [ ] Add Figma JSON export
- [ ] Create TypeScript export
- [ ] Implement Markdown export
- [ ] Add custom template support

---

## CLI Commands

```bash
# Private sharing
persona share create PATH [--expires DURATION] [--access view|download] [--password]
persona share list [--active|--expired]
persona share revoke SHARE_ID
persona share view SHARE_URL

# Team sharing
persona share workspace PATH --to WORKSPACE [--permission view|edit]
persona share user PATH --to EMAIL,EMAIL [--message TEXT]
persona share inbox [--from USER]

# Publishing
persona publish PATH --to registry [--collection NAME] [--visibility public|internal]
persona publish PATH --to figma --project NAME
persona publish PATH --to docs [--format markdown|html]

# Export
persona export PATH --format FORMAT [--output DIR] [--template NAME]

# Installation
persona install REGISTRY/COLLECTION [--version VERSION]
```

---

## Success Criteria

- [ ] Share links work with access controls
- [ ] Team sharing respects RBAC
- [ ] Published personas discoverable
- [ ] Export formats render correctly
- [ ] Provenance preserved in all shares
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
# Sharing configuration
sharing:
  defaults:
    expiry: 7d
    access: view
    require_password: false

  publishing:
    registry_url: https://registry.persona.app
    visibility: internal

  export:
    include_provenance: true
    include_metadata: true

  integrations:
    figma:
      enabled: true
      api_token: ${FIGMA_TOKEN}
    confluence:
      enabled: false
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data leakage via shares | Medium | High | Expiry, password, audit |
| Provenance tampering | Low | Medium | Hash verification |
| Registry availability | Low | Medium | Local caching |
| Export format compatibility | Medium | Low | Validation, versioning |

---

## Related Documentation

- [v2.0.0 Milestone](../../milestones/v2.0.0.md)
- [F-151: Team Workspace Support](F-151-team-workspace-support.md)
- [F-152: Role-Based Access Control](F-152-role-based-access-control.md)
- [F-125: Data Lineage & Provenance](../completed/F-125-data-lineage-provenance.md)
- [R-021: Multi-User Collaboration](../../../research/R-021-multi-user-collaboration.md)

---

**Status**: Planned
