# Manual Test Script: Quality Metrics (F-106)

This script verifies the quality metrics scoring functionality. Execute tests in order and record results.

## Prerequisites

- Python 3.12+
- Persona installed with `pip install -e ".[all]"`
- Sample persona JSON file for testing

## Setup

```bash
# 1. Activate virtual environment
source .venv-test/bin/activate  # On Windows: .venv-test\Scripts\activate

# 2. Verify installation
persona --version
```

**Expected:** Shows Persona version

---

## Test 1: Score Command Help

**Command:**
```bash
persona score --help
```

**Expected:** Shows help text with options including --output, --save, --min-score, --strict, --lenient

**Pass Criteria:**
- [ ] Help text displays correctly
- [ ] All options documented
- [ ] No import errors

---

## Test 2: Score Single Persona File

**Setup:** Create a test file `test_persona.json`:
```json
[
  {
    "id": "p001",
    "name": "Sarah Mitchell",
    "demographics": {
      "age": "32",
      "occupation": "Product Manager",
      "location": "London"
    },
    "goals": [
      "Streamline team communication workflows",
      "Reduce time spent on manual status updates"
    ],
    "pain_points": [
      "Too many meetings fragment the day"
    ],
    "behaviours": [
      "Checks Slack first thing every morning"
    ],
    "quotes": [
      "I spend half my day just figuring out what's happening"
    ]
  }
]
```

**Command:**
```bash
persona score test_persona.json
```

**Expected:**
- Quality score summary displayed
- Dimension breakdown shown
- Individual persona scores in table format

**Pass Criteria:**
- [ ] Overall score displayed (0-100)
- [ ] All 5 dimensions shown (completeness, consistency, evidence, distinctiveness, realism)
- [ ] Quality level displayed (excellent/good/acceptable/poor/failing)

---

## Test 3: JSON Output

**Command:**
```bash
persona score test_persona.json --output json
```

**Expected:** Valid JSON output with scores and dimension data

**Pass Criteria:**
- [ ] Output is valid JSON
- [ ] Contains `overall_score`, `level`, `dimensions`
- [ ] Can be piped to `jq` for further processing

---

## Test 4: Minimum Score Threshold

**Command:**
```bash
persona score test_persona.json --min-score 95
echo "Exit code: $?"
```

**Expected:** Exit code 1 if score below threshold, exit code 0 if above

**Pass Criteria:**
- [ ] Exits with code 1 for scores below threshold
- [ ] Error message indicates failing personas
- [ ] Exits with code 0 for scores above threshold

---

## Test 5: Strict Mode

**Command:**
```bash
persona score test_persona.json --strict
```

**Expected:** Uses stricter thresholds (higher requirements for each quality level)

**Pass Criteria:**
- [ ] Score may be lower than default mode
- [ ] Thresholds shifted upward

---

## Test 6: Lenient Mode

**Command:**
```bash
persona score test_persona.json --lenient
```

**Expected:** Uses more lenient thresholds (lower requirements)

**Pass Criteria:**
- [ ] Score may be higher than default mode
- [ ] Thresholds shifted downward

---

## Test 7: Save Report to File

**Command:**
```bash
persona score test_persona.json --save quality_report.json
cat quality_report.json
```

**Expected:** Report saved to specified file

**Pass Criteria:**
- [ ] File created successfully
- [ ] Contains complete quality data
- [ ] File is valid JSON

---

## Test 8: Markdown Output

**Command:**
```bash
persona score test_persona.json --output markdown
```

**Expected:** Markdown-formatted report with tables

**Pass Criteria:**
- [ ] Output is valid Markdown
- [ ] Contains summary table
- [ ] Contains individual scores table

---

## Test 9: Low Quality Persona Detection

**Setup:** Create `low_quality_persona.json`:
```json
[
  {
    "id": "p002",
    "name": "User",
    "demographics": {},
    "goals": ["Be better"],
    "pain_points": [],
    "behaviours": [],
    "quotes": []
  }
]
```

**Command:**
```bash
persona score low_quality_persona.json
```

**Expected:** Low score with issues listed

**Pass Criteria:**
- [ ] Score significantly lower than high-quality persona
- [ ] Issues listed for completeness, realism dimensions
- [ ] Generic name flagged
- [ ] Missing fields flagged

---

## Test 10: Multiple Personas (Distinctiveness)

**Setup:** Create `multiple_personas.json`:
```json
[
  {
    "id": "p001",
    "name": "Sarah Mitchell",
    "goals": ["Streamline team communication"],
    "pain_points": ["Too many meetings"]
  },
  {
    "id": "p002",
    "name": "James Chen",
    "goals": ["Improve code quality"],
    "pain_points": ["Technical debt"]
  }
]
```

**Command:**
```bash
persona score multiple_personas.json
```

**Expected:** Both personas scored, distinctiveness calculated

**Pass Criteria:**
- [ ] Both personas appear in results
- [ ] Distinctiveness scores shown
- [ ] Average score calculated
- [ ] Dimension averages shown

---

## Test 11: Python API Usage

**Command:**
```python
from persona.core.quality import QualityScorer, QualityConfig
from persona.core.generation.parser import Persona

# Create test persona
persona = Persona(
    id="p001",
    name="Test User",
    goals=["Goal one", "Goal two"],
    pain_points=["Pain point"],
)

# Score
scorer = QualityScorer()
result = scorer.score(persona)

print(f"Overall: {result.overall_score}")
print(f"Level: {result.level.value}")
print(f"Completeness: {result.dimensions['completeness'].score}")
```

**Expected:** Scores calculated via Python API

**Pass Criteria:**
- [ ] No import errors
- [ ] Score returned successfully
- [ ] Dimension scores accessible

---

## Test 12: Configuration Presets

**Command:**
```python
from persona.core.quality import QualityConfig

default = QualityConfig()
strict = QualityConfig.strict()
lenient = QualityConfig.lenient()

print(f"Default min_goals: {default.min_goals}")
print(f"Strict min_goals: {strict.min_goals}")
print(f"Lenient min_goals: {lenient.min_goals}")

print(f"Default excellent threshold: {default.excellent_threshold}")
print(f"Strict excellent threshold: {strict.excellent_threshold}")
```

**Expected:** Different thresholds for each preset

**Pass Criteria:**
- [ ] Strict has higher requirements
- [ ] Lenient has lower requirements
- [ ] All presets validate successfully

---

## Cleanup

```bash
rm -f test_persona.json low_quality_persona.json multiple_personas.json quality_report.json
```

---

## Results Summary

| Test | Status |
|------|--------|
| Test 1: Help | [ ] |
| Test 2: Single Persona | [ ] |
| Test 3: JSON Output | [ ] |
| Test 4: Min Score | [ ] |
| Test 5: Strict Mode | [ ] |
| Test 6: Lenient Mode | [ ] |
| Test 7: Save Report | [ ] |
| Test 8: Markdown Output | [ ] |
| Test 9: Low Quality | [ ] |
| Test 10: Multiple Personas | [ ] |
| Test 11: Python API | [ ] |
| Test 12: Config Presets | [ ] |

**Tested by:** ________________
**Date:** ________________
**Notes:**
