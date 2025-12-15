# F-123: Generation Audit Trail

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-007, UC-008 |
| **Milestone** | v1.7.0 |
| **Priority** | P1 |
| **Category** | Compliance |
| **Status** | Planned |

## Problem Statement

Research reproducibility requires complete provenance tracking of LLM-generated outputs. Regulatory frameworks (EU AI Act Article 19) mandate audit trails for high-risk AI systems. Without generation audit trails, users cannot verify how personas were created, with what data, or under what conditions.

## Research Foundation

### Academic Sources

- **PROLIT System (Journal of Big Data, Jul 2025)**: LLM-guided provenance collection
- **ProvenanceWeek 2025**: ChatGPT-4o achieves 73% accuracy in provenance extraction
- **Nature Machine Intelligence (2024)**: Dataset licensing audit across 1,800 datasets
- **EU AI Act Article 19**: Six-month log retention for high-risk systems

### Key Findings

- Provenance enhances transparency, explainability, and reproducibility
- LLM stochasticity means identical inputs may produce different outputs
- Audit trails must capture model version, parameters, and human-in-the-loop interactions
- Research with proprietary APIs may not be practically reproducible

### Compliance Requirements

| Framework | Requirement |
|-----------|-------------|
| **EU AI Act** | Automatic log generation, 6-month retention |
| **NIST AI RMF** | Traceability and documentation |
| **Model Cards** | Standardised model documentation |
| **Data Provenance** | Source attribution and licensing |

## Design Approach

### Audit Trail Components

| Component | Description | Retention |
|-----------|-------------|-----------|
| **Input Record** | Source data hash, path, metadata | Permanent |
| **Prompt Record** | Template, variables, final prompt | Permanent |
| **Model Record** | Provider, model ID, version, parameters | Permanent |
| **Output Record** | Generated personas, timestamps | Permanent |
| **Quality Record** | Validation scores, issues found | Permanent |
| **Session Record** | User, environment, tool version | Permanent |

### Architecture

```
Generation Request
        │
        ▼
┌───────────────────┐
│   Audit Logger    │──────► Audit Store
└───────┬───────────┘        (JSON/SQLite)
        │
        ▼
┌───────────────────┐
│ Generation Pipeline│
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│   Audit Logger    │──────► Audit Store
└───────┬───────────┘
        │
        ▼
   Generated Personas
```

### Audit Record Schema

```json
{
  "audit_id": "uuid",
  "timestamp": "2025-12-15T10:30:00Z",
  "tool_version": "1.7.0",
  "session": {
    "user": "researcher@example.com",
    "environment": "darwin-arm64",
    "python_version": "3.12.0"
  },
  "input": {
    "data_hash": "sha256:abc123...",
    "data_path": "interviews.csv",
    "record_count": 50,
    "data_preview_hash": "sha256:def456..."
  },
  "generation": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "model_version": "2025-05-14",
    "temperature": 0.7,
    "max_tokens": 4096,
    "prompt_template": "default_persona",
    "prompt_hash": "sha256:ghi789...",
    "persona_count": 5
  },
  "output": {
    "personas_hash": "sha256:jkl012...",
    "output_path": "output/2025-12-15_103000/",
    "generation_time_ms": 15234
  },
  "quality": {
    "validation_passed": true,
    "quality_scores": {
      "completeness": 0.92,
      "consistency": 0.88
    }
  },
  "reproducibility": {
    "seed": 42,
    "deterministic": false,
    "api_call_ids": ["call_abc123", "call_def456"]
  }
}
```

### Python API

```python
from persona.core.audit import AuditTrail, AuditConfig

# Configure audit trail
config = AuditConfig(
    enabled=True,
    store_path="~/.persona/audit/",
    retention_days=180,  # EU AI Act compliance
    include_prompts=True,
    include_outputs=False,  # Hash only for privacy
    sign_records=True,  # Cryptographic signing
)

# Audit trail is automatic during generation
pipeline = GenerationPipeline(audit_config=config)
result = pipeline.generate(data, count=5)

# Access audit record
print(f"Audit ID: {result.audit_id}")

# Query audit history
trail = AuditTrail(config)
records = trail.query(
    start_date="2025-12-01",
    model="claude-sonnet-4-20250514",
)

# Export for compliance
trail.export(
    audit_ids=["uuid1", "uuid2"],
    format="json",
    output="compliance-report.json",
)

# Verify record integrity
is_valid = trail.verify(audit_id="uuid1")
```

### CLI Interface

```bash
# Enable audit trail (default in v1.7.0+)
persona generate data.csv --audit

# View audit history
persona audit list --since 2025-12-01

# Show specific audit record
persona audit show <audit-id>

# Export for compliance
persona audit export --format json --output audit-export.json

# Verify record integrity
persona audit verify <audit-id>

# Configure retention
persona config set audit.retention_days 180

# Disable audit (not recommended)
persona generate data.csv --no-audit
```

### Storage Options

| Store | Use Case | Performance |
|-------|----------|-------------|
| **JSON files** | Simple, portable | Good for < 10k records |
| **SQLite** | Queryable, single-file | Good for < 100k records |
| **PostgreSQL** | Enterprise, multi-user | Scalable |

## Implementation Tasks

- [ ] Create audit module structure (`persona/core/audit/`)
- [ ] Define audit record schema (Pydantic models)
- [ ] Implement JSON file store
- [ ] Implement SQLite store
- [ ] Add audit hooks to GenerationPipeline
- [ ] Implement data hashing (SHA-256)
- [ ] Add prompt template hashing
- [ ] Implement record signing (optional)
- [ ] Add retention policy enforcement
- [ ] Create `persona audit` CLI command group
- [ ] Add `--audit` / `--no-audit` flags to generate
- [ ] Implement query and export functionality
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Add compliance documentation

## Success Criteria

- [ ] All generation operations logged automatically
- [ ] Records queryable by date, model, data source
- [ ] Export compliant with EU AI Act requirements
- [ ] Record integrity verifiable
- [ ] Retention policies enforced
- [ ] CLI commands functional
- [ ] Test coverage ≥ 85%
- [ ] Audit overhead < 5% of generation time

## Dependencies

- F-073: Experiment Logger (logging infrastructure)
- F-076: Metadata Recording (metadata patterns)
- F-085: Global Configuration (config storage)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Storage growth | Medium | Medium | Retention policies, compression |
| Performance overhead | Low | Medium | Async logging, batching |
| Privacy concerns with prompt storage | Medium | High | Hash-only option, encryption |
| Clock skew in distributed systems | Low | Low | UTC timestamps, NTP sync |

---

## Related Documentation

- [Milestone v1.7.0](../../milestones/v1.7.0.md)
- [F-073: Experiment Logger](../completed/F-073-experiment-logger.md)
- [Configuration Reference](../../../../reference/configuration-reference.md)

---

**Status**: Planned
