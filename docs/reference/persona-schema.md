# Persona Schema Reference

Technical specification for the persona JSON output format.

## Schema Version

Current version: `1.0.0`

## Complete Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Persona",
  "description": "A generated user persona from research data",
  "type": "object",
  "required": ["id", "name", "title", "demographics", "goals", "pain_points"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique identifier for this persona",
      "pattern": "^persona-[0-9]{3}$"
    },
    "name": {
      "type": "string",
      "description": "Full name of the persona",
      "minLength": 1,
      "maxLength": 100
    },
    "title": {
      "type": "string",
      "description": "Descriptive title (e.g., 'The Mobile Professional')",
      "minLength": 1,
      "maxLength": 100
    },
    "demographics": {
      "$ref": "#/definitions/Demographics"
    },
    "goals": {
      "type": "array",
      "description": "What this persona is trying to achieve",
      "items": {
        "type": "string"
      },
      "minItems": 1,
      "maxItems": 10
    },
    "pain_points": {
      "type": "array",
      "description": "Frustrations and challenges faced",
      "items": {
        "type": "string"
      },
      "minItems": 1,
      "maxItems": 10
    },
    "behaviours": {
      "type": "array",
      "description": "Observable actions and habits",
      "items": {
        "type": "string"
      },
      "maxItems": 10
    },
    "motivations": {
      "type": "array",
      "description": "Underlying drivers and values",
      "items": {
        "type": "string"
      },
      "maxItems": 10
    },
    "quotes": {
      "type": "array",
      "description": "Representative quotes from source data",
      "items": {
        "type": "string"
      },
      "maxItems": 5
    },
    "evidence": {
      "$ref": "#/definitions/Evidence"
    },
    "metadata": {
      "$ref": "#/definitions/Metadata"
    }
  },
  "definitions": {
    "Demographics": {
      "type": "object",
      "description": "Demographic characteristics",
      "properties": {
        "age_range": {
          "type": "string",
          "description": "Age range (e.g., '30-35')"
        },
        "occupation": {
          "type": "string",
          "description": "Job title or role"
        },
        "industry": {
          "type": "string",
          "description": "Industry sector"
        },
        "tech_proficiency": {
          "type": "string",
          "enum": ["Novice", "Beginner", "Intermediate", "Advanced", "Expert"]
        },
        "location": {
          "type": "string",
          "description": "Geographic location type (e.g., 'Urban', 'Rural')"
        },
        "education": {
          "type": "string",
          "description": "Education level"
        },
        "custom": {
          "type": "object",
          "description": "Additional demographic fields",
          "additionalProperties": {
            "type": "string"
          }
        }
      }
    },
    "Evidence": {
      "type": "object",
      "description": "Source data evidence for persona attributes",
      "properties": {
        "coverage_score": {
          "type": "number",
          "description": "Percentage of attributes with evidence (0-100)",
          "minimum": 0,
          "maximum": 100
        },
        "attributes": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/EvidenceItem"
          }
        }
      }
    },
    "EvidenceItem": {
      "type": "object",
      "required": ["attribute", "sources"],
      "properties": {
        "attribute": {
          "type": "string",
          "description": "The persona attribute being evidenced"
        },
        "strength": {
          "type": "string",
          "enum": ["strong", "moderate", "weak", "inferred"],
          "description": "Strength of evidence"
        },
        "sources": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/Source"
          }
        }
      }
    },
    "Source": {
      "type": "object",
      "required": ["file", "quote"],
      "properties": {
        "file": {
          "type": "string",
          "description": "Source file name"
        },
        "line": {
          "type": "integer",
          "description": "Line number in source file"
        },
        "quote": {
          "type": "string",
          "description": "Relevant quote from source"
        }
      }
    },
    "Metadata": {
      "type": "object",
      "description": "Generation metadata",
      "properties": {
        "generated_at": {
          "type": "string",
          "format": "date-time"
        },
        "experiment": {
          "type": "string"
        },
        "provider": {
          "type": "string"
        },
        "model": {
          "type": "string"
        },
        "template": {
          "type": "string"
        },
        "version": {
          "type": "string"
        }
      }
    }
  }
}
```

## Field Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (e.g., "persona-001") |
| `name` | string | Full name of persona |
| `title` | string | Descriptive title |
| `demographics` | object | Demographic information |
| `goals` | array | What they're trying to achieve |
| `pain_points` | array | Frustrations and challenges |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `behaviours` | array | Observable actions and habits |
| `motivations` | array | Underlying drivers |
| `quotes` | array | Representative quotes |
| `evidence` | object | Source data citations |
| `metadata` | object | Generation information |

### Demographics Object

| Field | Type | Values |
|-------|------|--------|
| `age_range` | string | "20-25", "25-30", etc. |
| `occupation` | string | Job title |
| `industry` | string | Sector name |
| `tech_proficiency` | enum | Novice, Beginner, Intermediate, Advanced, Expert |
| `location` | string | Urban, Suburban, Rural |
| `education` | string | Education level |
| `custom` | object | Additional fields |

## Example Persona

### Minimal Example

```json
{
  "id": "persona-001",
  "name": "Sarah Chen",
  "title": "The Mobile Professional",
  "demographics": {
    "age_range": "30-35",
    "occupation": "Marketing Manager"
  },
  "goals": [
    "Complete tasks efficiently on mobile",
    "Stay productive during commutes"
  ],
  "pain_points": [
    "Frustration when offline",
    "Too many steps for simple tasks"
  ]
}
```

### Full Example with Evidence

```json
{
  "id": "persona-001",
  "name": "Sarah Chen",
  "title": "The Mobile Professional",
  "demographics": {
    "age_range": "30-35",
    "occupation": "Marketing Manager",
    "industry": "Technology",
    "tech_proficiency": "Intermediate",
    "location": "Urban",
    "education": "Bachelor's degree",
    "custom": {
      "team_size": "5-10",
      "years_in_role": "3-5"
    }
  },
  "goals": [
    "Complete tasks efficiently on mobile devices",
    "Stay productive during commutes",
    "Access key features without internet connection",
    "Quickly share reports with stakeholders"
  ],
  "pain_points": [
    "Frustration when features don't work offline",
    "Too many steps required for simple tasks",
    "Difficulty finding specific features",
    "Slow load times on mobile"
  ],
  "behaviours": [
    "Checks app every morning during commute",
    "Prefers mobile app over desktop for quick tasks",
    "Uses keyboard shortcuts extensively",
    "Shares dashboard links with team weekly"
  ],
  "motivations": [
    "Efficiency and time-saving",
    "Professional reputation",
    "Work-life balance",
    "Career advancement"
  ],
  "quotes": [
    "I need this to work when I'm on the tube with no signal",
    "If I can't find it in 3 taps, I give up",
    "The export function drives me crazy"
  ],
  "evidence": {
    "coverage_score": 87,
    "attributes": [
      {
        "attribute": "Marketing Manager occupation",
        "strength": "strong",
        "sources": [
          {
            "file": "interviews.csv",
            "line": 15,
            "quote": "I'm a marketing manager at a tech startup"
          }
        ]
      },
      {
        "attribute": "Frustration with offline",
        "strength": "strong",
        "sources": [
          {
            "file": "interviews.csv",
            "line": 23,
            "quote": "When I lose signal on the tube, everything breaks"
          },
          {
            "file": "survey.json",
            "line": 89,
            "quote": "Offline mode is essential but missing"
          }
        ]
      },
      {
        "attribute": "Age range 30-35",
        "strength": "weak",
        "sources": [
          {
            "file": "interviews.csv",
            "line": 15,
            "quote": "Been in marketing about 8 years now"
          }
        ]
      }
    ]
  },
  "metadata": {
    "generated_at": "2024-12-15T14:30:22Z",
    "experiment": "q4-research",
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229",
    "template": "default",
    "version": "1.0.0"
  }
}
```

## Empathy Map Extension

For empathy map output (UC-009):

```json
{
  "id": "persona-001",
  "name": "Superfan Alice",
  "empathy_map": {
    "tasks": [
      "Expanding and exhibiting collection",
      "Engaging with community"
    ],
    "feelings": [
      "Curation is critical",
      "Access to history matters"
    ],
    "influences": [
      "Community of other fans",
      "Concert venues and organisers"
    ],
    "pain_points": [
      "Collecting becomes time-consuming",
      "Inaccurate information"
    ],
    "goals": [
      "Expand and share collection",
      "Safe interactions"
    ]
  }
}
```

## Validation

### Programmatic Validation

```python
import json
from jsonschema import validate

# Load schema
with open('persona-schema.json') as f:
    schema = json.load(f)

# Load persona
with open('persona.json') as f:
    persona = json.load(f)

# Validate
validate(instance=persona, schema=schema)
```

### CLI Validation

```bash
persona validate --schema persona.json
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-12 | Initial release |

## Extension Points

Custom fields can be added via:

1. **demographics.custom** - Additional demographic fields
2. **empathy_map** - Boag method dimensions
3. **metadata** - Custom metadata fields

---

## Related Documentation

- [F-024: Evidence Linking](../development/roadmap/features/completed/F-024-evidence-linking.md)
- [T-02: Understanding Output](../tutorials/02-understanding-output.md)
- [How Generation Works](../explanation/how-generation-works.md)
