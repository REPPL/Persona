# Running Persona in CI/CD Pipelines

An advanced guide to automating persona generation and validation in continuous integration workflows.

## Goal

Integrate Persona into your CI/CD pipeline to automatically generate, validate, and update personas as part of your development workflow.

## Prerequisites

- CI/CD platform (GitHub Actions, GitLab CI, Jenkins, etc.)
- Secure secrets management for API keys
- Understanding of [CLI commands](../reference/cli-reference.md)

## Use Cases

| Scenario | Automation Value |
|----------|------------------|
| Research data updated | Auto-regenerate personas |
| PR with data changes | Validate data quality |
| Weekly refresh | Keep personas current |
| Multi-environment | Different personas per stage |
| Quality gates | Block on validation failure |

## GitHub Actions Example

### Basic Workflow

```yaml
# .github/workflows/persona-generation.yml
name: Generate Personas

on:
  push:
    paths:
      - 'research/data/**'
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 1'  # Weekly Monday

jobs:
  generate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Persona
        run: |
          pip install persona-cli

      - name: Generate Personas
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          persona generate \
            --from research/data/ \
            --output research/personas/ \
            --format json \
            --no-confirm

      - name: Commit Generated Personas
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: regenerate personas from latest data"
          file_pattern: 'research/personas/**'
```

### Validation Workflow

```yaml
# .github/workflows/persona-validation.yml
name: Validate Personas

on:
  pull_request:
    paths:
      - 'research/data/**'
      - 'research/personas/**'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Persona
        run: pip install persona-cli

      - name: Validate Data Quality
        run: |
          persona data validate research/data/ --strict

      - name: Validate Personas
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          persona validate --all \
            --source research/data/ \
            --threshold 80 \
            --output validation-report.md

      - name: Comment Validation Report
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('validation-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

## GitLab CI Example

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - generate
  - publish

variables:
  PYTHON_VERSION: "3.12"

validate-data:
  stage: validate
  image: python:${PYTHON_VERSION}
  script:
    - pip install persona-cli
    - persona data validate research/data/ --strict
  rules:
    - changes:
        - research/data/**

generate-personas:
  stage: generate
  image: python:${PYTHON_VERSION}
  script:
    - pip install persona-cli
    - persona generate --from research/data/ --output research/personas/ --no-confirm
  artifacts:
    paths:
      - research/personas/
    expire_in: 1 week
  rules:
    - changes:
        - research/data/**
  variables:
    ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}

publish-personas:
  stage: publish
  script:
    - |
      git config user.name "CI Bot"
      git config user.email "ci@example.com"
      git add research/personas/
      git commit -m "chore: regenerate personas" || exit 0
      git push origin HEAD:${CI_COMMIT_REF_NAME}
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

## Environment Configuration

### Secrets Management

**GitHub Actions:**
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

**GitLab CI:**
```yaml
variables:
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}  # Set in CI/CD Settings
```

**Jenkins:**
```groovy
environment {
    ANTHROPIC_API_KEY = credentials('anthropic-api-key')
}
```

### Provider Selection by Environment

```yaml
# Different providers for different environments
jobs:
  generate-dev:
    env:
      PERSONA_PROVIDER: anthropic
      PERSONA_MODEL: claude-3-haiku  # Cheaper for dev

  generate-prod:
    env:
      PERSONA_PROVIDER: anthropic
      PERSONA_MODEL: claude-3-sonnet  # Higher quality for prod
```

## JSON Output for Downstream Tools

### Generate Structured Output

```bash
persona generate \
  --from research/data/ \
  --format json \
  --output personas.json \
  --no-confirm
```

### Parse in Pipeline

```yaml
- name: Process Personas
  run: |
    # Extract persona names for notification
    PERSONAS=$(jq -r '.personas[].name' personas.json | tr '\n' ', ')
    echo "Generated personas: $PERSONAS"

    # Count personas
    COUNT=$(jq '.personas | length' personas.json)
    echo "Total: $COUNT personas"
```

## Cost Monitoring

### Track Generation Costs

```yaml
- name: Generate with Cost Tracking
  run: |
    persona generate \
      --from research/data/ \
      --output personas/ \
      --no-confirm \
      --cost-report cost.json

    COST=$(jq '.total' cost.json)
    echo "Generation cost: \$$COST"

    # Fail if cost exceeds budget
    if (( $(echo "$COST > 5.00" | bc -l) )); then
      echo "Cost exceeded budget!"
      exit 1
    fi
```

### Monthly Cost Aggregation

```yaml
- name: Update Cost Log
  run: |
    DATE=$(date +%Y-%m)
    COST=$(jq '.total' cost.json)
    echo "$DATE,$COST" >> costs/monthly.csv

    # Calculate monthly total
    MONTHLY=$(awk -F',' -v month="$DATE" '$1==month {sum+=$2} END {print sum}' costs/monthly.csv)
    echo "Monthly total: \$$MONTHLY"
```

## Regression Testing

### Compare Against Baseline

```yaml
- name: Check for Persona Drift
  run: |
    # Generate new personas
    persona generate --from research/data/ --output new/

    # Compare with baseline
    persona compare \
      --baseline research/personas/baseline/ \
      --current new/ \
      --threshold 70 \
      --output comparison.json

    # Check similarity
    SIMILARITY=$(jq '.average_similarity' comparison.json)
    if (( $(echo "$SIMILARITY < 70" | bc -l) )); then
      echo "Warning: Significant persona drift detected"
      cat comparison.json
    fi
```

### Update Baseline

```yaml
- name: Update Baseline (manual trigger)
  if: github.event_name == 'workflow_dispatch'
  run: |
    cp -r new/* research/personas/baseline/
    git add research/personas/baseline/
    git commit -m "chore: update persona baseline"
```

## Notifications

### Slack Notification

```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Personas regenerated",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Persona Generation Complete*\n• Count: ${{ env.PERSONA_COUNT }}\n• Cost: ${{ env.GENERATION_COST }}\n• <${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run>"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Email Report

```yaml
- name: Email Report
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.example.com
    username: ${{ secrets.MAIL_USERNAME }}
    password: ${{ secrets.MAIL_PASSWORD }}
    subject: "Persona Generation Report - ${{ github.run_id }}"
    body: file://validation-report.md
    to: research-team@example.com
    from: ci@example.com
```

## Error Handling

### Graceful Failure

```yaml
- name: Generate Personas
  id: generate
  continue-on-error: true
  run: |
    persona generate --from research/data/ --output new/

- name: Handle Failure
  if: steps.generate.outcome == 'failure'
  run: |
    echo "Generation failed, using cached personas"
    cp -r research/personas/cache/* research/personas/current/
```

### Retry Logic

```yaml
- name: Generate with Retry
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 60
    command: |
      persona generate \
        --from research/data/ \
        --output new/ \
        --no-confirm
```

## Best Practices

### Do

- Store API keys securely (never in code)
- Use `--no-confirm` for unattended runs
- Set cost budgets and alerts
- Cache generated personas for fallback
- Use appropriate models per environment
- Log all generation metadata

### Don't

- Commit API keys to repository
- Generate on every commit (use path filters)
- Skip validation in production pipelines
- Ignore cost overruns
- Use expensive models for development

## Verification

Test your pipeline locally:

```bash
# Simulate CI environment
export CI=true
export ANTHROPIC_API_KEY="your-key"

# Run generation command
persona generate \
  --from research/data/ \
  --output test-output/ \
  --format json \
  --no-confirm

# Verify output
ls test-output/
cat test-output/metadata.json
```

---

## Related Documentation

- [CLI Reference](../reference/cli-reference.md)
- [F-020: Batch Processing](../development/roadmap/features/completed/F-020-batch-data-processing.md)
- [Reproducibility](../explanation/reproducibility.md)

