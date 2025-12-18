# F-043: Custom Vendor Configuration

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-008 |
| **Milestone** | v0.5.0 |
| **Priority** | P1 |
| **Category** | Config |

## Problem Statement

Enterprise users need to connect to custom LLM endpoints (Azure OpenAI, AWS Bedrock, private deployments). The current fixed vendor configuration doesn't support these use cases.

## Design Approach

- YAML-based vendor configuration
- Support custom API endpoints
- Configurable authentication methods
- Interactive setup wizard
- Validation before use

### Custom Vendor Schema

```yaml
# ~/.persona/vendors/azure-openai.yaml
id: azure-openai
name: Azure OpenAI
api_base: https://my-deployment.openai.azure.com
api_version: 2024-02-15-preview
auth_type: bearer
auth_env: AZURE_OPENAI_API_KEY
endpoints:
  chat: /openai/deployments/{deployment}/chat/completions
headers:
  api-key: ${AZURE_OPENAI_API_KEY}
```

## Implementation Tasks

- [ ] Design vendor configuration schema
- [ ] Create VendorLoader for custom YAML
- [ ] Implement authentication handlers
- [ ] Create `persona vendor add` wizard
- [ ] Add `persona vendor list` command
- [ ] Add `persona vendor test` command
- [ ] Validate vendor before first use
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Custom vendors load from YAML
- [ ] All auth types work (bearer, header, query)
- [ ] Wizard guides users through setup
- [ ] Invalid configs rejected with clear errors
- [ ] Test coverage ≥ 80%

## Dependencies

- F-002: LLM provider abstraction

---

## Related Documentation

- [Milestone v0.5.0](../../milestones/v0.5.0.md)
- [Configuration Reference](../../../../reference/configuration-reference.md)
