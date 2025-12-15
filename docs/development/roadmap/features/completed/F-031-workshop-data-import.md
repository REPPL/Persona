# F-031: Workshop Data Import

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-009 |
| **Milestone** | v0.2.0 |
| **Priority** | P2 |
| **Category** | Data |

## Problem Statement

Co-creation workshops produce photos of post-it notes on boards. Currently there's no way to import this visual data directly. Users must manually transcribe post-it notes before processing.

## Design Approach

- Extract text from workshop photos using vision LLM
- Parse post-it clusters into empathy map categories
- Support multiple images per workshop
- Allow manual correction of extracted text
- Preserve spatial relationships where meaningful

## Implementation Tasks

- [ ] Research vision LLM capabilities for post-it extraction
- [ ] Create `persona import-workshop <images>` command
- [ ] Implement image-to-text extraction
- [ ] Build post-it cluster detection
- [ ] Map clusters to empathy map categories
- [ ] Generate editable YAML for correction
- [ ] Support batch image processing
- [ ] Add confidence indicators for extractions
- [ ] Write integration tests

## Success Criteria

- [ ] Post-it text accurately extracted (>90% accuracy)
- [ ] Clusters correctly identified
- [ ] Manual correction workflow smooth
- [ ] Generates valid empathy map YAML
- [ ] Handles various photo qualities
- [ ] Test coverage ≥ 80%

## Dependencies

- F-029: Empathy map input format
- Vision-capable LLM (GPT-4V, Claude 3, Gemini Pro Vision)

---

## Related Documentation

- [UC-009: Empathy Mapping](../../../../use-cases/briefs/UC-009-empathy-mapping.md)
- [F-029: Empathy Map Input Format](F-029-empathy-map-input-format.md)
- [G-02: Preparing Research Data](../../../../guides/preparing-data.md)

