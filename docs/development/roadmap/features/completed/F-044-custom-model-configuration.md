# F-044: Custom Model Configuration

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-008 |
| **Milestone** | v0.5.0 |
| **Priority** | P1 |
| **Category** | Config |

## Problem Statement

New models are released frequently, and enterprises deploy custom fine-tuned models. Users need to add model configurations without waiting for Persona updates.

## Design Approach

- YAML-based model configuration
- Inherit from vendor defaults
- Define pricing, limits, capabilities
- Support for fine-tuned model IDs

### Custom Model Schema

```yaml
# ~/.persona/models/my-finetuned.yaml
id: my-finetuned-gpt4
name: Fine-tuned GPT-4 for Personas
provider: azure-openai
base_model: gpt-4
context_window: 128000
max_output: 8192
pricing:
  input: 5.00
  output: 15.00
capabilities:
  structured_output: true
  vision: false
```

## Implementation Tasks

- [ ] Design model configuration schema
- [ ] Create ModelLoader for custom YAML
- [ ] Implement inheritance from vendor
- [ ] Create `persona model add` wizard
- [ ] Add `persona model list` command
- [ ] Validate model availability on add
- [ ] Update cost estimation
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Custom models load from YAML
- [ ] Pricing calculations accurate
- [ ] New models usable immediately
- [ ] Invalid configs rejected
- [ ] Test coverage ≥ 80%

## Dependencies

- F-043: Custom vendor configuration
- F-007: Cost estimation

---

## Related Documentation

- [Milestone v0.5.0](../../milestones/v0.5.0.md)
- [Model Cards](../../../../reference/model-cards.md)
