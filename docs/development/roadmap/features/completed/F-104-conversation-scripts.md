# F-104: Conversation Scripts

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-006, UC-008 |
| **Milestone** | v1.1.0 |
| **Priority** | P1 |
| **Category** | Output |

## Problem Statement

Generated personas are static documents. To use them for user research simulation, empathy-building, or design validation, practitioners need **conversation scripts** that can be fed into LLMs to "have a conversation" with the persona. However, naive approaches risk exposing actual source data through direct quotes, creating privacy and ethical concerns.

## Design Approach

- Generate privacy-preserving LLM conversation scripts from personas
- Abstract source data into patterns (never expose raw quotes)
- Three output formats: Character Card, System Prompt, Jinja2 Template
- Mandatory privacy audit before output
- Knowledge boundaries: knows, doesn't know, can infer

### Key Components

1. **Abstraction Engine**
   - QuoteAbstractor: Extract linguistic features without exposing quotes
   - ScenarioGeneraliser: Abstract specific incidents into patterns
   - BehaviourAbstractor: Derive tendencies from actions
   - CharacterSynthesiser: Infer personality traits

2. **Privacy Audit**
   - Embedding similarity check for paraphrase detection
   - Leakage scoring (must be < 0.1 to pass)
   - Blocks output if audit fails

3. **Output Formats**
   - Character Card (JSON/YAML) - default
   - System Prompt (text) - single comprehensive prompt
   - Jinja2 Template - with conversation context slots

### Character Card Schema

```json
{
  "id": "script-abc12345",
  "identity": {
    "name": "Sarah Chen",
    "title": "The Mobile Professional",
    "demographics_summary": "32-year-old marketing manager..."
  },
  "psychological_profile": {
    "goals": [...],
    "motivations": [...],
    "pain_points": [...],
    "personality_traits": ["efficiency-focused", "tech-savvy"],
    "flaws": ["impatient with slow systems"]
  },
  "communication_style": {
    "tone": "professional but frustrated",
    "vocabulary_level": "professional",
    "speech_patterns": ["uses industry jargon", "direct and concise"]
  },
  "knowledge_boundaries": {
    "knows": ["mobile app usage patterns", "commute workflows"],
    "doesnt_know": ["backend implementation", "competitor pricing"],
    "can_infer": ["general market trends"]
  },
  "guidelines": {
    "response_style": "Answer as Sarah would, staying in character",
    "uncertainty_handling": "Admit when unsure, don't fabricate",
    "character_maintenance": "If drifting, return to core traits"
  },
  "provenance": {
    "synthetic_marker": "SYNTHETIC_PERSONA_SCRIPT",
    "generated_at": "2025-12-14T10:30:00Z"
  }
}
```

## Implementation Tasks

- [x] Create script_generation module
- [x] Implement QuoteAbstractor
- [x] Implement ScenarioGeneraliser
- [x] Implement BehaviourAbstractor
- [x] Implement CharacterSynthesiser
- [x] Implement PrivacyAuditor with embedding similarity
- [x] Create CharacterCardFormatter
- [x] Create SystemPromptFormatter
- [x] Create Jinja2TemplateFormatter
- [x] Add CLI command: `persona script generate`
- [x] Add CLI command: `persona script batch`
- [x] Add `--format` option (character_card, system_prompt, template)
- [x] Add `--yaml` option for YAML output
- [x] Add `--threshold` option for privacy configuration
- [x] Write comprehensive privacy tests (64 tests)
- [x] Write unit tests for core functionality
- [x] Write CLI command tests (18 tests)
- [x] Create user documentation guide

## Success Criteria

- [x] Scripts generated without ANY source quote leakage ✅
- [x] Privacy audit catches 100% of direct quote matches ✅
- [x] Privacy audit catches >90% of paraphrased matches ✅
- [x] All three output formats work correctly ✅
- [x] CLI commands documented and tested ✅
- [x] Test coverage ≥ 90% (achieved 100% on core scripts module) ✅

## Implementation Summary

**Completed**: 2025-12-15

The conversation scripts feature has been fully implemented with:

1. **Core Module** (`src/persona/core/scripts/`)
   - 5 abstractor classes for privacy-preserving transformation
   - Privacy auditor with leakage detection
   - 3 output formatters (Character Card, System Prompt, Jinja2)
   - Complete data models for character cards

2. **CLI Commands** (`src/persona/ui/commands/script.py`)
   - `persona script generate` - Single persona script generation
   - `persona script batch` - Batch processing of multiple personas
   - Format options: character_card (JSON/YAML), system_prompt, jinja2_template
   - Privacy threshold configuration

3. **Testing**
   - 64 core module tests (100% coverage)
   - 18 CLI command tests
   - Privacy audit tests verifying leakage detection

4. **Documentation**
   - Comprehensive user guide with examples
   - Workflow documentation
   - Privacy protection explanation

## Dependencies

- F-004: Persona generation pipeline
- F-024: Evidence linking (for confidence levels)
- F-005: Output formatting

---

## Related Documentation

- [Milestone v1.1.0](../../milestones/v1.1.0.md)
- [Conversation Scripts Guide](../../../../guides/conversation-scripts.md)
- [Privacy Considerations](../../../explanation/privacy-considerations.md)
- [Character Card Schema](../../../../reference/character-card-schema.md)

