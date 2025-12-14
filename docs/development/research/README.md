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
