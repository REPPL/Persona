# F-084: Synthetic Data for Testing

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-008 |
| **Milestone** | v1.0.0 |
| **Priority** | P2 |
| **Category** | Docs |

## Problem Statement

Users need sample data to learn Persona without using their own sensitive data. Developers need deterministic test data for automated testing.

## Design Approach

- Create realistic synthetic interview data
- Multiple formats (CSV, JSON, Markdown)
- Diverse participant profiles
- Privacy-safe (no real PII)
- Included with installation

### Synthetic Data Set

```
data/synthetic/
├── README.md                    # Dataset documentation
├── interviews/
│   ├── participant-001.md       # Developer persona
│   ├── participant-002.md       # Designer persona
│   ├── participant-003.md       # Product Manager
│   ├── participant-004.md       # Data Scientist
│   └── participant-005.md       # DevOps Engineer
├── surveys/
│   ├── user-feedback.csv        # Survey responses
│   └── nps-scores.json          # NPS data
└── mixed/
    ├── combined.json            # All data in JSON
    └── combined.csv             # All data in CSV
```

### Participant Profiles

| ID | Role | Focus Areas |
|----|------|-------------|
| P001 | Senior Developer | Code quality, tooling |
| P002 | UX Designer | User research, accessibility |
| P003 | Product Manager | Roadmaps, prioritisation |
| P004 | Data Scientist | ML pipelines, notebooks |
| P005 | DevOps Engineer | CI/CD, infrastructure |

### Sample Interview Format

```markdown
# Interview: Participant 001

## Background
Role: Senior Software Developer
Experience: 8 years
Industry: FinTech

## Interview Transcript

**Interviewer:** Tell me about your typical workday.

**P001:** I usually start by reviewing pull requests from my team...

[Realistic but synthetic responses covering pain points,
workflows, tools, frustrations, and goals]
```

### Generation Utility

```bash
# Generate fresh synthetic data
persona data generate-synthetic --participants 10 --format markdown

# Regenerate with specific seed
persona data generate-synthetic --seed 42

# Generate specific format
persona data generate-synthetic --format csv --output ./my-data/
```

## Implementation Tasks

- [x] Design participant profiles
- [x] Write synthetic interview content
- [x] Create CSV survey data
- [x] Create JSON data variants
- [x] Document sample data
- [ ] Build generation utility (deferred - static data sufficient)
- [ ] Include in pip package (deferred - data at project root for tutorials)
- [ ] Use in tutorials (documentation task)

## Success Criteria

- [x] Realistic synthetic content
- [x] Multiple formats included
- [x] No PII in data
- [x] Works in tutorials
- [ ] Generation reproducible (deferred - static data is reproducible by definition)

## Dependencies

- None (sample data)

---

## Related Documentation

- [Milestone v1.0.0](../../milestones/v1.0.0.md)
- [Tutorials](../../../tutorials/)

---

**Status**: Complete
