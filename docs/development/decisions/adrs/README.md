# Architecture Decision Records

Documented architecture and design decisions for Persona.

## ADR Index

### Architecture Decisions

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0001](ADR-0001-hybrid-specification-approach.md) | Hybrid Specification Approach | Accepted |
| [ADR-0002](ADR-0002-multi-provider-architecture.md) | Multi-Provider LLM Architecture | Accepted |
| [ADR-0003](ADR-0003-experiment-centric-workflow.md) | Experiment-Centric Workflow | Accepted |
| [ADR-0004](ADR-0004-jinja2-templating.md) | Jinja2 Prompt Templating | Accepted |
| [ADR-0005](ADR-0005-cli-framework.md) | Typer + Rich CLI Framework | Accepted |
| [ADR-0006](ADR-0006-yaml-configuration.md) | YAML-Based Configuration | Accepted |
| [ADR-0007](ADR-0007-feature-centric-roadmap.md) | Feature-Centric Roadmap | Accepted |

### Design Decisions

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0008](ADR-0008-structured-json-output.md) | Structured JSON Output | Accepted |
| [ADR-0009](ADR-0009-timestamped-output.md) | Timestamped Output Organisation | Accepted |
| [ADR-0010](ADR-0010-cost-estimation.md) | Cost Estimation Before Generation | Accepted |
| [ADR-0011](ADR-0011-multi-step-workflow.md) | Multi-Step Workflow Orchestration | Accepted |
| [ADR-0012](ADR-0012-multi-variation-generation.md) | Multi-Variation Generation | Accepted |
| [ADR-0013](ADR-0013-formatter-registry.md) | Formatter Registry Pattern | Accepted |
| [ADR-0014](ADR-0014-security-api-keys.md) | Security-First API Key Handling | Accepted |

### Process Decisions

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0015](ADR-0015-minor-version-releases.md) | Minor Version Releases Only | Accepted |
| [ADR-0016](ADR-0016-ai-transparency.md) | AI Transparency Commitment | Accepted |
| [ADR-0017](ADR-0017-testing-alongside.md) | Testing Alongside Implementation | Accepted |
| [ADR-0018](ADR-0018-documentation-as-you-go.md) | Documentation As You Go | Accepted |

### Feature Design Decisions

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0019](ADR-0019-persona-validation-methodology.md) | Persona Validation Methodology | Accepted |
| [ADR-0020](ADR-0020-reasoning-capture-architecture.md) | Reasoning Capture Architecture | Accepted |
| [ADR-0021](ADR-0021-programmatic-api.md) | Programmatic API Design | Accepted |
| [ADR-0022](ADR-0022-interactive-cli-library.md) | Interactive CLI Library Selection | Accepted |

### Retroactive Decisions (v1.2.0 - v1.11.0)

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0023](ADR-0023-plugin-system-architecture.md) | Plugin System Architecture | Accepted |
| [ADR-0024](ADR-0024-tui-dashboard-architecture.md) | TUI Dashboard Architecture | Accepted |
| [ADR-0025](ADR-0025-ollama-provider-integration.md) | Ollama Provider Integration | Accepted |
| [ADR-0026](ADR-0026-hybrid-pipeline-strategy.md) | Hybrid Pipeline Strategy | Accepted |
| [ADR-0027](ADR-0027-data-lineage-implementation.md) | Data Lineage Implementation | Accepted |
| [ADR-0028](ADR-0028-pii-detection-strategy.md) | PII Detection Strategy | Accepted |

### Robustness Decisions

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0029](ADR-0029-error-handling-strategy.md) | Error Handling Strategy | Planned |
| [ADR-0030](ADR-0030-async-execution-model.md) | Async Execution Model | Planned |
| [ADR-0031](ADR-0031-caching-architecture.md) | Caching Architecture | Planned |
| [ADR-0032](ADR-0032-performance-baseline-commitment.md) | Performance Baseline Commitment | Planned |
| [ADR-0033](ADR-0033-deprecation-policy.md) | Deprecation Policy | Planned |

### Future-Proofing Decisions

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0034](ADR-0034-breaking-changes-policy.md) | v2.0.0 Breaking Changes Policy | Planned |
| [ADR-0035](ADR-0035-webui-technology-selection.md) | WebUI Technology Selection | Planned |
| [ADR-0036](ADR-0036-multi-tenancy-architecture.md) | Multi-Tenancy Architecture | Planned |

## ADR Format

```markdown
# ADR-XXXX: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What is the issue we're addressing?]

## Decision
[What decision was made?]

## Consequences
[What are the implications?]
```

---

## Related Documentation

- [Decisions Overview](../README.md)
- [RFCs](../rfcs/)
