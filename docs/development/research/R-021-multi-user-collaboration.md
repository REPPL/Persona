# R-021: Multi-User & Team Collaboration

Research into multi-user architectures, team collaboration patterns, and enterprise features for Persona.

## Executive Summary

This document evaluates approaches for transforming Persona from a single-user CLI tool into a collaborative platform supporting teams and organisations.

**Key Finding:** Team collaboration requires foundational infrastructure changes: centralised storage, user identity, and access control. These should be implemented incrementally, starting with project sharing before full multi-tenancy.

**Recommendation:** Implement a **project-based collaboration model** for v2.0.0 with optional cloud storage backends, progressing to full **multi-tenancy with RBAC** in v2.1.0.

---

## Context

### Current Architecture (Single-User)

Persona v1.11.0 is designed for single-user workflows:

| Aspect | Current State | Collaboration Need |
|--------|---------------|-------------------|
| **Storage** | Local filesystem | Shared/cloud storage |
| **Identity** | None (OS user) | User authentication |
| **Access** | Full access | Role-based permissions |
| **Projects** | Local registry | Team registries |
| **Experiments** | User-owned | Shared ownership |
| **Personas** | Local output | Shareable artefacts |

### Requirements for Collaboration

| Requirement | Priority | Rationale |
|-------------|----------|-----------|
| Share experiments with teammates | P0 | Core collaboration need |
| Control who can view/edit | P0 | Data governance |
| Audit who did what | P0 | Compliance |
| Support multiple organisations | P1 | Enterprise multi-tenancy |
| Real-time collaboration | P2 | Simultaneous editing |
| Comments and annotations | P2 | Team communication |

---

## Collaboration Models

### Model 1: Project-Based Sharing (Recommended for v2.0.0)

**Concept:** Projects are the unit of sharing; users share entire projects with collaborators.

```
Organisation
├── Project A (owned by User 1)
│   ├── Collaborators: User 2 (editor), User 3 (viewer)
│   ├── Experiments
│   │   ├── Experiment 1
│   │   └── Experiment 2
│   └── Output Personas
└── Project B (owned by User 2)
    └── ...
```

**Pros:**
- Simple mental model
- Clear ownership
- Matches existing project structure
- Incremental adoption (start with local, add sharing)

**Cons:**
- No fine-grained sharing (experiment-level)
- All-or-nothing access to project contents
- May not suit large organisations with many projects

**Implementation:**
- Add `collaborators` field to project manifest
- Implement project-level permissions
- Support cloud storage backends for shared access

### Model 2: Workspace-Based Multi-Tenancy (v2.1.0+)

**Concept:** Organisations have workspaces containing projects; users belong to workspaces with roles.

```
Workspace (Organisation)
├── Members
│   ├── User 1 (Admin)
│   ├── User 2 (Editor)
│   └── User 3 (Viewer)
├── Projects
│   ├── Project A
│   ├── Project B
│   └── Project C
├── Shared Templates
├── Shared Prompts
└── Organisation Settings
    ├── Default Provider
    ├── Cost Limits
    └── Compliance Policies
```

**Pros:**
- Enterprise-grade multi-tenancy
- Centralised administration
- Shared resources (templates, prompts)
- Organisational policies

**Cons:**
- Significant implementation effort
- Requires user management infrastructure
- May be overkill for small teams

**Implementation:**
- Central user/workspace database
- RBAC with predefined roles
- Workspace-scoped resources
- Admin console for management

### Model 3: Real-Time Collaborative Editing (v3.0.0+)

**Concept:** Multiple users edit personas/experiments simultaneously with live sync.

**Pros:**
- Google Docs-like experience
- Immediate visibility of changes
- Comments and suggestions in-line

**Cons:**
- Highest implementation complexity
- Requires operational transformation or CRDT
- May not match persona generation workflow (async by nature)

**Assessment:** Defer to v3.0.0 or later. Persona generation is inherently asynchronous; real-time editing adds complexity without clear value for core workflows.

---

## Storage Architecture

### Option 1: Filesystem + Sync Service

**Approach:** Keep filesystem storage, use external sync (Dropbox, OneDrive, Google Drive)

**Pros:**
- No storage changes needed
- Users manage their own sync
- Works offline

**Cons:**
- Conflict resolution delegated to sync service
- No fine-grained access control
- Audit logging external to Persona

**Recommendation:** Acceptable for personal use, not for enterprise.

### Option 2: Cloud Object Storage (Recommended)

**Approach:** Abstract storage behind interface; support S3, GCS, Azure Blob

**Pros:**
- Scalable and durable
- Fine-grained ACLs
- Audit logging built-in
- Multi-region support

**Cons:**
- Requires cloud account setup
- Network dependency
- Cost for storage

**Implementation:**

```python
# Abstract storage interface
class StorageBackend(ABC):
    @abstractmethod
    def read(self, path: str) -> bytes: ...
    @abstractmethod
    def write(self, path: str, data: bytes) -> None: ...
    @abstractmethod
    def list(self, prefix: str) -> list[str]: ...
    @abstractmethod
    def delete(self, path: str) -> None: ...

# Implementations
class LocalStorage(StorageBackend): ...
class S3Storage(StorageBackend): ...
class GCSStorage(StorageBackend): ...
class AzureBlobStorage(StorageBackend): ...
```

### Option 3: Database Storage

**Approach:** Store all data in PostgreSQL/SQLite with blob columns or references

**Pros:**
- Transactional consistency
- Complex queries possible
- Single source of truth

**Cons:**
- Large binary storage inefficient
- More complex than object storage
- Requires database operations expertise

**Recommendation:** Use database for metadata, object storage for artefacts.

---

## Authentication & Identity

### Option 1: OAuth2/OIDC (Recommended)

**Approach:** Federated identity via standard protocols

**Supported Providers:**
- Google Workspace
- Microsoft Entra ID (Azure AD)
- Okta
- Auth0
- Keycloak (self-hosted)

**Pros:**
- Industry standard
- No password management
- Enterprise SSO support
- MFA handled by provider

**Cons:**
- Requires identity provider setup
- Network dependency for auth

**Implementation:**

```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    ...
)
```

### Option 2: Username/Password + MFA

**Approach:** Traditional authentication with optional MFA

**Pros:**
- No external dependencies
- Works offline after initial auth

**Cons:**
- Password management burden
- MFA implementation needed
- Less enterprise-friendly

**Recommendation:** Support as fallback, but prioritise OAuth2/OIDC.

### Option 3: API Keys Only

**Approach:** Simple API key authentication

**Pros:**
- Simple implementation
- Works well for programmatic access
- No user management

**Cons:**
- No user identity
- Sharing requires key sharing
- Limited audit granularity

**Recommendation:** Keep for API access, add user auth for WebUI.

---

## Role-Based Access Control (RBAC)

### Predefined Roles

| Role | Project | Experiments | Personas | Settings |
|------|---------|-------------|----------|----------|
| **Owner** | Full | Full | Full | Full |
| **Admin** | Read | Full | Full | Full |
| **Editor** | Read | Create/Edit | Create/Edit | Read |
| **Contributor** | Read | Create | Create | Read |
| **Viewer** | Read | Read | Read | None |

### Permission Matrix

| Action | Owner | Admin | Editor | Contributor | Viewer |
|--------|-------|-------|--------|-------------|--------|
| Create project | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete project | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage members | ✅ | ✅ | ❌ | ❌ | ❌ |
| Create experiment | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit experiment | ✅ | ✅ | ✅ | Own only | ❌ |
| Delete experiment | ✅ | ✅ | Own only | ❌ | ❌ |
| Generate personas | ✅ | ✅ | ✅ | ✅ | ❌ |
| View personas | ✅ | ✅ | ✅ | ✅ | ✅ |
| Export personas | ✅ | ✅ | ✅ | ✅ | ✅ |
| View audit logs | ✅ | ✅ | ❌ | ❌ | ❌ |

### Custom Roles (Future)

For v2.2.0+, allow organisations to define custom roles:

```yaml
# Custom role definition
roles:
  researcher:
    inherit: contributor
    permissions:
      - experiment.delete.own
      - persona.annotate
  compliance_officer:
    inherit: viewer
    permissions:
      - audit.view
      - persona.export.anonymised
```

---

## Audit Logging

### Existing Foundation (F-123)

Persona v1.7.0 includes generation audit trail (F-123). Extend for collaboration:

### Events to Log

| Category | Events |
|----------|--------|
| **Authentication** | Login, logout, failed attempts |
| **Authorisation** | Permission granted/denied |
| **Projects** | Create, update, delete, share |
| **Experiments** | Create, update, delete, run |
| **Personas** | Generate, export, annotate |
| **Members** | Invite, remove, role change |
| **Settings** | Config change, provider update |

### Audit Record Schema

```python
@dataclass
class AuditRecord:
    id: str                    # Unique record ID
    timestamp: datetime        # When it happened
    actor_id: str              # Who did it
    actor_type: str            # user, api_key, system
    action: str                # What was done
    resource_type: str         # What type of resource
    resource_id: str           # Which resource
    workspace_id: str          # Which workspace
    project_id: str | None     # Which project (if applicable)
    details: dict              # Additional context
    ip_address: str            # Client IP
    user_agent: str            # Client identifier
```

### Retention and Compliance

- **Default retention:** 90 days
- **Compliance mode:** 7 years (configurable)
- **Export format:** JSON, CSV, SIEM-compatible
- **Immutability:** Append-only log with cryptographic chaining

---

## Data Isolation

### Multi-Tenant Isolation Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **Logical** | Same database, filtered by tenant_id | Cost-effective, simpler |
| **Schema** | Separate database schemas per tenant | Better isolation |
| **Database** | Separate databases per tenant | Maximum isolation |
| **Infrastructure** | Dedicated deployment per tenant | Enterprise/regulated |

**Recommendation:** Start with logical isolation (tenant_id filtering); offer dedicated infrastructure for enterprise customers.

### Data Boundaries

```
┌─────────────────────────────────────────┐
│ Workspace (Tenant Boundary)             │
│ ┌─────────────────────────────────────┐ │
│ │ Project 1                           │ │
│ │ ┌─────────────┐ ┌─────────────────┐ │ │
│ │ │ Experiment  │ │ Experiment      │ │ │
│ │ │ ┌─────────┐ │ │ ┌─────────────┐ │ │ │
│ │ │ │ Persona │ │ │ │ Persona     │ │ │ │
│ │ │ └─────────┘ │ │ └─────────────┘ │ │ │
│ │ └─────────────┘ └─────────────────┘ │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ Project 2                           │ │
│ │ ...                                 │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Project Sharing (v2.0.0)

**Features:**
- F-141: Team Workspace Support (basic)
- F-143: Persona Sharing & Publishing

**Scope:**
- Project-level sharing via invitation
- Simple roles: Owner, Editor, Viewer
- Cloud storage backend (S3/GCS)
- Basic audit logging

**Effort:** Medium

### Phase 2: Workspace Multi-Tenancy (v2.1.0)

**Features:**
- F-142: Role-Based Access Control
- Workspace management

**Scope:**
- Full workspace/organisation model
- Predefined roles with RBAC
- User management console
- SSO integration

**Effort:** High

### Phase 3: Enterprise Features (v2.2.0+)

**Features:**
- Custom roles
- Advanced audit and compliance
- Data residency options
- Dedicated infrastructure option

**Effort:** High

---

## Security Considerations

### Authentication Security

- Token-based sessions (JWT with short expiry)
- Refresh token rotation
- Session invalidation on password change
- IP-based anomaly detection

### Authorisation Security

- Permission checks at API layer
- No client-side permission enforcement
- Audit all authorisation decisions
- Principle of least privilege defaults

### Data Security

- Encryption at rest (cloud storage)
- Encryption in transit (TLS 1.3)
- Customer-managed keys option (BYOK)
- Data residency compliance

---

## Proposed Features

This research informs the following features:

1. **F-141: Team Workspace Support** (P0, v2.0.0)
2. **F-142: Role-Based Access Control** (P1, v2.0.0)
3. **F-143: Persona Sharing & Publishing** (P1, v2.0.0)
4. **F-144: Audit Log Export** (P1, v2.0.0)
5. **F-145: Cloud Storage Integration** (P1, v2.0.0)

---

## Research Sources

### Multi-Tenancy Architecture

- [SaaS Multi-Tenant Architecture Patterns](https://docs.aws.amazon.com/whitepapers/latest/saas-tenant-isolation-strategies/saas-tenant-isolation-strategies.html)
- [Multi-Tenant Data Architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/considerations/tenancy-models)
- [Stripe's Multi-Tenant Architecture](https://stripe.com/blog/how-we-build-multi-tenant-systems)

### RBAC and Identity

- [OAuth2 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [RBAC NIST Standard](https://csrc.nist.gov/publications/detail/conference-paper/2000/12/11/role-based-access-controls)
- [Authlib Documentation](https://docs.authlib.org/)

### Collaboration Patterns

- [Real-Time Collaboration with CRDTs](https://crdt.tech/)
- [Google Docs Architecture](https://www.youtube.com/watch?v=hv3_bGLo9U8)
- [Figma's Multiplayer Technology](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)

### Enterprise Security

- [SOC 2 Compliance Overview](https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2)
- [GDPR Data Processing Requirements](https://gdpr.eu/data-processing/)
- [Enterprise Security Checklist](https://www.enterpriseready.io/)

---

## Related Documentation

- [F-123: Generation Audit Trail](../roadmap/features/completed/F-123-generation-audit-trail.md)
- [F-124: Experiment Management](../roadmap/features/completed/F-124-experiment-management.md)
- [R-020: WebUI Framework Selection](./R-020-webui-framework-selection.md)
- [ADR-0036: Multi-Tenancy Architecture](../decisions/adrs/ADR-0036-multi-tenancy-architecture.md) (Planned)
