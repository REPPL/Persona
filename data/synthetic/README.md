# Synthetic Test Data

This directory contains synthetic interview and survey data for learning Persona.

**Important:** All data in this directory is fictional and generated for demonstration purposes. No real personally identifiable information (PII) is included.

## Contents

### Interviews (`interviews/`)

Five synthetic user research interviews covering different professional roles:

| File | Role | Focus Areas |
|------|------|-------------|
| participant-001.md | Senior Developer | Code quality, tooling, workflows |
| participant-002.md | UX Designer | User research, accessibility, design systems |
| participant-003.md | Product Manager | Roadmaps, prioritisation, stakeholder management |
| participant-004.md | Data Scientist | ML pipelines, notebooks, data quality |
| participant-005.md | DevOps Engineer | CI/CD, infrastructure, monitoring |

### Surveys (`surveys/`)

- `user-feedback.csv` - Structured survey responses from 20 participants
- `nps-scores.json` - Net Promoter Score data with verbatim comments

### Mixed (`mixed/`)

- `combined.json` - All interview data in JSON format
- `combined.csv` - All survey data consolidated

## Usage

```bash
# Generate personas from interview data
persona generate --from data/synthetic/interviews/ --count 3

# Generate from survey data
persona generate --from data/synthetic/surveys/user-feedback.csv --count 3

# Preview data before generation
persona preview --from data/synthetic/interviews/
```

## Generating Fresh Synthetic Data

You can regenerate synthetic data with different seeds:

```bash
# Generate with default seed
persona data generate-synthetic

# Generate with specific seed (for reproducibility)
persona data generate-synthetic --seed 42
```

## Data Format Guidelines

### Interview Format (Markdown)

```markdown
# Interview: Participant ID

## Background
Role: <job title>
Experience: <years> years
Industry: <industry>

## Interview Transcript

**Interviewer:** <question>

**Participant:** <response>
```

### Survey Format (CSV)

```csv
participant_id,role,years_experience,satisfaction_score,biggest_challenge,feature_request
P001,Developer,5,4,"Managing dependencies","Better IDE integration"
```
