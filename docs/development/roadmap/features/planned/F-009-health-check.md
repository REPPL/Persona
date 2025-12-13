# F-009: Health Check

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003 |
| **Milestone** | v0.1.0 |
| **Priority** | P1 |
| **Category** | CLI |

## Problem Statement

Users need to verify installation and configuration before running generation.

## Design Approach

- Check each configured provider
- Validate API key presence (without exposing)
- List available models
- Clear pass/fail output with Rich

## Implementation Tasks

- [ ] Create HealthChecker class
- [ ] Implement provider connectivity check
- [ ] Add API key validation
- [ ] Add model availability check
- [ ] Create `check` command
- [ ] Add helpful suggestions for failures
- [ ] Write unit tests

## Success Criteria

- [ ] All configured providers checked
- [ ] Clear indication of issues
- [ ] Helpful suggestions for fixes
- [ ] Non-zero exit code on failure
- [ ] API keys never exposed
- [ ] Test coverage ≥ 80%

## Output Example

```
$ persona check

System Check
───────────────────────────────────
Python      ✓ 3.12.0
Config      ✓ Valid

Providers
───────────────────────────────────
OpenAI      ✓ API key configured
            ✓ Models: gpt-4, gpt-4o
Anthropic   ✓ API key configured
            ✓ Models: claude-3-opus, claude-3-sonnet
Gemini      ✗ API key not found
            → Set GEMINI_API_KEY environment variable

Status: 2/3 providers ready
```

---

## Related Documentation

- [UC-003: View Status](../../../../use-cases/briefs/UC-003-view-status.md)
- [F-008: CLI Interface](F-008-cli-interface.md)
