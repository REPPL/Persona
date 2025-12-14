# Preparing Research Data for Persona Generation

A practical guide to cleaning, structuring, and optimising your research data for persona generation.

## Goal

Prepare your research data in a format that produces high-quality, accurate personas while minimising API costs.

## Prerequisites

- Research data (interviews, surveys, observations)
- Understanding of [supported formats](../tutorials/03-data-formats.md)
- Text editor or spreadsheet software

## Data Preparation Checklist

Before processing your data:

- [ ] Data is anonymised (no real names, emails, IDs)
- [ ] Text is in a supported format (CSV, JSON, Markdown, YAML, TXT)
- [ ] Encoding is UTF-8
- [ ] Content is meaningful (not mostly empty)
- [ ] Duplicates are removed
- [ ] Quality is consistent across sources

## Step 1: Anonymisation

**Critical:** Remove all personally identifiable information.

### What to Anonymise

| PII Type | Example | Replacement |
|----------|---------|-------------|
| Names | "John Smith said..." | "P001 said..." |
| Emails | john@company.com | [email removed] |
| Phone numbers | 555-1234 | [phone removed] |
| Addresses | "123 Main Street" | [location removed] |
| Company names | "I work at Acme Corp" | "I work at [company]" |
| Dates | "On March 15th..." | "In Q1..." |

### Anonymisation Script

```python
import re

def anonymise(text):
    # Replace email addresses
    text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[email]', text)

    # Replace phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[phone]', text)

    # Replace common name patterns (basic)
    # Recommend manual review for names

    return text
```

### Manual Review

Always manually review anonymised data:
1. Search for proper nouns
2. Check for identifying context clues
3. Verify participant IDs are consistent

## Step 2: Format Selection

Choose the best format for your data:

| Data Type | Recommended Format | Why |
|-----------|-------------------|-----|
| Survey responses | CSV | Structured, easy to process |
| Interview transcripts | Markdown | Preserves structure, quotes |
| Observation notes | TXT | Flexible, no structure needed |
| Empathy maps | YAML | Hierarchical, category-based |
| API exports | JSON | Already structured |

## Step 3: Data Cleaning

### Common Issues and Fixes

| Issue | Example | Fix |
|-------|---------|-----|
| Encoding errors | Ã© instead of é | Convert to UTF-8 |
| Empty rows | Blank CSV rows | Remove or skip |
| Inconsistent delimiters | Mix of commas and semicolons | Standardise |
| Broken quotes | "He said "hello"" | Escape or rephrase |
| HTML artifacts | &amp; nbsp; | Convert to plain text |

### Cleaning Script

```bash
# Convert encoding
iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv

# Remove empty lines
sed '/^$/d' input.txt > output.txt

# Remove HTML entities
sed 's/&nbsp;/ /g; s/&amp;/\&/g' input.txt > output.txt
```

## Step 4: Structure Optimisation

### For CSV Data

**Good structure:**

```csv
participant_id,segment,question,response
P001,power_user,"What do you use most?","Dashboard and API"
P001,power_user,"What frustrates you?","Export is slow"
P002,casual_user,"What do you use most?","Just the mobile app"
```

**Poor structure:**

```csv
id,data
1,"some feedback about everything"
2,"more general feedback"
```

### For Interview Transcripts

**Good structure:**

```markdown
# Interview: P001

## Context
Role: Product Manager | Experience: 5 years

## Key Quotes
> "I check the dashboard every morning"
> "Export needs to be one click"

## Observations
- Very efficient with keyboard shortcuts
- Visible frustration with modal dialogs
```

**Poor structure:**

```
talked to someone about the product they said stuff about it being good but also bad
```

## Step 5: Token Optimisation

LLM costs are based on tokens. Optimise for quality and cost:

### What to Keep

- Direct quotes from participants
- Specific behaviours observed
- Concrete pain points
- Clear goals and motivations

### What to Remove

- Interviewer statements (unless context-critical)
- Filler words ("um", "like", "you know")
- Redundant information
- Administrative notes

### Before and After

**Before (450 tokens):**
```
Interviewer: So, um, tell me about your experience?
P001: Well, you know, I mean, I guess I would say that like,
the app is, um, pretty good most of the time but sometimes,
you know, when I'm trying to export things, it's like, really
frustrating because there are so many steps...
```

**After (120 tokens):**
```
P001: "The app is good most of the time, but export is
frustrating because there are so many steps."
```

### Token Estimation

```bash
# Preview token count before processing
persona preview experiments/my-experiment/data/

# Output:
# Total tokens: ~3,500
# Estimated cost: $0.12
```

## Step 6: Multi-Language Data

If you have data in multiple languages:

### Option A: Translate Before Processing

```bash
# Translate to English (using external tool)
translate input.csv --to english > input_en.csv
```

### Option B: Process in Original Language

Persona supports multi-language input:

```bash
persona generate \
  --from my-experiment \
  --language auto  # Detect language
```

### Option C: Separate by Language

```
data/
├── english/
│   └── interviews_en.csv
├── spanish/
│   └── interviews_es.csv
└── combined/
    └── all_interviews.csv
```

## Step 7: Quality Validation

Before processing, validate your data:

```bash
# Preview and validate
persona data validate experiments/my-experiment/data/
```

**Output:**

```
Data Validation Report
───────────────────────────────────
Files: 4
Total tokens: 3,500

Quality Checks:
  ✓ All files readable
  ✓ Encoding: UTF-8
  ✓ No empty files
  ⚠ interviews.csv: 3 empty rows (lines 12, 45, 67)
  ⚠ notes.txt: Possible PII detected (line 23)

Recommendations:
  1. Remove empty rows from interviews.csv
  2. Review line 23 of notes.txt for anonymisation
```

## Step 8: Folder Organisation

Structure your data folder clearly:

```
experiments/my-experiment/data/
├── README.md              # Describe data sources
├── interviews/
│   ├── round-1/
│   │   └── transcripts.md
│   └── round-2/
│       └── transcripts.md
├── surveys/
│   └── results.csv
└── observations/
    └── field-notes.txt
```

### Data README Template

```markdown
# Data Sources

## Interviews
- Round 1: 10 participants, Dec 2024
- Round 2: 8 participants, Jan 2025

## Surveys
- 89 responses, collected Nov 2024

## Observations
- 3 field sessions, usability testing

## Anonymisation
Anonymised on 2024-12-15 by research team.
All participant names replaced with IDs.
```

## Common Mistakes

| Mistake | Impact | Prevention |
|---------|--------|------------|
| PII in data | Privacy violation | Anonymise first |
| Wrong encoding | Garbled text | Convert to UTF-8 |
| Too much data | High cost, noise | Curate key insights |
| Too little data | Shallow personas | Combine sources |
| Inconsistent structure | Poor extraction | Standardise format |

## Verification

Confirm your data is ready:

```bash
# Full validation
persona data validate experiments/my-experiment/data/ --strict

# Expected output
✓ Data validation passed
  Files: 4
  Tokens: 3,500
  Estimated cost: $0.12
  Quality: Good

Ready for generation: Yes
```

---

## Related Documentation

- [T-03: Data Formats](../tutorials/03-data-formats.md)
- [F-001: Data Loading](../development/roadmap/features/completed/F-001-data-loading.md)
- [F-022: Data Preview](../development/roadmap/features/completed/F-022-data-preview.md)

