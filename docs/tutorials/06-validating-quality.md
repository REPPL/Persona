# Validating Persona Quality

Learn to critically evaluate generated personas and ensure they reflect your source data.

**Level:** Advanced | **Time:** 30 minutes

## What You'll Learn

- What makes a persona "valid"
- Cross-referencing with source data
- Identifying hallucinated attributes
- Using the validation command
- Iterative refinement workflow
- Documentation for stakeholder review

## Prerequisites

- Completed [Understanding Output](02-understanding-output.md)
- Generated personas with source data available
- Understanding of qualitative research principles

## Why Validation Matters

Academic research warns about LLM persona biases:

> "LLM-generated personas may include plausible-sounding details not grounded in actual user data, potentially misleading design decisions."
> — Shin et al., DIS 2024

Validation ensures your personas:
- Accurately reflect source data
- Don't include hallucinated details
- Are suitable for decision-making
- Can withstand stakeholder scrutiny

## Step 1: Understanding Validity

A valid persona is:

| Criterion | Description | How to Check |
|-----------|-------------|--------------|
| **Grounded** | Every claim backed by source data | Evidence linking |
| **Representative** | Reflects patterns, not outliers | Coverage analysis |
| **Consistent** | No internal contradictions | Logic check |
| **Distinct** | Different from other personas | Comparison |
| **Actionable** | Enables design decisions | Stakeholder review |

## Step 2: Run Validation Command

Use the built-in validation:

```bash
persona validate <persona-id> --source experiments/my-experiment/data/
```

**Output:**

```
Persona Validation Report: Sarah Chen
───────────────────────────────────

Overall Score: 87% (Good)

Coverage Analysis
───────────────────────────────────
Attributes with evidence:    18/21 (86%)
Attributes without evidence:  3/21 (14%)

Grounded Attributes:
  ✓ "Marketing Manager" — source: interviews.csv:15
  ✓ "Uses mobile app daily" — source: interviews.csv:15,23
  ✓ "Frustrated by export" — source: field-notes.txt:42
  ✓ "Values efficiency" — source: interviews.csv:15,89

Ungrounded Attributes (Potential Hallucinations):
  ⚠ "Age 32" — No age data in sources
  ⚠ "Lives in San Francisco" — Location not mentioned
  ⚠ "Has MBA degree" — Education not discussed

Recommendations:
  1. Remove or generalise ungrounded attributes
  2. Add evidence notes for stakeholder review
  3. Consider regenerating with --strict flag
```

## Step 3: Evidence Linking Review

Examine how each attribute maps to source data:

```bash
persona validate --show-evidence
```

**Detailed output:**

```
Attribute: "Frustrated by export process"
───────────────────────────────────
Evidence Strength: Strong (3 sources)

Source 1: interviews.csv:15
  "The export function drives me crazy. Why can't I just
   click once and get a PDF?"

Source 2: field-notes.txt:42
  "Participant 3 took 45 seconds to find export, visible
   frustration, said 'why is this so hidden?'"

Source 3: survey-results.csv:89
  Rating: Export feature = 2/5
  Comment: "Export needs major improvement"
```

### Evidence Strength Scale

| Strength | Sources | Confidence |
|----------|---------|------------|
| **Strong** | 3+ sources | High confidence, keep as-is |
| **Moderate** | 2 sources | Good, consider emphasis |
| **Weak** | 1 source | Include with caution |
| **None** | 0 sources | Likely hallucination |

## Step 4: Identifying Hallucinations

Common hallucination patterns:

| Type | Example | Why It Happens |
|------|---------|----------------|
| **Specific numbers** | "Age 32" when data says "30s" | LLM adds false precision |
| **Named locations** | "Lives in Seattle" not in data | LLM fills gaps |
| **Credentials** | "Has CS degree" assumed | LLM stereotypes |
| **Backstory** | "Started coding at 12" | LLM creates narrative |

### Hallucination Detection Checklist

- [ ] Are specific ages justified by data?
- [ ] Are locations mentioned in sources?
- [ ] Are education/credentials supported?
- [ ] Are family details (married, 2 kids) in data?
- [ ] Are hobbies/interests from actual quotes?

## Step 5: Gap Analysis

Identify what's missing from your personas:

```bash
persona validate --gaps
```

**Output:**

```
Gap Analysis
───────────────────────────────────

Themes in data NOT represented in personas:
  - Security concerns (mentioned by 4 participants)
  - Accessibility needs (mentioned by 2 participants)
  - Team collaboration patterns (mentioned by 6 participants)

Participant segments NOT represented:
  - Senior/executive users (n=3 in data)
  - International users (n=2 in data)

Recommendation: Regenerate with 5 personas to capture
additional segments, or manually add missing themes.
```

## Step 6: Iterative Refinement

When validation reveals issues:

### Option A: Regenerate with Constraints

```bash
# Strict mode - only use explicit data
persona generate --from my-experiment --strict

# More personas to capture segments
persona generate --from my-experiment --count 5

# Different model (may hallucinate less)
persona generate --from my-experiment --model claude-3-sonnet
```

### Option B: Manual Refinement

```bash
persona refine <persona-id>
```

**Interactive session:**

```
Current persona: Sarah Chen

What would you like to change?
> Remove the specific age, use "early 30s" instead

Updating persona...

Changed:
  - "Age: 32" → "Age: Early 30s"

What else?
> Remove the San Francisco location entirely

Updating persona...

Changed:
  - Removed: "Location: San Francisco"

Validation score: 87% → 94%

Save changes? [Y/n]: y
```

### Option C: Add Evidence Notes

For attributes you want to keep despite weak evidence:

```json
{
  "attribute": "Tech-savvy",
  "value": true,
  "evidence": {
    "strength": "inferred",
    "note": "Implied by quick adoption of features (observed, not stated)",
    "reviewer": "Research team, 2024-12-15"
  }
}
```

## Step 7: Validation Report for Stakeholders

Generate a shareable report:

```bash
persona validate --report --output validation-report.md
```

**Report structure:**

```markdown
# Persona Validation Report

## Executive Summary
3 personas validated against 15 interview transcripts
and 89 survey responses.

## Overall Scores
| Persona | Score | Status |
|---------|-------|--------|
| Sarah Chen | 94% | ✓ Validated |
| James Developer | 88% | ✓ Validated |
| Elena Commuter | 76% | ⚠ Review needed |

## Methodology
- Source data: 15 interviews, 89 survey responses
- Validation method: Embedding-based evidence matching
- Threshold: 80% for approval

## Detailed Findings
[Per-persona breakdown with evidence links]

## Recommendations
[Action items for personas needing review]
```

## Validation Workflow

### Pre-Stakeholder Review

1. **Generate** personas
2. **Validate** automatically
3. **Review** ungrounded attributes
4. **Refine** or remove hallucinations
5. **Document** evidence for key claims
6. **Export** validation report

### Regular Validation Schedule

| Trigger | Action |
|---------|--------|
| New data added | Re-validate existing personas |
| Before presentation | Generate validation report |
| Quarterly | Review and refresh personas |
| New team member | Share validation methodology |

## Common Validation Pitfalls

### Over-validation

**Problem:** Removing everything not explicitly quoted
**Result:** Bland, unusable personas

**Solution:** Allow reasonable inference with documentation

### Under-validation

**Problem:** Accepting all LLM output as truth
**Result:** Personas with false details

**Solution:** Always run validation before sharing

### Metric Obsession

**Problem:** Optimising for 100% score only
**Result:** Missing the point of useful personas

**Solution:** Balance scores with usefulness review

## What's Next?

Now that you can validate personas:

1. **[G-02: Preparing Data](../guides/preparing-data.md)** - Better data = better validation
2. **[Evidence Linking](../development/roadmap/features/planned/F-024-evidence-linking.md)** - Automatic provenance
3. **[Reproducibility](../explanation/reproducibility.md)** - Consistent validation results

---

## Related Documentation

- [F-019: Persona Validation](../development/roadmap/features/planned/F-019-persona-validation.md)
- [F-024: Evidence Linking](../development/roadmap/features/planned/F-024-evidence-linking.md)
- [UC-005: Validate Personas](../use-cases/briefs/UC-005-validate-personas.md)

## Academic References

- Shin, J., Hedderich, M. A., Lucero, A., & Oulasvirta, A. (2024). Understanding Human-AI Workflows for Generating Personas. *Designing Interactive Systems Conference (DIS)*. https://doi.org/10.1145/3643834.3660729
- LLM Generated Persona is a Promise with a Catch. *arXiv:2503.16527*

