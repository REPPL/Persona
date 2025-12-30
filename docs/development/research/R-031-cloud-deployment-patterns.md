# R-031: Cloud Deployment Patterns

## Executive Summary

This research analyses cloud-native deployment patterns for Persona, covering containerisation, orchestration, and managed services. While Persona is primarily a CLI tool, cloud deployment enables team usage, API access, and managed services. Recommended approach: Docker-based deployment with Kubernetes support, using managed databases and secrets management.

---

## Research Context

| Attribute | Value |
|-----------|-------|
| **ID** | R-031 |
| **Category** | Enterprise Adoption |
| **Status** | Complete |
| **Priority** | P3 |
| **Informs** | v2.0.0+ cloud features |

---

## Problem Statement

Enterprise adoption requires cloud deployment capabilities:
- Shared team access to Persona
- REST API for integrations
- Managed configuration and secrets
- High availability and scaling
- Audit logging and compliance

The current CLI-focused architecture needs extension for cloud-native environments.

---

## State of the Art Analysis

### Deployment Models

| Model | Description | Use Case |
|-------|-------------|----------|
| **Local CLI** | Current model | Individual use |
| **Docker single** | Containerised API | Small teams |
| **Kubernetes** | Orchestrated pods | Enterprise |
| **Serverless** | Function-based | Burst workloads |
| **Managed SaaS** | Hosted service | Zero-ops |

### Containerisation

**Dockerfile Pattern:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install .

# Copy application
COPY src/ src/

# Non-root user
RUN useradd -m persona
USER persona

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["persona", "api", "serve", "--host", "0.0.0.0"]
```

**Multi-stage build:**
```dockerfile
# Build stage
FROM python:3.12 as builder
WORKDIR /build
COPY . .
RUN pip wheel -w /wheels .

# Runtime stage
FROM python:3.12-slim
COPY --from=builder /wheels /wheels
RUN pip install /wheels/*.whl
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: persona-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: persona
  template:
    metadata:
      labels:
        app: persona
    spec:
      containers:
      - name: persona
        image: persona:1.14.0
        ports:
        - containerPort: 8000
        env:
        - name: PERSONA_PROVIDER_API_KEY
          valueFrom:
            secretKeyRef:
              name: persona-secrets
              key: anthropic-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
```

### Serverless Patterns

**AWS Lambda + API Gateway:**
```python
# lambda_handler.py
from mangum import Mangum
from persona.api import app

handler = Mangum(app)
```

**Cloud Run:**
```yaml
# cloudbuild.yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/persona', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/persona']
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args:
  - 'run'
  - 'deploy'
  - 'persona'
  - '--image'
  - 'gcr.io/$PROJECT_ID/persona'
  - '--region'
  - 'europe-west1'
```

### Configuration Management

**Environment Variables:**
```bash
PERSONA_PROVIDER_NAME=anthropic
PERSONA_PROVIDER_API_KEY=${ANTHROPIC_API_KEY}
PERSONA_CACHE_ENABLED=true
PERSONA_LOG_LEVEL=info
```

**Kubernetes ConfigMap:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: persona-config
data:
  persona.yaml: |
    provider:
      name: anthropic
    cache:
      enabled: true
    logging:
      level: info
```

**Secrets Management:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: persona-secrets
type: Opaque
data:
  anthropic-api-key: <base64-encoded>
```

### Database Patterns

| Database | Use Case | Managed Service |
|----------|----------|-----------------|
| SQLite | Single instance | N/A |
| PostgreSQL | Multi-instance | RDS, Cloud SQL |
| Redis | Caching | ElastiCache, Memorystore |

---

## Architecture Patterns

### Single-Instance Docker

```
┌─────────────────────────────────────────────────────────────┐
│                    Single Instance                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐            │
│  │  Client  │────▶│  Persona │────▶│ Provider │            │
│  │          │     │   API    │     │   APIs   │            │
│  └──────────┘     └──────────┘     └──────────┘            │
│                        │                                     │
│                        ▼                                     │
│                   ┌──────────┐                              │
│                   │  SQLite  │                              │
│                   │ (volume) │                              │
│                   └──────────┘                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Kubernetes Multi-Instance

```
┌─────────────────────────────────────────────────────────────┐
│                 Kubernetes Cluster                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐     ┌───────────────────────────────────┐    │
│  │  Ingress │────▶│         Service (LoadBalancer)    │    │
│  └──────────┘     └───────────────────────────────────┘    │
│                              │                              │
│        ┌─────────────────────┼─────────────────────┐       │
│        ▼                     ▼                     ▼       │
│   ┌─────────┐          ┌─────────┐          ┌─────────┐   │
│   │  Pod 1  │          │  Pod 2  │          │  Pod 3  │   │
│   │ Persona │          │ Persona │          │ Persona │   │
│   └─────────┘          └─────────┘          └─────────┘   │
│        │                     │                     │       │
│        └─────────────────────┼─────────────────────┘       │
│                              ▼                              │
│                   ┌───────────────────┐                    │
│                   │    PostgreSQL     │                    │
│                   │   (StatefulSet)   │                    │
│                   └───────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Evaluation Matrix

| Pattern | Complexity | Scalability | Cost | Operations |
|---------|------------|-------------|------|------------|
| Local CLI | ✅ | ❌ | ✅ | ✅ |
| Docker single | ⚠️ | ⚠️ | ✅ | ⚠️ |
| Kubernetes | ⚠️ | ✅ | ⚠️ | ⚠️ |
| Serverless | ⚠️ | ✅ | ✅ | ✅ |
| Managed SaaS | ✅ | ✅ | ⚠️ | ✅ |

---

## Recommendation

### Phase 1: Docker Support
- Official Dockerfile
- Docker Compose for local testing
- Documentation for self-hosting

### Phase 2: Kubernetes Manifests
- Helm chart
- Horizontal pod autoscaling
- Secret management integration

### Phase 3: Cloud-Specific Guides
- AWS deployment guide (ECS, Lambda)
- GCP deployment guide (Cloud Run, GKE)
- Azure deployment guide (AKS, Functions)

---

## References

1. [12-Factor App](https://12factor.net/)
2. [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
3. [Docker Security](https://docs.docker.com/engine/security/)
4. [AWS Well-Architected](https://aws.amazon.com/architecture/well-architected/)

---

## Related Documentation

- [F-105: REST API](../roadmap/features/completed/F-105-rest-api.md)
- [R-021: Multi-User & Team Collaboration](R-021-multi-user-collaboration.md)

---

**Status**: Complete
