# F-042: Full LLM Response Capture

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-007 |
| **Milestone** | v0.4.0 |
| **Priority** | P1 |
| **Category** | Output |

## Problem Statement

For debugging, auditing, and research purposes, users need access to the complete LLM response including any metadata, usage statistics, and raw output before parsing. Partial captures make troubleshooting difficult.

## Design Approach

- Capture complete raw LLM response
- Store in structured format
- Include all metadata (tokens, latency, model info)
- Separate from parsed output
- Enable response replay for testing

### Captured Data

| Field | Description |
|-------|-------------|
| `raw_response` | Complete API response body |
| `request` | Request sent to API |
| `model` | Model ID used |
| `tokens.input` | Input token count |
| `tokens.output` | Output token count |
| `latency_ms` | Response time |
| `timestamp` | ISO 8601 timestamp |
| `provider` | Provider name |

## Implementation Tasks

- [ ] Create ResponseCapture class
- [ ] Implement provider-specific capture
- [ ] Store as full_response.json
- [ ] Add token and latency tracking
- [ ] Enable response replay mode
- [ ] Add `--capture-response` CLI option (default on)
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Complete response captured for all providers
- [ ] Replay mode reproduces parsing
- [ ] Minimal performance overhead
- [ ] Storage size reasonable
- [ ] Test coverage ≥ 80%

## Dependencies

- F-002: LLM provider abstraction
- F-013: Timestamped output folders

---

## Related Documentation

- [Milestone v0.4.0](../../milestones/v0.4.0.md)
- [F-032: Reasoning Capture](F-032-reasoning-capture.md)
