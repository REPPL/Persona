# v0.1.0 Scope Definition

Detailed scope for the v0.1.0 Foundation release.

## Included Features

| ID | Feature | Category | Priority |
|----|---------|----------|----------|
| F-001 | Multi-format data loading | Data | P0 |
| F-002 | Data format normalisation | Data | P0 |
| F-003 | Multi-provider LLM support | LLM | P0 |
| F-004 | Provider interface abstraction | LLM | P0 |
| F-005 | Reusable prompt templates | Prompts | P0 |
| F-006 | Single-step workflow | Workflow | P0 |
| F-007 | Basic persona extraction | Generation | P0 |
| F-008 | Structured JSON output | Output | P0 |
| F-009 | Timestamped output folders | Output | P0 |
| F-010 | Create/list/show/delete experiments | Experiments | P0 |
| F-011 | Experiment configuration (YAML) | Experiments | P0 |
| F-012 | Experiment directory structure | Experiments | P0 |
| F-013 | Cost estimation before generation | Cost | P0 |
| F-014 | Model-specific pricing | Cost | P0 |
| F-015 | CLI core commands | CLI | P0 |
| F-016 | Interactive Rich UI | CLI | P0 |
| F-017 | System check command | CLI | P1 |
| F-018 | Context-aware help | CLI | P1 |

## Explicitly Excluded

| Feature | Deferred To | Reason |
|---------|-------------|--------|
| Multi-step workflows | v0.2.0 | Foundation must be stable |
| Multi-variation generation | v0.3.0 | Depends on workflows |
| Custom configuration wizards | v0.5.0 | Extensibility phase |
| Security hardening | v0.6.0 | Dedicated security phase |

## Dependencies

- Python 3.12+
- LLM provider API key (at least one)
- Internet connectivity for API calls

## Release Criteria

- [ ] All P0 features implemented and tested
- [ ] P1 features implemented or documented as known limitations
- [ ] Test coverage ≥ 80%
- [ ] Getting Started tutorial complete
- [ ] All ADRs documented
- [ ] PersonaZero analysis complete
- [ ] Documentation audit passed

---

## Related Documentation

- [v0.1.0 Vision](../../vision/v0.1-vision.md)
- [v0.1.0 Milestone](../../../roadmap/milestones/v0.1.0.md)
- [Feature Specifications](../../../roadmap/features/)
