# F-148: Persona Diff Tool

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-148 |
| **Title** | Persona Diff Tool |
| **Priority** | P1 (High) |
| **Category** | UX |
| **Milestone** | [v1.14.0](../../milestones/v1.14.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | None |

---

## Problem Statement

When personas are refined iteratively, users need to:
- See what changed between versions
- Understand semantic vs structural changes
- Compare personas side-by-side
- Document changes for audit

Currently, comparison requires manual inspection.

---

## Design Approach

Provide structural and semantic diff capabilities with multiple output formats.

---

## Key Capabilities

### 1. Structural Diff

Compare persona structure and values.

```bash
persona diff persona-a.json persona-b.json
```

**Output:**
```
Persona Diff: persona-a.json → persona-b.json
═══════════════════════════════════════════════════════════════

Changed Fields
──────────────
  demographics.age:
    - 28
    + 32

  demographics.location:
    - "London"
    + "Manchester"

  goals[0]:
    - "Save time on daily tasks"
    + "Save time on work-related tasks"

Added Fields
────────────
  + goals[2]: "Improve work-life balance"
  + frustrations[1]: "Too many meetings"

Removed Fields
──────────────
  - behaviours[3]: "Checks social media hourly"

Summary: 3 changed, 2 added, 1 removed
```

### 2. Semantic Diff

Compare meaning beyond structural changes.

```bash
persona diff --semantic persona-a.json persona-b.json
```

**Output:**
```
Semantic Analysis
═════════════════

Overall Similarity: 87%

Significant Semantic Changes
────────────────────────────
1. Career Focus Shift
   Before: Lifestyle-oriented goals
   After: Career-oriented goals
   Impact: High

2. Location Change
   Before: London metropolitan
   After: Northern England
   Impact: Medium (different cultural context)

Minor Semantic Drift
────────────────────
- Age increase (4 years) within same life stage
- Frustration topics shifted from personal to professional
```

### 3. Version Diff

Compare versioned personas.

```bash
persona version diff customer-sarah v1 v3
```

### 4. Export Formats

Export diffs in various formats.

```bash
# Text (default)
persona diff a.json b.json

# JSON (machine-readable)
persona diff --format json a.json b.json

# HTML (visual)
persona diff --format html a.json b.json --output diff.html

# Markdown
persona diff --format md a.json b.json --output diff.md
```

---

## CLI Commands

```bash
# Basic diff
persona diff PERSONA_A PERSONA_B [--format text|json|html|md]

# Semantic diff
persona diff --semantic PERSONA_A PERSONA_B

# Version diff
persona version diff PERSONA_ID VERSION_A VERSION_B

# Side-by-side
persona diff --side-by-side PERSONA_A PERSONA_B

# Output to file
persona diff PERSONA_A PERSONA_B --output DIFF_FILE
```

---

## Success Criteria

- [ ] Structural diff shows all changes accurately
- [ ] Semantic diff identifies meaning changes
- [ ] Multiple output formats supported
- [ ] Version diff integrates with versioning system
- [ ] Side-by-side display works in terminal
- [ ] Test coverage >= 85%

---

## Related Documentation

- [v1.14.0 Milestone](../../milestones/v1.14.0.md)
- [R-032: Persona Evolution & Versioning](../../../research/R-032-persona-evolution-versioning.md)

---

**Status**: Planned
