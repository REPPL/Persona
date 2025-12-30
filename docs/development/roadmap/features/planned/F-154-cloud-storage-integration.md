# F-154: Cloud Storage Integration

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-154 |
| **Title** | Cloud Storage Integration |
| **Priority** | P1 (High) |
| **Category** | Infrastructure |
| **Milestone** | [v2.0.0](../../milestones/v2.0.0.md) |
| **Status** | Planned |
| **Dependencies** | F-151 (Team Workspace Support) |

---

## Problem Statement

Local file storage limits collaboration and scalability:
- Teams can't share data across machines
- No backup or disaster recovery
- Limited storage capacity
- No geographic distribution
- Compliance requirements for data residency

Cloud storage enables team collaboration and enterprise deployment patterns.

---

## Design Approach

Implement a storage abstraction layer supporting multiple cloud backends (S3, GCS, Azure Blob) with local storage as default, following [R-031: Cloud Deployment Patterns](../../../research/R-031-cloud-deployment-patterns.md).

---

## Key Capabilities

### 1. Storage Backend Configuration

Configure storage backend per workspace.

```yaml
# persona.yaml
storage:
  backend: s3  # local | s3 | gcs | azure

  s3:
    bucket: company-personas
    prefix: product-research/
    region: eu-west-2
    # Credentials via environment or IAM role

  gcs:
    bucket: company-personas
    prefix: product-research/
    project: my-gcp-project

  azure:
    container: personas
    prefix: product-research/
    account: companydata
```

### 2. Transparent Storage Operations

Storage operations work identically across backends.

```bash
# All commands work regardless of backend
persona generate input.json --output ./personas/  # Writes to configured backend
persona list ./personas/                           # Lists from configured backend
persona export ./personas/ --format yaml           # Reads from configured backend

# Check storage status
persona storage status

# Storage statistics
persona storage stats
```

**Output:**
```
Storage Status
═════════════════════════════════════════════════════════════════

Backend: AWS S3
Bucket: company-personas
Prefix: product-research/
Region: eu-west-2

Statistics:
  Objects: 1,247
  Total Size: 45.3 MB
  Last Modified: 2025-01-20 14:32 UTC

Health: ✅ Connected
```

### 3. Storage Abstraction Layer

Unified interface for all storage backends.

```python
from abc import ABC, abstractmethod

class StorageBackend(ABC):
    @abstractmethod
    async def read(self, path: str) -> bytes:
        """Read object from storage."""
        pass

    @abstractmethod
    async def write(self, path: str, data: bytes) -> None:
        """Write object to storage."""
        pass

    @abstractmethod
    async def list(self, prefix: str) -> list[StorageObject]:
        """List objects with prefix."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete object from storage."""
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if object exists."""
        pass

class S3Backend(StorageBackend):
    """AWS S3 implementation."""
    pass

class GCSBackend(StorageBackend):
    """Google Cloud Storage implementation."""
    pass

class AzureBlobBackend(StorageBackend):
    """Azure Blob Storage implementation."""
    pass

class LocalBackend(StorageBackend):
    """Local filesystem implementation."""
    pass
```

### 4. Migration Between Backends

Migrate data between storage backends.

```bash
# Migrate from local to S3
persona storage migrate --from local --to s3

# Migrate between cloud providers
persona storage migrate --from s3 --to gcs

# Dry run
persona storage migrate --from local --to s3 --dry-run

# With progress
persona storage migrate --from local --to s3 --progress
```

**Output:**
```
Storage Migration: local → s3
═════════════════════════════════════════════════════════════════

Phase 1: Inventory
  Local objects: 1,247
  Total size: 45.3 MB

Phase 2: Migration
  [████████████████████░░░░░░░░░░] 67% (835/1,247)
  Current: personas/customer-sarah.yaml
  Speed: 2.3 MB/s
  ETA: 2 minutes

Phase 3: Verification
  Pending...

Press Ctrl+C to pause migration.
```

### 5. Caching Layer

Local cache for cloud storage performance.

```yaml
storage:
  backend: s3
  s3:
    bucket: company-personas

  cache:
    enabled: true
    path: ~/.persona/cache
    max_size: 1GB
    ttl: 1h
```

```bash
# Cache statistics
persona storage cache stats

# Clear cache
persona storage cache clear

# Warm cache
persona storage cache warm ./personas/
```

---

## Implementation Tasks

### Phase 1: Storage Abstraction

- [ ] Define StorageBackend interface
- [ ] Implement LocalBackend
- [ ] Add storage backend factory
- [ ] Integrate with existing file operations
- [ ] Add storage configuration schema

### Phase 2: S3 Backend

- [ ] Implement S3Backend
- [ ] Add credential handling (env, IAM, profile)
- [ ] Implement multipart upload for large files
- [ ] Add retry logic with exponential backoff
- [ ] Test with different S3-compatible services

### Phase 3: GCS & Azure Backends

- [ ] Implement GCSBackend
- [ ] Implement AzureBlobBackend
- [ ] Add authentication for each provider
- [ ] Test cross-provider compatibility
- [ ] Add provider-specific optimisations

### Phase 4: Migration & Caching

- [ ] Implement migration workflow
- [ ] Add dry-run and progress display
- [ ] Implement local caching layer
- [ ] Add cache invalidation
- [ ] Create cache warming functionality

---

## CLI Commands

```bash
# Storage configuration
persona storage config show
persona storage config set backend s3
persona storage config test

# Storage operations
persona storage status
persona storage stats [--detailed]
persona storage list [PREFIX]
persona storage sync --from PATH --to PATH

# Migration
persona storage migrate --from BACKEND --to BACKEND [--dry-run] [--progress]
persona storage migrate pause
persona storage migrate resume

# Cache management
persona storage cache stats
persona storage cache clear [--older-than DURATION]
persona storage cache warm PATH
```

---

## Success Criteria

- [ ] All three cloud backends functional
- [ ] Transparent operation across backends
- [ ] Migration between backends works
- [ ] Caching improves cloud performance
- [ ] Credentials handled securely
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
# Complete storage configuration
storage:
  # Backend selection
  backend: s3  # local | s3 | gcs | azure

  # AWS S3 configuration
  s3:
    bucket: company-personas
    prefix: workspaces/product-research/
    region: eu-west-2
    endpoint_url: null  # For S3-compatible services
    signature_version: s3v4

  # Google Cloud Storage configuration
  gcs:
    bucket: company-personas
    prefix: workspaces/product-research/
    project: my-gcp-project
    credentials_file: null  # Uses ADC by default

  # Azure Blob Storage configuration
  azure:
    container: personas
    prefix: workspaces/product-research/
    account: companydata
    connection_string: null  # Or use managed identity

  # Local storage configuration
  local:
    path: ~/.persona/data

  # Caching configuration
  cache:
    enabled: true
    path: ~/.persona/cache
    max_size: 1GB
    ttl: 1h
    strategy: lru  # lru | lfu | fifo

  # Performance tuning
  performance:
    concurrent_uploads: 4
    chunk_size: 5MB
    retry_attempts: 3
    retry_delay: 1s
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cloud provider outage | Low | High | Multi-backend support, local fallback |
| Credential exposure | Low | Critical | IAM roles, secret management |
| Migration data loss | Low | Critical | Verification, backup |
| Cost overruns | Medium | Medium | Usage monitoring, alerts |
| Latency issues | Medium | Medium | Caching, regional deployment |

---

## Related Documentation

- [v2.0.0 Milestone](../../milestones/v2.0.0.md)
- [F-151: Team Workspace Support](F-151-team-workspace-support.md)
- [R-031: Cloud Deployment Patterns](../../../research/R-031-cloud-deployment-patterns.md)
- [ADR-0031: Caching Architecture](../../../decisions/adrs/ADR-0031-caching-architecture.md)

---

**Status**: Planned
