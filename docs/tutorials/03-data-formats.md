# Working with Different Data Formats

Learn how to prepare data in each format supported by Persona.

**Level:** Beginner | **Time:** 15 minutes

## What You'll Learn

- Supported file formats (CSV, JSON, Markdown, YAML, TXT)
- Best practices for each format
- How to structure research data
- Common mistakes to avoid

## Prerequisites

- Completed [Getting Started](01-getting-started.md)
- Sample research data to work with

## Supported Formats

Persona supports these file formats:

| Format | Best For | File Extension |
|--------|----------|----------------|
| CSV | Survey responses, tabular data | `.csv` |
| JSON | Structured interviews, API data | `.json` |
| Markdown | Interview transcripts, notes | `.md` |
| YAML | Structured research notes | `.yaml`, `.yml` |
| TXT | Raw notes, observations | `.txt` |

## CSV: Survey Responses

**Best for:** Structured feedback, survey data, user testing results

### Structure

```csv
respondent_id,feedback,sentiment,category
1,"The mobile app is great for quick tasks",positive,mobile
2,"Too many features, hard to find things",negative,navigation
3,"Love the dark mode option",positive,ui
4,"Wish there was offline support",neutral,mobile
5,"Customer support is excellent",positive,support
```

### Best Practices

- **Include headers** - First row should be column names
- **Quote text fields** - Wrap text in double quotes
- **One response per row** - Don't merge multiple responses
- **Use consistent categories** - Same values for same meanings

### Common Mistakes

```csv
# BAD: No headers
1,The app is great,positive

# BAD: Unquoted text with commas
1,The app is great, but needs work,positive

# GOOD: Proper structure
respondent_id,feedback,sentiment
1,"The app is great, but needs work",positive
```

## JSON: Structured Interviews

**Best for:** Interview transcripts, structured notes, API exports

### Structure

```json
{
  "interviews": [
    {
      "participant_id": "P001",
      "date": "2024-12-10",
      "demographics": {
        "role": "Product Manager",
        "experience": "5 years"
      },
      "responses": [
        {
          "question": "How do you typically use the product?",
          "answer": "I use it daily for team coordination. Mostly the dashboard and reporting features."
        },
        {
          "question": "What frustrates you most?",
          "answer": "The export function is clunky. Takes too many clicks."
        }
      ]
    },
    {
      "participant_id": "P002",
      "date": "2024-12-11",
      "demographics": {
        "role": "Developer",
        "experience": "3 years"
      },
      "responses": [
        {
          "question": "How do you typically use the product?",
          "answer": "Mainly for API integration. The documentation could be better."
        }
      ]
    }
  ]
}
```

### Best Practices

- **Consistent structure** - Same fields for each participant
- **Clear nesting** - Group related data logically
- **Descriptive keys** - `responses` not `r` or `data`
- **Valid JSON** - Use a validator before processing

### Common Mistakes

```json
// BAD: Inconsistent structure
{
  "interviews": [
    {"id": 1, "feedback": "Great product"},
    {"participant": "P002", "response": "Needs work"}
  ]
}

// GOOD: Consistent structure
{
  "interviews": [
    {"participant_id": "P001", "feedback": "Great product"},
    {"participant_id": "P002", "feedback": "Needs work"}
  ]
}
```

## Markdown: Interview Transcripts

**Best for:** Long-form transcripts, qualitative notes, research reports

### Structure

```markdown
# Interview: P001 - Sarah

**Date:** 2024-12-10
**Role:** Marketing Manager
**Experience:** 5 years

## Background

Sarah has been using the product for 2 years. She primarily uses
the dashboard and reporting features.

## Key Quotes

> "I check the dashboard every morning before standup. It's become
> part of my routine."

> "The export function drives me crazy. Why can't I just click once
> and get a PDF?"

## Observations

- Very confident with technology
- Frustrated by multi-step processes
- Values efficiency over features

---

# Interview: P002 - James

**Date:** 2024-12-11
**Role:** Developer
**Experience:** 3 years

## Background

James integrates with the API for automated reporting.

## Key Quotes

> "The API documentation is outdated. I had to figure out half
> the endpoints myself."

## Observations

- Technical user
- Prefers self-service over support
- Documentation is critical for this user type
```

### Best Practices

- **Use headings** - Structure with `#`, `##`, `###`
- **Include metadata** - Date, role, context
- **Quote key statements** - Use `>` for quotes
- **Separate interviews** - Use `---` between entries

### Common Mistakes

```markdown
# BAD: No structure
sarah said the app is good but export is bad
james wants better docs

# GOOD: Structured content
# Interview: Sarah

## Key Feedback
> "Export is cumbersome, needs improvement"
```

## YAML: Structured Research Notes

**Best for:** Organised research notes, empathy maps, structured observations

### Structure

```yaml
research_session:
  date: 2024-12-10
  method: "User interview"

participants:
  - id: P001
    name: Sarah
    role: Marketing Manager
    observations:
      - "Very efficient with keyboard shortcuts"
      - "Gets frustrated with modal dialogs"
    pain_points:
      - "Export takes too many steps"
      - "Can't customise dashboard"
    goals:
      - "Quick daily check-ins"
      - "Easy reporting to stakeholders"

  - id: P002
    name: James
    role: Developer
    observations:
      - "Uses API exclusively"
      - "Rarely uses web interface"
    pain_points:
      - "Outdated documentation"
      - "Rate limiting on API"
    goals:
      - "Automated reporting"
      - "Integration with CI/CD"
```

### Best Practices

- **Consistent indentation** - Use 2 spaces (not tabs)
- **Quote special characters** - Wrap text with `:` or `#`
- **Use lists** - Arrays with `-` for multiple items
- **Group logically** - Related data nested together

## TXT: Raw Notes

**Best for:** Quick observations, unstructured notes, field research

### Structure

```
User Testing Session - 2024-12-10

Participant 1 (Sarah, Marketing)
- Took 45 seconds to find export button
- Said "why is this so hidden?"
- Completed task on second attempt
- Frustrated with number of clicks

Participant 2 (James, Developer)
- Ignored UI, went straight to API docs
- Spent 10 minutes finding right endpoint
- Quote: "This documentation is from 2022"
- Eventually succeeded with trial and error

General Observations:
- Power users skip the UI
- New users struggle with navigation
- Export is universally problematic
```

### Best Practices

- **Add structure where possible** - Headers, bullet points
- **Include context** - Date, session type, who
- **Capture quotes verbatim** - Mark with "Quote:" or quotation marks
- **Group observations** - By participant or theme

## Combining Multiple Files

You can mix formats in your data directory:

```
experiments/my-experiment/data/
├── survey-results.csv         # Quantitative feedback
├── interview-transcripts.md   # Qualitative interviews
├── field-notes.txt            # Observation notes
└── empathy-maps.yaml          # Structured analysis
```

Persona combines all files, adding clear separators:

```
=== FILE: survey-results.csv ===
[content]

=== FILE: interview-transcripts.md ===
[content]
```

## Preview Before Processing

Always preview your data before running generation:

```bash
persona preview experiments/my-experiment/data/
```

**Output:**

```
Data Preview
───────────────────────────────────
Files detected: 4
Total tokens: ~3,500
Estimated cost: $0.12

File Breakdown:
  survey-results.csv      1,200 tokens
  interview-transcripts.md 1,800 tokens
  field-notes.txt           300 tokens
  empathy-maps.yaml         200 tokens

Sample content:
  "I check the dashboard every morning..."
  "Export takes too many steps..."
```

## What's Next?

Now that you understand data formats:

1. **[Comparing Providers](04-comparing-providers.md)** - Test with different models
2. **[Building a Library](05-building-library.md)** - Organise multiple projects
3. **[Validating Quality](06-validating-quality.md)** - Ensure accuracy

---

## Related Documentation

- [F-001: Data Loading](../development/roadmap/features/completed/F-001-data-loading.md)
- [F-029: Empathy Map Input](../development/roadmap/features/completed/F-029-empathy-map-input-format.md)
- [G-02: Preparing Data](../guides/preparing-data.md)
