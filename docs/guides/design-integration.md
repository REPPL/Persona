# Integrating Personas into Design Workflow

A practical guide to using generated personas in design tools and team workflows.

## Goal

Export and integrate personas into your existing design workflow, including popular tools like Figma, Miro, and stakeholder presentation formats.

## Prerequisites

- Generated personas (completed generation)
- Access to your design tools (Figma, Miro, etc.)
- Understanding of [persona output format](../tutorials/02-understanding-output.md)

## Export Formats Overview

| Format | Best For | Command |
|--------|----------|---------|
| Markdown | Documentation, GitHub | `--format md` |
| HTML | Presentations, web | `--format html` |
| PDF | Printing, sharing | `--format pdf` |
| Figma | Design files | `--format figma` |
| Miro | Workshops, collaboration | `--format miro` |
| JSON | Integration, automation | `--format json` |

## Exporting Personas

### Basic Export

```bash
# Export single persona
persona export <persona-id> --format html --output ./exports/

# Export all personas from experiment
persona export --all --from my-experiment --format pdf

# Export collection
persona export collection "Mobile Users" --format figma
```

### Export Options

```bash
persona export <id> \
  --format html \
  --output ./exports/ \
  --include-evidence \      # Include source citations
  --include-metadata \      # Include generation details
  --template professional   # Use professional template
```

## Figma Integration

### Export for Figma

```bash
persona export --all --format figma --output personas.fig
```

This creates a Figma-compatible file with:
- Persona cards (auto-layout frames)
- Consistent styling
- Editable text fields
- Placeholder for persona images

### Manual Figma Setup

If you prefer manual setup:

1. **Create a persona card component** in Figma
2. **Copy JSON attributes** from persona output
3. **Paste into text fields**

**Persona Card Template Structure:**

```
┌─────────────────────────────────────┐
│  [Photo Placeholder]                │
│                                     │
│  Name: Sarah Chen                   │
│  Title: The Mobile Professional     │
│                                     │
│  ─────────────────────────────────  │
│  Demographics                       │
│  • Age: 30-35                       │
│  • Role: Marketing Manager          │
│                                     │
│  Goals                              │
│  • Mobile efficiency                │
│  • Offline access                   │
│                                     │
│  Pain Points                        │
│  • No offline mode                  │
│  • Complex navigation               │
│                                     │
│  Key Quote                          │
│  "I need this to work on the tube"  │
└─────────────────────────────────────┘
```

## Miro Integration

### Export for Miro

```bash
persona export --all --format miro --output personas-board.json
```

### Import to Miro

1. Open your Miro board
2. Use **Import** feature
3. Select the exported JSON file
4. Position imported cards on board

### Miro Board Layout

Organise personas in a useful structure:

```
┌───────────────────────────────────────────────────────┐
│                    PERSONA BOARD                       │
├───────────┬───────────┬───────────┬───────────────────┤
│  Primary  │ Secondary │ Tertiary  │    Edge Cases     │
│  Personas │ Personas  │ Personas  │                   │
├───────────┼───────────┼───────────┼───────────────────┤
│           │           │           │                   │
│  [Sarah]  │  [James]  │  [Elena]  │    [Marcus]       │
│           │           │           │                   │
└───────────┴───────────┴───────────┴───────────────────┘
```

## Creating Persona Posters

### Generate Print-Ready Posters

```bash
persona export <id> --format pdf --template poster
```

### Poster Layout (A3/A2)

```
┌─────────────────────────────────────────┐
│                                         │
│   [Large Photo/Illustration]            │
│                                         │
│   SARAH CHEN                            │
│   The Mobile Professional               │
│                                         │
├────────────────┬────────────────────────┤
│ DEMOGRAPHICS   │ GOALS                  │
│ • Age: 30-35   │ • Mobile efficiency    │
│ • Marketing    │ • Offline access       │
│ • Urban        │ • Quick tasks          │
├────────────────┼────────────────────────┤
│ PAIN POINTS    │ BEHAVIOURS             │
│ • No offline   │ • Morning commute      │
│ • Complex nav  │ • Voice commands       │
│ • Many clicks  │ • Keyboard shortcuts   │
├────────────────┴────────────────────────┤
│ KEY QUOTE                               │
│ "I need this to work on the tube        │
│  with no signal"                        │
└─────────────────────────────────────────┘
```

## Stakeholder Presentations

### Presentation Export

```bash
persona export --all --format html --template presentation
```

### Slide Structure

**Slide 1: Overview**
- Research methodology
- Data sources
- Persona count

**Slides 2-N: Individual Personas**
- One persona per slide
- Key attributes highlighted
- Representative quote

**Final Slide: Comparison**
- All personas at glance
- Key differentiators
- Usage recommendations

### PowerPoint/Google Slides

```bash
# Export to HTML, then copy/paste
persona export --all --format html --output ./presentation/

# Or export individual elements
persona export <id> --format json --output persona.json
```

Then manually create slides using the structured data.

## Living Persona Documentation

### Wiki/Notion Integration

Export personas as Markdown for documentation platforms:

```bash
persona export --all --format md --output ./wiki/personas/
```

**File structure:**

```
wiki/personas/
├── README.md           # Overview and index
├── sarah-chen.md       # Individual persona
├── james-developer.md
└── elena-commuter.md
```

### Keep Documentation Updated

When personas are regenerated:

```bash
# Re-export and update
persona export --all --format md --output ./wiki/personas/ --overwrite

# Or sync with version control
cd ./wiki/personas/
git add .
git commit -m "Update personas from latest research"
git push
```

## Team Sharing Workflow

### Shared Drive Export

```bash
# Export to team folder
persona export collection "Q4 Personas" \
  --format bundle \
  --output /shared/research/personas/
```

Creates:

```
/shared/research/personas/q4-personas-2024-12-15/
├── README.md           # Usage instructions
├── personas/
│   ├── sarah-chen.md
│   ├── sarah-chen.json
│   └── ...
├── metadata.json       # Generation details
└── poster-assets/      # Print-ready files
    ├── sarah-chen.pdf
    └── ...
```

### Slack/Teams Notification

After exporting, notify your team:

```bash
# Generate shareable summary
persona export --all --format summary

# Output:
# Generated 3 personas from Q4 research
# - Sarah Chen (Mobile Professional)
# - James Wong (Developer)
# - Elena Ruiz (Casual User)
#
# View: /shared/research/personas/q4-personas-2024-12-15/
```

## Integration with Design Systems

### Design Token Export

For design systems that use tokens:

```bash
persona export --format tokens --output persona-tokens.json
```

**Output:**

```json
{
  "personas": {
    "sarah": {
      "color": "#4A90D9",
      "label": "Mobile Professional",
      "priority": "primary"
    },
    "james": {
      "color": "#7CB342",
      "label": "Developer",
      "priority": "secondary"
    }
  }
}
```

### Component Library Integration

Reference personas in your component library:

```jsx
// React example
import { personas } from './persona-tokens.json';

function PersonaBadge({ personaId }) {
  const persona = personas[personaId];
  return (
    <Badge color={persona.color}>
      {persona.label}
    </Badge>
  );
}
```

## Verification

After integration, verify personas are usable:

- [ ] All personas visible in design tool
- [ ] Text is editable (not rasterised)
- [ ] Photos/placeholders appropriate size
- [ ] Colours match brand guidelines
- [ ] Stakeholders can access shared files
- [ ] Version/date visible for reference

---

## Related Documentation

- [T-02: Understanding Output](../tutorials/02-understanding-output.md)
- [T-05: Building a Library](../tutorials/05-building-library.md)
- [F-026: Export to Persona Tools](../development/roadmap/features/planned/F-026-export-to-persona-tools.md)

