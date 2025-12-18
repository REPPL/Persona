"""
Data models for conversation scripts.

This module defines the schema for conversation script output,
including character cards, communication styles, and knowledge boundaries.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import yaml


class ScriptFormat(Enum):
    """Available script output formats."""

    CHARACTER_CARD = "character_card"
    SYSTEM_PROMPT = "system_prompt"
    JINJA2_TEMPLATE = "jinja2_template"


@dataclass
class Identity:
    """Identity information for a character."""

    name: str
    title: str = ""
    demographics_summary: str = ""


@dataclass
class PsychologicalProfile:
    """Psychological profile derived from persona."""

    goals: list[str] = field(default_factory=list)
    motivations: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    personality_traits: list[str] = field(default_factory=list)
    flaws: list[str] = field(default_factory=list)


@dataclass
class CommunicationStyle:
    """Communication style characteristics."""

    tone: str = "neutral"
    vocabulary_level: str = "professional"
    speech_patterns: list[str] = field(default_factory=list)


@dataclass
class KnowledgeBoundaries:
    """Knowledge boundaries for the character."""

    knows: list[str] = field(default_factory=list)
    doesnt_know: list[str] = field(default_factory=list)
    can_infer: list[str] = field(default_factory=list)


@dataclass
class Guidelines:
    """Guidelines for LLM behaviour when roleplaying."""

    response_style: str = "Answer as this character would, staying in character"
    uncertainty_handling: str = "Admit when unsure, don't fabricate"
    character_maintenance: str = "If drifting, return to core traits"
    additional_rules: list[str] = field(default_factory=list)


@dataclass
class Provenance:
    """Provenance information for the script."""

    synthetic_marker: str = "SYNTHETIC_PERSONA_SCRIPT"
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    generator_version: str = "0.4.0"
    source_persona_id: str = ""


@dataclass
class CharacterCard:
    """
    Complete character card for conversation scripts.

    This is the primary output format for conversation scripts,
    containing all information needed for an LLM to roleplay
    as the character.
    """

    id: str
    identity: Identity
    psychological_profile: PsychologicalProfile
    communication_style: CommunicationStyle
    knowledge_boundaries: KnowledgeBoundaries
    guidelines: Guidelines
    provenance: Provenance

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "identity": {
                "name": self.identity.name,
                "title": self.identity.title,
                "demographics_summary": self.identity.demographics_summary,
            },
            "psychological_profile": {
                "goals": self.psychological_profile.goals,
                "motivations": self.psychological_profile.motivations,
                "pain_points": self.psychological_profile.pain_points,
                "personality_traits": self.psychological_profile.personality_traits,
                "flaws": self.psychological_profile.flaws,
            },
            "communication_style": {
                "tone": self.communication_style.tone,
                "vocabulary_level": self.communication_style.vocabulary_level,
                "speech_patterns": self.communication_style.speech_patterns,
            },
            "knowledge_boundaries": {
                "knows": self.knowledge_boundaries.knows,
                "doesnt_know": self.knowledge_boundaries.doesnt_know,
                "can_infer": self.knowledge_boundaries.can_infer,
            },
            "guidelines": {
                "response_style": self.guidelines.response_style,
                "uncertainty_handling": self.guidelines.uncertainty_handling,
                "character_maintenance": self.guidelines.character_maintenance,
                "additional_rules": self.guidelines.additional_rules,
            },
            "provenance": {
                "synthetic_marker": self.provenance.synthetic_marker,
                "generated_at": self.provenance.generated_at,
                "generator_version": self.provenance.generator_version,
                "source_persona_id": self.provenance.source_persona_id,
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_yaml(self) -> str:
        """Convert to YAML string."""
        return yaml.dump(
            self.to_dict(),
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterCard":
        """Create from dictionary."""
        identity_data = data.get("identity", {})
        profile_data = data.get("psychological_profile", {})
        style_data = data.get("communication_style", {})
        knowledge_data = data.get("knowledge_boundaries", {})
        guidelines_data = data.get("guidelines", {})
        provenance_data = data.get("provenance", {})

        return cls(
            id=data.get("id", ""),
            identity=Identity(
                name=identity_data.get("name", ""),
                title=identity_data.get("title", ""),
                demographics_summary=identity_data.get("demographics_summary", ""),
            ),
            psychological_profile=PsychologicalProfile(
                goals=profile_data.get("goals", []),
                motivations=profile_data.get("motivations", []),
                pain_points=profile_data.get("pain_points", []),
                personality_traits=profile_data.get("personality_traits", []),
                flaws=profile_data.get("flaws", []),
            ),
            communication_style=CommunicationStyle(
                tone=style_data.get("tone", "neutral"),
                vocabulary_level=style_data.get("vocabulary_level", "professional"),
                speech_patterns=style_data.get("speech_patterns", []),
            ),
            knowledge_boundaries=KnowledgeBoundaries(
                knows=knowledge_data.get("knows", []),
                doesnt_know=knowledge_data.get("doesnt_know", []),
                can_infer=knowledge_data.get("can_infer", []),
            ),
            guidelines=Guidelines(
                response_style=guidelines_data.get("response_style", ""),
                uncertainty_handling=guidelines_data.get("uncertainty_handling", ""),
                character_maintenance=guidelines_data.get("character_maintenance", ""),
                additional_rules=guidelines_data.get("additional_rules", []),
            ),
            provenance=Provenance(
                synthetic_marker=provenance_data.get("synthetic_marker", ""),
                generated_at=provenance_data.get("generated_at", ""),
                generator_version=provenance_data.get("generator_version", ""),
                source_persona_id=provenance_data.get("source_persona_id", ""),
            ),
        )
