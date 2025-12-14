# v0.1.0 Scope Definition

Detailed scope for the v0.1.0 Foundation release.

## Included Features

| ID | Feature | Category | Priority |
|----|---------|----------|----------|
| F-001 | Multi-format data loading | Data | P0 |
| F-002 | LLM provider abstraction | LLM | P0 |
| F-003 | Prompt templating (Jinja2) | Prompts | P0 |
| F-004 | Persona generation pipeline | Generation | P0 |
| F-005 | Output formatting | Output | P0 |
| F-006 | Experiment management | Experiments | P0 |
| F-007 | Cost estimation | Cost | P0 |
| F-008 | CLI interface | CLI | P0 |
| F-009 | Health check command | CLI | P0 |
| F-010 | Data format normalisation | Data | P0 |
| F-011 | Multi-provider LLM support | LLM | P0 |
| F-012 | Experiment configuration (YAML) | Experiments | P0 |
| F-013 | Timestamped output folders | Output | P0 |
| F-014 | Model-specific pricing | Cost | P0 |
| F-015 | CLI core commands | CLI | P0 |
| F-016 | Interactive Rich UI | CLI | P0 |
| F-017 | Single-step workflow | Workflow | P1 |
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
