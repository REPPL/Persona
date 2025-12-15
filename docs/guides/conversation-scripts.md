# Conversation Scripts Guide

Generate privacy-preserving conversation scripts from your personas for use with LLMs.

## Overview

Conversation scripts transform static personas into interactive character cards that can be used with LLMs (ChatGPT, Claude, Gemini) to simulate user conversations. This is valuable for:

- User research simulation
- Design validation
- Training and empathy building
- UX testing scenarios

**Privacy First**: Scripts are generated with mandatory privacy auditing to prevent source data leakage.

## Quick Start

### Generate a Single Script

```bash
# System prompt format (ready to paste into ChatGPT/Claude)
persona script generate ./outputs/persona-001.json --format system_prompt

# Save to file
persona script generate ./outputs/persona-001.json \
    --format system_prompt \
    --output script.txt
```

### Batch Generation

```bash
# Generate scripts for all personas in a directory
persona script batch ./outputs/exp-001 --output ./scripts

# Use different format
persona script batch ./outputs --format character_card --yaml
```

## Output Formats

### 1. System Prompt (Text)

Best for: Direct use with LLM chat interfaces

```bash
persona script generate persona.json --format system_prompt
```

**Output**: A comprehensive prompt you can paste directly into ChatGPT, Claude, or other LLMs.

**Example**:
```
You are Sarah Chen, The Marketing Manager.
Background: 32 years old, Marketing Manager, with 8 years experience

## Personality
- efficiency-focused
- values collaboration
- seeks balance

## Goals
- seeks efficiency improvements
- seeks work-life harmony

## Communication Style
Tone: direct and impatient
Vocabulary: professional
- uses urgency language
- prefers concise communication

...
```

### 2. Character Card (JSON/YAML)

Best for: Programmatic use, storage, sharing

```bash
# JSON format (default)
persona script generate persona.json --format character_card

# YAML format
persona script generate persona.json --format character_card --yaml
```

**Output**: Structured character data including:
- Identity (name, title, demographics)
- Psychological profile (goals, motivations, pain points)
- Communication style (tone, vocabulary, speech patterns)
- Knowledge boundaries (knows, doesn't know, can infer)
- Guidelines for LLM behaviour
- Provenance metadata

**Example**:
```json
{
  "id": "script-abc12345",
  "identity": {
    "name": "Sarah Chen",
    "title": "The Marketing Manager",
    "demographics_summary": "32 years old, Marketing Manager..."
  },
  "psychological_profile": {
    "goals": ["seeks efficiency improvements"],
    "personality_traits": ["efficiency-focused", "tech-savvy"],
    "flaws": ["impatient with slow systems"]
  },
  "communication_style": {
    "tone": "professional but frustrated",
    "speech_patterns": ["uses industry jargon"]
  },
  "knowledge_boundaries": {
    "knows": ["mobile app usage patterns"],
    "doesnt_know": ["backend implementation"]
  }
}
```

### 3. Jinja2 Template

Best for: Dynamic contexts, conversation history integration

```bash
persona script generate persona.json --format jinja2_template
```

**Output**: A Jinja2 template with slots for context and conversation history.

**Usage**:
```python
from jinja2 import Template

template = Template(script_content)
prompt = template.render(
    context="User is frustrated with slow checkout",
    conversation_history=[
        {"role": "user", "content": "This is taking too long"},
        {"role": "assistant", "content": "I understand your frustration"}
    ]
)
```

## Privacy Protection

### How It Works

Every script generation includes **mandatory privacy auditing**:

1. **Quote Abstraction**: Direct quotes are transformed into speech patterns
   - ❌ "I hate waiting for reports" (direct quote)
   - ✅ "uses urgency language" (abstracted pattern)

2. **Scenario Generalisation**: Specific incidents become patterns
   - ❌ "Stayed late on Thursday to fix spreadsheet" (specific)
   - ✅ "tendency to work overtime when solving problems" (generalised)

3. **Behaviour Abstraction**: Actions become tendencies
   - ❌ "Uses Slack at 7am every day" (specific)
   - ✅ "routinely checks communication tools early" (abstracted)

4. **Leakage Detection**: Similarity scoring catches paraphrases
   - Blocks output if leakage score > threshold

### Privacy Options

```bash
# Default threshold (0.1 = 10% similarity maximum)
persona script generate persona.json

# Stricter threshold (lower = stricter)
persona script generate persona.json --threshold 0.05

# Custom threshold
persona script generate persona.json --threshold 0.2
```

**Default behaviour**: Output is **blocked** if privacy audit fails.

### Privacy Audit Results

Generation shows privacy audit results:

```
✓ Privacy audit: No leakage detected
```

Or if issues found:

```
⚠️ Privacy audit: Leakage score: 0.08
  Detected 2 potential leakage(s)
```

If blocked:

```
✗ Script generation blocked by privacy audit

Details: Direct quote detected in speech patterns
The script contains potential source data leakage.
```

## Common Workflows

### Workflow 1: ChatGPT Conversation Simulation

```bash
# 1. Generate system prompt
persona script generate ./persona.json --format system_prompt -o prompt.txt

# 2. Copy prompt.txt contents to ChatGPT

# 3. Start conversation:
# "You are participating in a user research interview about our new app..."
```

### Workflow 2: Batch Processing for Team

```bash
# Generate scripts for all personas
persona script batch ./outputs/user-research \
    --output ./scripts \
    --format system_prompt

# Share scripts/ folder with team
# Each researcher gets a character to "play"
```

### Workflow 3: API Integration

```bash
# Generate character cards in JSON
persona script batch ./personas \
    --output ./character-cards \
    --format character_card

# Load into your application
```

```python
import json

with open('character-cards/persona-001.json') as f:
    card = json.load(f)

# Use with OpenAI API
messages = [
    {"role": "system", "content": card_to_system_prompt(card)},
    {"role": "user", "content": "What frustrates you most?"}
]
```

### Workflow 4: Dynamic Contexts with Jinja2

```bash
# Generate template
persona script generate persona.json \
    --format jinja2_template \
    -o character.j2
```

```python
from jinja2 import Template
from persona.core.scripts.models import CharacterCard

# Load template
with open('character.j2') as f:
    template = Template(f.read())

# Render with context
prompt = template.render(
    context="User is trying the app for the first time",
    conversation_history=previous_messages
)
```

## Advanced Options

### Batch Processing Options

```bash
# All options
persona script batch ./personas \
    --output ./scripts \
    --format system_prompt \
    --threshold 0.05 \
    --strict
```

**Options**:
- `--output`, `-o`: Output directory (default: ./scripts)
- `--format`, `-f`: Output format (default: character_card)
- `--yaml`: Use YAML for character_card format
- `--threshold`: Privacy leakage threshold (default: 0.1)
- `--strict`: Block on privacy failure (default: true)

### Understanding Threshold Values

| Threshold | Meaning | Recommended For |
|-----------|---------|-----------------|
| 0.0 - 0.05 | Very strict | Legal/regulated contexts |
| 0.05 - 0.1 | Strict (default) | General use |
| 0.1 - 0.2 | Moderate | Internal research |
| 0.2+ | Lenient | Non-sensitive data |

## Knowledge Boundaries

Scripts include **knowledge boundaries** to make LLM roleplay realistic:

### What the Character Knows

Based on persona's role, behaviours, and context:

```json
"knows": [
  "mobile app usage patterns",
  "team collaboration practices",
  "project planning methodologies"
]
```

### What They Don't Know

Prevents LLM from hallucinating expertise:

```json
"doesnt_know": [
  "backend system implementation",
  "competitor internal processes",
  "future product roadmap"
]
```

### What They Can Infer

Allows educated guesses based on experience:

```json
"can_infer": [
  "general market trends",
  "industry best practices"
]
```

**Usage**: The LLM will stay in character, admitting "I don't know" when appropriate.

## Character Card Schema

Complete structure of a character card:

```json
{
  "id": "script-abc12345",
  "identity": {
    "name": "string",
    "title": "string",
    "demographics_summary": "string"
  },
  "psychological_profile": {
    "goals": ["string"],
    "motivations": ["string"],
    "pain_points": ["string"],
    "personality_traits": ["string"],
    "flaws": ["string"]
  },
  "communication_style": {
    "tone": "string",
    "vocabulary_level": "string",
    "speech_patterns": ["string"]
  },
  "knowledge_boundaries": {
    "knows": ["string"],
    "doesnt_know": ["string"],
    "can_infer": ["string"]
  },
  "guidelines": {
    "response_style": "string",
    "uncertainty_handling": "string",
    "character_maintenance": "string",
    "additional_rules": ["string"]
  },
  "provenance": {
    "synthetic_marker": "SYNTHETIC_PERSONA_SCRIPT",
    "generated_at": "ISO 8601 timestamp",
    "generator_version": "string",
    "source_persona_id": "string"
  }
}
```

## Troubleshooting

### "Script generation blocked by privacy audit"

**Cause**: Generated script contains potential source data leakage.

**Solutions**:
1. Reduce persona detail (remove specific quotes)
2. Increase threshold: `--threshold 0.15`
3. Review persona for overly specific content

### "No JSON files found"

**Cause**: Batch command can't find persona files.

**Solutions**:
1. Check directory path
2. Ensure files have `.json` extension
3. Verify persona files are valid JSON

### "Unknown format: X"

**Cause**: Invalid format specified.

**Valid formats**:
- `character_card`
- `system_prompt`
- `jinja2_template`

## Best Practices

### 1. Use System Prompts for Quick Conversations

```bash
persona script generate persona.json --format system_prompt
```

Copy-paste into ChatGPT/Claude for immediate use.

### 2. Use Character Cards for Sharing

```bash
persona script batch ./personas --format character_card --yaml
```

YAML is more human-readable for team collaboration.

### 3. Keep Privacy Strict by Default

Don't lower threshold unless you have a specific reason:

```bash
# Good (default)
persona script generate persona.json

# Only if needed
persona script generate persona.json --threshold 0.15
```

### 4. Batch Process for Efficiency

```bash
# Process all at once
persona script batch ./outputs/exp-001 --output ./scripts
```

Faster than generating one at a time.

### 5. Document Your Context

When sharing scripts, include context:

```bash
mkdir -p scripts/user-research-2024
persona script batch ./personas \
    --output scripts/user-research-2024 \
    --format system_prompt

echo "Generated: $(date)" > scripts/user-research-2024/README.txt
echo "Source: user-interviews-dec-2024" >> scripts/user-research-2024/README.txt
```

## Examples

### Example 1: User Research Interview Simulation

```bash
# Generate multiple interview subjects
persona script batch ./outputs/interview-study \
    --output ./interview-scripts \
    --format system_prompt

# Each file is a different "interview subject"
# Researchers paste into ChatGPT and conduct simulated interviews
```

### Example 2: Design Validation

```bash
# Generate character card
persona script generate ./persona-sarah.json \
    --format character_card \
    -o sarah-card.json

# Use in design workshop
# "How would Sarah react to this feature?"
# Load card, review pain points and goals
```

### Example 3: Training Materials

```bash
# Generate scripts in YAML for readability
persona script batch ./training-personas \
    --format character_card \
    --yaml \
    --output ./training-materials

# Include in documentation
# Team learns to empathise with different user types
```

## Related Documentation

- [Persona Generation Guide](persona-generation.md)
- [Privacy Considerations](../explanation/privacy-considerations.md)
- [Character Card Schema](../reference/character-card-schema.md)
- [Scripts API Reference](../reference/api.md#scripts-api)

---

**Next Steps**:
- Generate your first script: `persona script generate`
- Explore different formats
- Try simulated conversations with LLMs
