# F-152: Role-Based Access Control

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-152 |
| **Title** | Role-Based Access Control |
| **Priority** | P1 (High) |
| **Category** | Security |
| **Milestone** | [v2.0.0](../../milestones/v2.0.0.md) |
| **Status** | Planned |
| **Dependencies** | F-151 (Team Workspace Support) |

---

## Problem Statement

Team workspaces require access control:
- Different permission levels for team members
- Protection of sensitive configurations
- Audit compliance for regulated industries
- Prevent accidental data modification
- Support organisational hierarchies

Without RBAC, all workspace members have equal access, creating security and compliance risks.

---

## Design Approach

Implement role-based access control with four built-in roles and permission inheritance, following the principle of least privilege.

---

## Key Capabilities

### 1. Role Hierarchy

Four built-in roles with progressive permissions.

```
Owner
  │
  ├── Admin
  │     │
  │     └── Member
  │           │
  │           └── Viewer
```

**Permission Matrix:**

| Permission | Owner | Admin | Member | Viewer |
|------------|-------|-------|--------|--------|
| View personas | ✅ | ✅ | ✅ | ✅ |
| Generate personas | ✅ | ✅ | ✅ | ❌ |
| Validate personas | ✅ | ✅ | ✅ | ✅ |
| Delete personas | ✅ | ✅ | ❌ | ❌ |
| Manage experiments | ✅ | ✅ | ✅ | ❌ |
| Configure workspace | ✅ | ✅ | ❌ | ❌ |
| Manage members | ✅ | ✅ | ❌ | ❌ |
| Manage roles | ✅ | ❌ | ❌ | ❌ |
| Delete workspace | ✅ | ❌ | ❌ | ❌ |
| Transfer ownership | ✅ | ❌ | ❌ | ❌ |

### 2. Member Management

Invite, manage, and remove workspace members.

```bash
# Invite member
persona team invite alice@company.com --role member

# List members
persona team list

# Change role
persona team role alice@company.com --set admin

# Remove member
persona team remove alice@company.com
```

**Output:**
```
Team Members: product-research
═══════════════════════════════════════════════════════════════

  USER                    ROLE     JOINED       LAST ACTIVE
  ─────────────────────────────────────────────────────────────
  owner@company.com       Owner    2025-01-01   2025-01-20
  alice@company.com       Admin    2025-01-05   2025-01-20
  bob@company.com         Member   2025-01-10   2025-01-19
  carol@company.com       Viewer   2025-01-15   2025-01-18

Total: 4 members
```

### 3. Permission Checking

Runtime permission verification.

```python
class PermissionChecker:
    def check(
        self,
        user: User,
        workspace: Workspace,
        action: Action
    ) -> PermissionResult:
        role = workspace.get_role(user)
        allowed = self.permissions[role].allows(action)

        return PermissionResult(
            allowed=allowed,
            role=role,
            action=action,
            reason=self._get_reason(role, action)
        )
```

**CLI Feedback:**
```bash
$ persona generate --workspace product-research input.json
Error: Permission denied

You have 'Viewer' role in workspace 'product-research'.
The 'generate' action requires 'Member' role or higher.

Contact a workspace Admin to request role change.
```

### 4. Invitation Flow

Secure invitation workflow with expiry.

```bash
# Generate invitation link
persona team invite --generate-link --role member --expires 7d

# Accept invitation
persona team accept INVITATION_CODE
```

**Invitation Email:**
```
Subject: Invitation to Persona Workspace: product-research

You've been invited to join the 'product-research' workspace
as a Member.

Click to accept: https://persona.app/invite/abc123
Expires: 2025-01-27

---
Invited by: alice@company.com
```

### 5. Audit Trail

Track all permission-related actions.

```bash
persona team audit --days 30
```

**Output:**
```
Permission Audit Log
════════════════════════════════════════════════════════════════════

2025-01-20 14:32  alice@company.com   Changed role: bob → Admin
2025-01-19 11:15  owner@company.com   Invited: carol@company.com (Viewer)
2025-01-18 16:45  alice@company.com   Permission denied: delete workspace
2025-01-17 09:30  owner@company.com   Created workspace

Showing 4 of 15 entries
```

---

## Implementation Tasks

### Phase 1: Core RBAC

- [ ] Define Role enum and Permission model
- [ ] Implement permission matrix
- [ ] Create PermissionChecker service
- [ ] Add permission checks to all operations
- [ ] Implement role assignment storage

### Phase 2: Member Management

- [ ] Create team CLI commands
- [ ] Implement member invitation flow
- [ ] Add invitation code generation
- [ ] Implement role change workflow
- [ ] Add member removal with cleanup

### Phase 3: Invitation System

- [ ] Design invitation schema
- [ ] Implement invitation generation
- [ ] Add expiry handling
- [ ] Create invitation acceptance flow
- [ ] Integrate with notification system

### Phase 4: Audit & Compliance

- [ ] Implement permission audit logging
- [ ] Create audit report generation
- [ ] Add compliance export formats
- [ ] Integrate with existing audit trail
- [ ] Add permission change notifications

---

## CLI Commands

```bash
# Team management
persona team list [--workspace NAME]
persona team invite EMAIL [--role ROLE] [--message TEXT]
persona team invite --generate-link [--role ROLE] [--expires DURATION]
persona team accept CODE
persona team remove EMAIL [--force]

# Role management
persona team role EMAIL --set ROLE
persona team role EMAIL --show
persona team permissions [--role ROLE]

# Audit
persona team audit [--days N] [--user EMAIL]
persona team audit export --format csv|json
```

---

## Success Criteria

- [ ] Four roles with correct permission inheritance
- [ ] Permission checks on all sensitive operations
- [ ] Invitation flow works end-to-end
- [ ] Audit trail captures all permission changes
- [ ] Clear error messages for permission denials
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
# Workspace RBAC configuration
workspace:
  name: product-research

  roles:
    # Default role for new members
    default: member

    # Custom role (future)
    # custom_roles:
    #   - name: reviewer
    #     inherits: viewer
    #     additional: [validate]

  invitations:
    default_expiry: 7d
    require_approval: false  # Admin approval for invitations

  security:
    require_mfa: false  # Future: MFA requirement
    session_timeout: 24h
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Permission bypass | Low | Critical | Comprehensive testing, code review |
| Role confusion | Medium | Medium | Clear documentation, UI feedback |
| Invitation abuse | Low | Medium | Expiry, rate limiting |
| Audit log tampering | Low | High | Immutable log storage |

---

## Related Documentation

- [v2.0.0 Milestone](../../milestones/v2.0.0.md)
- [F-151: Team Workspace Support](F-151-team-workspace-support.md)
- [R-021: Multi-User Collaboration](../../../research/R-021-multi-user-collaboration.md)
- [ADR-0036: Multi-Tenancy Architecture](../../../decisions/adrs/ADR-0036-multi-tenancy-architecture.md)
- [F-123: Generation Audit Trail](../completed/F-123-generation-audit-trail.md)

---

**Status**: Planned
