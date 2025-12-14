# Synthetic Test Data

This document describes the design, creation methodology, and usage of synthetic test data for Persona.

## Purpose

Synthetic test data enables:
- **Reproducible testing** without real user data
- **Privacy compliance** - no actual user information
- **Controlled scenarios** - predictable content for assertions
- **Edge case coverage** - intentionally crafted edge cases

## Ethics and Bias Mitigation

Synthetic test data must be created responsibly. This section documents our approach to ethical data generation.

### Core Principles

1. **No real personal data** - All content is entirely fictional
2. **No stereotyping** - Avoid associating traits with demographics
3. **Intentional diversity** - Represent varied perspectives
4. **Transparent limitations** - Document known gaps
5. **Regular review** - Audit data for emerging biases

### Bias Mitigation Strategies

#### What We Do

| Strategy | Implementation |
|----------|---------------|
| **Role diversity** | 10 distinct professional roles across tech functions |
| **Experience range** | 3-8 years, representing early-to-mid career |
| **Sentiment balance** | Mix of positive, mixed, and critical feedback |
| **No demographic stereotypes** | Use participant IDs, not gendered names |
| **No physical descriptions** | Focus on behaviours and goals, not appearance |
| **Platform diversity** | iOS, Web, Windows represented |
| **User type variety** | Power users, new users, administrators |

#### What We Intentionally Avoid

| Avoided Pattern | Reason |
|-----------------|--------|
| Gendered names | Prevents gender-role associations |
| Age indicators | Avoids age-based stereotyping |
| Ethnic/cultural markers | Prevents cultural assumptions |
| Physical descriptions | Not relevant to persona testing |
| Salary/income data | Prevents socioeconomic bias |
| Geographic specifics | Avoids regional stereotyping |

### Known Limitations

The current synthetic data has these documented limitations:

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Tech industry focus** | May not represent non-tech users | Acknowledged as test scope |
| **English-only** | No multilingual content | Document for future expansion |
| **Western context** | Work patterns assume Western norms | Acknowledge in documentation |
| **Mid-career bias** | Missing entry-level and senior perspectives | Note in data description |
| **Able-bodied assumptions** | No accessibility-related feedback | Add in future iterations |

### Diversity Audit

Current dataset representation:

**Professional Roles (10 unique):**
- Technical: Developer, DevOps, Security Engineer, QA Engineer
- Design: UX Designer
- Business: Product Manager, Marketing Manager
- Support: Customer Support Lead, Technical Writer
- Analysis: Data Analyst

**Experience Distribution:**
- 3 years: 2 participants (20%)
- 4 years: 2 participants (20%)
- 5 years: 3 participants (30%)
- 6 years: 1 participant (10%)
- 7 years: 1 participant (10%)
- 8 years: 1 participant (10%)

**Feedback Sentiment:**
- Very positive (5/5, 9-10 NPS): 2 responses (40%)
- Positive (4/5, 7-8 NPS): 2 responses (40%)
- Mixed (3/5, 5-6 NPS): 1 response (20%)
- Negative (1-2/5): 0 responses (0% - noted gap)

### Future Improvements

When expanding synthetic data:

1. **Add negative feedback** - Include 1-2/5 satisfaction responses
2. **Entry-level perspectives** - Add 0-2 years experience participants
3. **Senior perspectives** - Add 10+ years experience participants
4. **Accessibility feedback** - Include screen reader users, motor impairments
5. **Non-tech roles** - Healthcare, education, manufacturing contexts
6. **Multilingual hints** - Non-native English patterns (for v0.3.0+)

### Ethical Review Checklist

Before adding new synthetic data, verify:

- [ ] No real personal information included
- [ ] No stereotypical associations with demographics
- [ ] Diverse perspectives represented
- [ ] Limitations documented
- [ ] No potentially offensive content
- [ ] British English used consistently

---

## Design Principles

### 1. Realistic Content

Test data mimics real-world user research:
- Authentic-sounding interview transcripts
- Plausible survey responses with varied sentiment
- Diverse professional roles and experience levels
- Natural language patterns (not lorem ipsum)

### 2. Thematic Consistency

All synthetic data follows consistent themes enabling predictable persona generation:
- **Technology tools** - CLI preferences, automation needs
- **Documentation** - quality concerns, maintenance challenges
- **Collaboration** - team communication, stakeholder alignment
- **Workflow efficiency** - speed, consolidation, integration

### 3. Varied Complexity

Different dataset sizes for different test scenarios:
- **Small (3 records)** - Quick unit tests, CI speed
- **Medium (10 records)** - Realistic integration tests
- **Mixed formats** - Multi-format loading verification

### 4. Ethical by Design

All data follows bias mitigation principles:
- No demographic stereotyping
- Documented limitations
- Regular audit for biases
- Transparent about scope

---

## Dataset Inventory

### Interview Data (CSV)

#### interviews_small.csv

| Attribute | Value |
|-----------|-------|
| **Records** | 3 |
| **Columns** | 6 |
| **Use Case** | Quick tests, CI pipelines |
| **Location** | `tests/data/synthetic/interviews_small.csv` |

**Schema:**
```csv
participant_id,date,role,experience_years,transcript,key_themes
```

**Participants:**
| ID | Role | Experience | Key Themes |
|----|------|------------|------------|
| P001 | Software Developer | 5 years | CLI preference, documentation issues |
| P002 | UX Designer | 3 years | Visual feedback, speed, collaboration |
| P003 | Product Manager | 7 years | Feedback tracking, research synthesis |

**Sample Transcript:**
> "I primarily use command-line tools for my daily work. The main frustration is when documentation is outdated. I wish there was a single tool that could handle all my needs."

---

#### interviews_medium.csv

| Attribute | Value |
|-----------|-------|
| **Records** | 10 |
| **Columns** | 6 |
| **Use Case** | Realistic integration tests |
| **Location** | `tests/data/synthetic/interviews_medium.csv` |

**Participants:**
| ID | Role | Experience | Key Themes |
|----|------|------------|------------|
| P001 | Software Developer | 5 years | CLI preference, documentation |
| P002 | UX Designer | 3 years | Visual feedback, collaboration |
| P003 | Product Manager | 7 years | Feedback tracking, synthesis |
| P004 | Data Analyst | 4 years | Data quality, Python, reproducibility |
| P005 | DevOps Engineer | 6 years | Automation, security, CI/CD |
| P006 | Customer Support Lead | 5 years | Response time, customer history |
| P007 | Marketing Manager | 4 years | Analytics, attribution, real-time |
| P008 | Security Engineer | 8 years | Compliance, log analysis |
| P009 | Technical Writer | 3 years | Documentation sync, version control |
| P010 | QA Engineer | 5 years | Test coverage, reliability, test data |

---

### Survey Data (JSON)

#### survey_responses.json

| Attribute | Value |
|-----------|-------|
| **Records** | 5 |
| **Format** | JSON array |
| **Use Case** | JSON loading, structured data |
| **Location** | `tests/data/synthetic/survey_responses.json` |

**Schema:**
```json
{
  "survey_responses": [
    {
      "response_id": "R001",
      "timestamp": "2024-01-20T10:30:00Z",
      "satisfaction_score": 4,
      "likelihood_to_recommend": 8,
      "most_useful_feature": "string",
      "biggest_pain_point": "string",
      "open_feedback": "string"
    }
  ]
}
```

**Response Distribution:**
| ID | Satisfaction | NPS Score | Sentiment |
|----|--------------|-----------|-----------|
| R001 | 4/5 | 8 | Positive (mobile concerns) |
| R002 | 5/5 | 10 | Very positive (setup learning curve) |
| R003 | 3/5 | 5 | Mixed (pricing concerns) |
| R004 | 4/5 | 7 | Positive (documentation gaps) |
| R005 | 5/5 | 9 | Very positive (offline needs) |

---

### Feedback Data (Markdown)

#### user_feedback.md

| Attribute | Value |
|-----------|-------|
| **Entries** | 3 |
| **Format** | Structured Markdown |
| **Use Case** | Markdown parsing, unstructured data |
| **Location** | `tests/data/synthetic/user_feedback.md` |

**Structure per entry:**
```markdown
## User Feedback: [Topic]

**Date:** YYYY-MM-DD
**User Type:** [Type]
**Platform:** [Platform]

### Summary
[Brief description]

### Key Points
- Point 1
- Point 2
- Point 3

### User Quote
> "[Direct quote]"
```

**Entries:**
| Topic | User Type | Platform | Key Theme |
|-------|-----------|----------|-----------|
| Mobile App Experience | Power User | iOS | Feature parity |
| Onboarding Experience | New User | Web | Information overload |
| Team Collaboration | Team Admin | Windows | Permission management |

---

### Mixed Format Directory

#### mixed_format/

| Attribute | Value |
|-----------|-------|
| **Files** | 3 |
| **Formats** | CSV, JSON, Markdown |
| **Use Case** | Multi-format loading tests |
| **Location** | `tests/data/synthetic/mixed_format/` |

**Contents:**
| File | Format | Records | Purpose |
|------|--------|---------|---------|
| `interviews.csv` | CSV | 2 | Minimal CSV |
| `survey.json` | JSON | 2 | Minimal JSON |
| `feedback.md` | Markdown | 1 | Minimal Markdown |

These are intentionally minimal for testing format detection and aggregation.

---

## Generation Methodology

### Static Files

All synthetic data is hand-crafted and committed to the repository. This ensures:
- **Reproducibility** - Same data across all environments
- **Stability** - No generation drift over time
- **Review** - Data can be audited for quality

### Programmatic Generation

For tests requiring dynamic data, use `tests/fixtures/data_samples.py`:

```python
from tests.fixtures.data_samples import (
    generate_interview_csv,
    generate_survey_json,
    generate_feedback_markdown,
    write_synthetic_data_files,
)

# Generate CSV string
csv_content = generate_interview_csv(num_interviews=5)

# Generate JSON string
json_content = generate_survey_json(num_responses=10)

# Generate Markdown string
md_content = generate_feedback_markdown(num_entries=3)

# Write all files to directory
files = write_synthetic_data_files(Path("./test_output"))
```

### When to Use Each Approach

| Scenario | Approach |
|----------|----------|
| Standard tests | Static files |
| Parameterised tests | Programmatic generation |
| Edge case testing | Custom hand-crafted data |
| Performance testing | Programmatic (large datasets) |

---

## Expected Outputs

### Persona Schema

When generating personas from the synthetic data, expect output matching this schema:

```json
{
  "id": "persona-001",
  "name": "Alex Chen",
  "demographics": {
    "age_range": "25-34",
    "occupation": "Software Developer",
    "experience_level": "Mid-level",
    "location": "Urban tech hub"
  },
  "goals": [
    "Streamline daily workflow with efficient tools",
    "Stay current with technology best practices"
  ],
  "pain_points": [
    "Outdated documentation wastes valuable time",
    "Too many tools required for basic tasks"
  ],
  "behaviours": [
    "Prefers keyboard shortcuts and CLI over GUI",
    "Reads documentation before trying new tools"
  ],
  "quotes": [
    "I just want things to work without friction."
  ]
}
```

See `tests/data/expected_outputs/persona_schema_valid.json` for the canonical example.

---

## Theme Reference

All synthetic data intentionally includes these themes to enable predictable persona generation:

### Primary Themes

| Theme | Description | Keywords |
|-------|-------------|----------|
| **Tool Efficiency** | Desire for streamlined workflows | consolidation, single tool, friction |
| **Documentation** | Quality and maintenance concerns | outdated, gaps, sync |
| **Collaboration** | Team communication challenges | stakeholders, permissions, feedback |
| **Automation** | Repetitive task reduction | scripts, CI/CD, integration |

### Secondary Themes

| Theme | Description | Source Data |
|-------|-------------|-------------|
| Mobile experience | Platform parity concerns | Survey, Feedback |
| Onboarding | New user experience | Survey, Feedback |
| Pricing | Cost for small teams | Survey |
| Speed | Performance concerns | Survey, Interviews |

---

## Adding New Test Data

When adding new synthetic data:

1. **Follow existing patterns** - Match schema and style of existing files
2. **Use British English** - Consistent with project standards
3. **Include diverse perspectives** - Multiple roles, experience levels
4. **Document in this file** - Update inventory and metadata
5. **Keep it realistic** - Authentic-sounding, not lorem ipsum

### Checklist for New Data

- [ ] Follows existing schema/format
- [ ] Contains realistic, diverse content
- [ ] Uses British English spelling
- [ ] Added to inventory in this document
- [ ] Tested with data loading functions

---

## Related Documentation

- [Testing Guide](README.md) - Main testing documentation
- [Test Fixtures](../../../tests/fixtures/README.md) - Fixture reference
- [Data Samples Module](../../../tests/fixtures/data_samples.py) - Generation code
