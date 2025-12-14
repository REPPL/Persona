# F-086: Conversation Scripts

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-006, UC-008 |
| **Milestone** | v0.4.0 |
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

- [ ] Create script_generation module
- [ ] Implement QuoteAbstractor
- [ ] Implement ScenarioGeneraliser
- [ ] Implement BehaviourAbstractor
- [ ] Implement CharacterSynthesiser
- [ ] Implement PrivacyAuditor with embedding similarity
- [ ] Create CharacterCardFormatter
- [ ] Create SystemPromptFormatter
- [ ] Create Jinja2TemplateFormatter
- [ ] Add CLI command: `persona script generate`
- [ ] Add `--format` option (character_card, system_prompt, template)
- [ ] Write comprehensive privacy tests
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Create user documentation

## Success Criteria

- [ ] Scripts generated without ANY source quote leakage
- [ ] Privacy audit catches 100% of direct quote matches
- [ ] Privacy audit catches >90% of paraphrased matches
- [ ] All three output formats work correctly
- [ ] CLI commands documented and tested
- [ ] Test coverage ≥ 90% (critical feature)

## Dependencies

- F-004: Persona generation pipeline
- F-024: Evidence linking (for confidence levels)
- F-005: Output formatting

---

## Related Documentation

- [Milestone v0.4.0](../../milestones/v0.4.0.md)
- [Persona Schema](../../../reference/persona-schema.md)
- [Privacy Considerations](../../../explanation/privacy-considerations.md)

