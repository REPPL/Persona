# F-001: Multi-Format Data Loading

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001 |
| **Milestone** | v0.1.0 |
| **Priority** | P0 |
| **Category** | Data |

## Problem Statement

Users need to load qualitative research data from various file formats. The system must support common formats and combine multiple files into a unified dataset for LLM analysis.

## Design Approach

- Support: CSV, JSON, TXT, Markdown, YAML, Org-mode
- Combine multiple files with clear separators
- Validate content before processing
- Calculate token count for cost estimation

## Implementation Tasks

- [ ] Create DataLoader base class
- [ ] Implement format-specific loaders:
  - [ ] CSVLoader
  - [ ] JSONLoader
  - [ ] TXTLoader
  - [ ] MarkdownLoader
  - [ ] YAMLLoader
  - [ ] OrgLoader
- [ ] Build file discovery (glob, recursive)
- [ ] Add content validation
- [ ] Implement file combination logic
- [ ] Add token counting (tiktoken)
- [ ] Write unit tests

## Success Criteria

- [ ] All supported formats load correctly
- [ ] Multiple files combined with clear separators
- [ ] Token count accurate within 5%
- [ ] Clear error messages for unsupported formats
- [ ] Test coverage ≥ 80%

## Dependencies

- tiktoken for token counting

---

## Related Documentation

- [UC-001: Generate Personas](../../../../use-cases/briefs/UC-001-generate-personas.md)
- [F-002: LLM Provider Abstraction](F-002-llm-provider-abstraction.md)
