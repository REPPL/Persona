# Research

State-of-the-art research to inform implementation decisions for Persona.

## Purpose

This directory contains comprehensive research notes on key technical areas. Each research note:

- Analyses current industry standards and best practices (2025)
- Evaluates available libraries and tools
- Compares alternatives with trade-offs
- Provides implementation-ready recommendations
- Links to relevant ADRs for decision tracking

## Research Notes

| ID | Topic | Status | Related ADR |
|----|-------|--------|-------------|
| [R-001](./R-001-structured-llm-output.md) | Structured LLM Output | Complete | ADR-0008 |
| [R-002](./R-002-multi-provider-abstraction.md) | Multi-Provider Abstraction | Complete | ADR-0002 |
| [R-003](./R-003-persona-generation-methodology.md) | Persona Generation Methodology | Complete | ADR-0003 |
| [R-004](./R-004-token-counting-cost-estimation.md) | Token Counting & Cost Estimation | Complete | ADR-0010 |
| [R-005](./R-005-cli-design-patterns.md) | CLI Design Patterns | Complete | ADR-0005 |
| [R-006](./R-006-yaml-configuration-validation.md) | YAML Configuration & Validation | Complete | ADR-0006 |
| [R-007](./R-007-prompt-templating.md) | Prompt Templating | Complete | ADR-0004 |
| [R-008](./R-008-persona-validation-methodology.md) | Persona Validation Methodology | Complete | ADR-0019 |
| [R-009](./R-009-reasoning-capture.md) | Reasoning Capture | Complete | ADR-0020 |
| [R-010](./R-010-mvp-architecture.md) | MVP Architecture | Complete | - |
| [R-011](./R-011-interactive-cli-libraries.md) | Interactive CLI Libraries | Complete | ADR-0022 |
| [R-012](./R-012-tui-fullscreen-layout-patterns.md) | Full-Screen TUI Layout Patterns | Complete | - |
| [R-013](./R-013-local-model-assessment.md) | Local Model Assessment | Complete | - |
| [R-014](./R-014-shin-et-al-gap-analysis.md) | Shin et al. DIS 2024 Gap Analysis | Complete | - |
| [R-015](./R-015-quality-metrics-taxonomy.md) | Quality Metrics Taxonomy | Complete | - |
| [R-016](./R-016-experiment-project-organisation.md) | Experiment & Project Organisation | Complete | - |
| [R-017](./R-017-remote-data-ingestion.md) | Remote Data Ingestion | Complete | - |
| [R-018](./R-018-documentation-audit-and-automation.md) | Documentation Audit & Automation | Complete | - |
| [R-019](./R-019-project-automation-implementation.md) | Project Automation Implementation | Complete | - |

---

## Research-to-Feature Mapping

Quick reference showing which features each research document informs:

| Research | Milestone | Features Informed |
|----------|-----------|-------------------|
| R-001 | v0.1.0 | F-004, F-005 (Persona generation, output formatting) |
| R-002 | v0.1.0 | F-002, F-011 (LLM abstraction, multi-provider) |
| R-003 | v0.1.0 | F-004, F-019 (Generation methodology, validation) |
| R-004 | v0.1.0 | F-007, F-014 (Cost estimation, model pricing) |
| R-005 | v0.1.0 | F-008, F-015, F-016 (CLI interface, commands, Rich UI) |
| R-006 | v0.1.0 | F-012, F-055 (Experiment config, config validation) |
| R-007 | v0.1.0 | F-003, F-046 (Prompt templating, custom templates) |
| R-008 | v0.2.0 | F-019, F-106 (Persona validation, quality metrics) |
| R-009 | v0.1.0 | F-032 (Reasoning capture) |
| R-010 | v0.1.0 | Overall architecture |
| R-011 | v1.0.0 | F-092 (Interactive mode) |
| R-012 | v1.2.0 | F-098-F-103 (TUI dashboard features) |
| R-013 | v1.3.0 | F-112, F-113, F-116 (Ollama, PII, hybrid pipeline) |
| R-014 | v1.6.0 | F-117, F-118 (Academic validation, hallucination) |
| R-015 | v1.6.0+ | F-106, F-119, F-121 (Quality metrics, bias, diversity) |
| R-016 | v1.8.0+ | F-124, F-125 (Experiment management, lineage) |
| R-017 | v1.10.0 | F-126 (URL data ingestion) |
| R-018 | v1.10.0+ | F-127 (Documentation, project automation) |
| R-019 | v1.10.0 | F-127 (Project automation infrastructure) |

## Research Methodology

Each research note follows a consistent structure:

1. **Executive Summary** - Key findings and recommendation
2. **Current State of the Art** - Industry standards, academic research, open source ecosystem
3. **Alternatives Analysis** - Comparison table with pros/cons
4. **Recommendation** - Primary approach with rationale and implementation notes
5. **Impact on Existing Decisions** - ADR and feature spec updates required
6. **Sources** - All references with URLs

## How Research Informs Implementation

```
Research Notes → Validate/Update ADRs → Guide Feature Implementation
     ↓                    ↓                        ↓
  R-001...R-007    ADR-0002...ADR-0010    F-001...F-018
```

Research notes provide the **evidence base** for architecture decisions. When research reveals better approaches than originally planned, ADRs are updated with:

- **Alternatives Considered** section documenting what was evaluated
- **Research Reference** linking to the relevant research note

---

## Related Documentation

- [Architecture Decision Records](../decisions/adrs/)
- [Feature Specifications](../roadmap/features/)
- [Development Hub](../README.md)
