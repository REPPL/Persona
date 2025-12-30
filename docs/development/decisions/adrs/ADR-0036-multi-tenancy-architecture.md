# ADR-0036: Multi-Tenancy Architecture

## Status

Planned

## Context

Enterprise adoption requires multi-tenancy to support:
- Multiple teams using shared Persona deployment
- Isolated data between organisations
- Role-based access control
- Resource quotas and billing
- Centralised administration

Need to design tenant isolation while maintaining shared infrastructure efficiency.

## Decision

Implement **project-based multi-tenancy** with logical isolation and shared infrastructure.

### Tenancy Model

| Model | Description | Isolation | Complexity | Cost |
|-------|-------------|-----------|------------|------|
| **Single-tenant** | Dedicated instance per org | ✅ High | High | High |
| **Schema per tenant** | Shared DB, separate schemas | ⚠️ Medium | Medium | Medium |
| **Row-level** | Shared everything, tenant ID column | ⚠️ Lower | Low | Low |
| **Project-based** | Logical projects with RBAC | ⚠️ Medium | Medium | Medium |

**Selected: Project-based tenancy**

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Multi-Tenancy Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Organisation Layer                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Org A     │  │    Org B     │  │    Org C     │      │
│  │ (tenant_id)  │  │ (tenant_id)  │  │ (tenant_id)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                 │               │
│         ▼                 ▼                 ▼               │
│  Project Layer                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │ │
│  │  │Project 1│  │Project 2│  │Project 3│  │Project 4│  │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│         │                                                    │
│         ▼                                                    │
│  Access Control                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Users ──▶ Roles ──▶ Permissions ──▶ Resources        │ │
│  └────────────────────────────────────────────────────────┘ │
│         │                                                    │
│         ▼                                                    │
│  Shared Infrastructure                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Database   │  │    Cache     │  │   Storage    │      │
│  │  (row-level) │  │  (prefixed)  │  │  (prefixed)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Model

```python
@dataclass
class Organisation:
    id: str
    name: str
    settings: OrganisationSettings
    created_at: datetime
    subscription_tier: str

@dataclass
class Project:
    id: str
    organisation_id: str  # Foreign key
    name: str
    settings: ProjectSettings
    created_at: datetime

@dataclass
class User:
    id: str
    email: str
    organisation_id: str
    roles: list[Role]

@dataclass
class Role:
    id: str
    name: str  # admin, editor, viewer
    permissions: list[Permission]

@dataclass
class Permission:
    resource: str  # project, persona, experiment
    action: str  # create, read, update, delete
    scope: str  # own, project, organisation
```

### Database Schema

```sql
-- Organisations
CREATE TABLE organisations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    settings JSON,
    subscription_tier TEXT DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    organisation_id TEXT NOT NULL REFERENCES organisations(id),
    name TEXT NOT NULL,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    organisation_id TEXT NOT NULL REFERENCES organisations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Roles
CREATE TABLE roles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    permissions JSON NOT NULL
);

-- User-Role mapping
CREATE TABLE user_roles (
    user_id TEXT REFERENCES users(id),
    role_id TEXT REFERENCES roles(id),
    project_id TEXT REFERENCES projects(id),  -- NULL = org-wide
    PRIMARY KEY (user_id, role_id, project_id)
);

-- Personas (with tenant isolation)
CREATE TABLE personas (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    data JSON NOT NULL,
    created_by TEXT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Row-level security
CREATE POLICY persona_isolation ON personas
    USING (project_id IN (
        SELECT p.id FROM projects p
        JOIN user_roles ur ON ur.project_id = p.id OR ur.project_id IS NULL
        WHERE ur.user_id = current_user_id()
    ));
```

### Access Control

**Predefined Roles:**

| Role | Permissions |
|------|-------------|
| **Owner** | Full access to organisation |
| **Admin** | Manage users, projects, settings |
| **Editor** | Create, edit, delete personas/experiments |
| **Viewer** | Read-only access |
| **API** | Programmatic access only |

**Permission Checks:**
```python
class PermissionChecker:
    def check(
        self,
        user: User,
        resource: str,
        action: str,
        resource_id: str | None = None
    ) -> bool:
        # Get user's roles for this resource
        roles = self.get_user_roles(user, resource, resource_id)

        # Check if any role grants this permission
        for role in roles:
            for permission in role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True

        return False

    async def require(self, user: User, resource: str, action: str, resource_id: str | None = None) -> None:
        if not self.check(user, resource, action, resource_id):
            raise PermissionDeniedError(f"Cannot {action} {resource}")
```

### Resource Quotas

```python
@dataclass
class Quota:
    max_projects: int
    max_personas_per_project: int
    max_api_calls_per_month: int
    max_storage_gb: float

TIER_QUOTAS = {
    "free": Quota(
        max_projects=3,
        max_personas_per_project=100,
        max_api_calls_per_month=1000,
        max_storage_gb=1.0
    ),
    "team": Quota(
        max_projects=20,
        max_personas_per_project=1000,
        max_api_calls_per_month=10000,
        max_storage_gb=10.0
    ),
    "enterprise": Quota(
        max_projects=-1,  # Unlimited
        max_personas_per_project=-1,
        max_api_calls_per_month=-1,
        max_storage_gb=-1
    )
}
```

## Consequences

**Positive:**
- Efficient resource sharing
- Flexible access control
- Simple tenant onboarding
- Cost-effective scaling

**Negative:**
- Row-level security complexity
- Shared infrastructure risk
- Quota enforcement overhead

## Alternatives Considered

### Single-Tenant Deployment

**Description:** Dedicated instance per organisation.

**Pros:** Maximum isolation, simpler security.

**Cons:** Higher cost, operational overhead.

**Why Not Chosen:** Not cost-effective for smaller teams.

### Schema Per Tenant

**Description:** Shared database, separate schemas.

**Pros:** Good isolation, easier migrations.

**Cons:** Schema proliferation, connection pooling issues.

**Why Not Chosen:** Project-based simpler to manage.

### Kubernetes Namespaces

**Description:** Namespace per tenant.

**Pros:** Infrastructure isolation.

**Cons:** Kubernetes required, higher complexity.

**Why Not Chosen:** Overkill for MVP.

## Research Reference

See [R-021: Multi-User & Team Collaboration](../../research/R-021-multi-user-collaboration.md) for collaboration patterns.

---

## Related Documentation

- [R-021: Multi-User & Team Collaboration](../../research/R-021-multi-user-collaboration.md)
- [R-031: Cloud Deployment Patterns](../../research/R-031-cloud-deployment-patterns.md)
- [F-105: REST API](../../roadmap/features/completed/F-105-rest-api.md)

---

**Status**: Planned
