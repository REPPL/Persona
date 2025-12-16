# Demo Project

A demonstration project with synthetic research data for learning Persona.

## Contents

- **data/interviews.csv** - Synthetic developer interview transcripts
- **data/survey-responses.json** - Synthetic survey responses

## Quick Start

```bash
# From the demo-project directory:
cd examples/demo-project

# Generate personas from interview data
persona generate --from data/interviews.csv

# Generate personas from survey data
persona generate --from data/survey-responses.json

# Generate with a specific provider
persona generate --from data/interviews.csv --provider ollama --model llama3:8b
```

## Sample Data Overview

### Interviews (interviews.csv)

5 participants across different roles:
- Software Engineer (5 years)
- Product Manager (8 years)
- UX Designer (3 years)
- Data Scientist (4 years)
- DevOps Engineer (6 years)

Each participant has 2 quotes covering pain points and daily workflows.

### Survey Responses (survey-responses.json)

5 developer survey responses including:
- Role and experience
- Satisfaction scores
- Biggest challenges
- Tool preferences
- Improvement suggestions

## Expected Output

Persona will generate evidence-linked personas based on your data. Each persona will include:
- Demographics (name, role, experience)
- Goals and motivations
- Pain points and frustrations
- Quotes from the source data

Output files will be saved to the `output/` directory.
