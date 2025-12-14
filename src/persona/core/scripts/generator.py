"""
Conversation script generator.

This module provides the main generator for creating privacy-preserving
conversation scripts from personas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid

from persona.core.generation.parser import Persona
from persona.core.scripts.abstractors import (
    BehaviourAbstractor,
    CharacterSynthesiser,
    QuoteAbstractor,
    ScenarioGeneraliser,
)
from persona.core.scripts.models import (
    CharacterCard,
    CommunicationStyle,
    Guidelines,
    Identity,
    KnowledgeBoundaries,
    Provenance,
    PsychologicalProfile,
    ScriptFormat,
)
from persona.core.scripts.privacy import (
    PrivacyAuditResult,
    PrivacyAuditor,
    PrivacyConfig,
    PrivacyLeakageError,
)


@dataclass
class ScriptGenerationResult:
    """Result of script generation."""

    character_card: CharacterCard
    privacy_audit: PrivacyAuditResult
    format: ScriptFormat
    output: str
    blocked: bool = False
    error: str = ""


class ConversationScriptGenerator:
    """
    Generate privacy-preserving conversation scripts from personas.

    Creates character cards and other formats suitable for LLM roleplay,
    with mandatory privacy auditing to prevent source data leakage.

    CRITICAL: Output is BLOCKED if privacy audit fails.

    Example:
        generator = ConversationScriptGenerator()
        result = generator.generate(persona)
        if result.blocked:
            print(f"Generation blocked: {result.error}")
        else:
            print(result.output)
    """

    def __init__(
        self,
        privacy_config: PrivacyConfig | None = None,
        block_on_failure: bool = True,
    ) -> None:
        """
        Initialise generator.

        Args:
            privacy_config: Configuration for privacy auditing.
            block_on_failure: Whether to block output on privacy failure.
        """
        self._privacy_config = privacy_config or PrivacyConfig()
        self._block_on_failure = block_on_failure

        # Initialise abstractors
        self._quote_abstractor = QuoteAbstractor()
        self._scenario_generaliser = ScenarioGeneraliser()
        self._behaviour_abstractor = BehaviourAbstractor()
        self._character_synthesiser = CharacterSynthesiser()

        # Initialise auditor
        self._auditor = PrivacyAuditor(self._privacy_config)

    def generate(
        self,
        persona: Persona,
        format: ScriptFormat = ScriptFormat.CHARACTER_CARD,
    ) -> ScriptGenerationResult:
        """
        Generate a conversation script from a persona.

        Args:
            persona: The source persona.
            format: Output format.

        Returns:
            ScriptGenerationResult with output or error.
        """
        # Generate character card
        card = self._generate_character_card(persona)

        # Run privacy audit
        audit_result = self._auditor.audit(card, persona)

        # Check if blocked
        if audit_result.blocked and self._block_on_failure:
            return ScriptGenerationResult(
                character_card=card,
                privacy_audit=audit_result,
                format=format,
                output="",
                blocked=True,
                error=audit_result.details,
            )

        # Format output
        output = self._format_output(card, format)

        return ScriptGenerationResult(
            character_card=card,
            privacy_audit=audit_result,
            format=format,
            output=output,
            blocked=False,
        )

    def _generate_character_card(self, persona: Persona) -> CharacterCard:
        """Generate a character card from persona."""
        # Generate unique script ID
        script_id = f"script-{uuid.uuid4().hex[:8]}"

        # Build identity
        identity = self._build_identity(persona)

        # Build psychological profile
        profile = self._build_psychological_profile(persona)

        # Build communication style
        comm_style = self._build_communication_style(persona)

        # Build knowledge boundaries
        knowledge = self._build_knowledge_boundaries(persona)

        # Build guidelines
        guidelines = self._build_guidelines(persona)

        # Build provenance
        provenance = Provenance(
            source_persona_id=persona.id,
        )

        return CharacterCard(
            id=script_id,
            identity=identity,
            psychological_profile=profile,
            communication_style=comm_style,
            knowledge_boundaries=knowledge,
            guidelines=guidelines,
            provenance=provenance,
        )

    def _build_identity(self, persona: Persona) -> Identity:
        """Build identity from persona."""
        # Generate title from demographics
        title = ""
        if persona.demographics:
            role = persona.demographics.get("role", "")
            if role:
                title = f"The {role}"

        # Generate demographics summary
        demo_parts = []
        if persona.demographics:
            if "age" in persona.demographics:
                demo_parts.append(f"{persona.demographics['age']} years old")
            if "role" in persona.demographics:
                demo_parts.append(persona.demographics["role"])
            if "experience" in persona.demographics:
                demo_parts.append(f"with {persona.demographics['experience']} experience")

        demographics_summary = ", ".join(demo_parts) if demo_parts else ""

        return Identity(
            name=persona.name,
            title=title,
            demographics_summary=demographics_summary,
        )

    def _build_psychological_profile(self, persona: Persona) -> PsychologicalProfile:
        """Build psychological profile from persona."""
        # Get traits and flaws
        traits, flaws = self._character_synthesiser.get_traits_and_flaws(persona)

        # Abstract goals (don't use raw goals directly to avoid leakage)
        abstracted_goals = []
        for goal in (persona.goals or []):
            # Generalise the goal
            words = goal.lower().split()
            if any(w in words for w in ["streamline", "improve", "enhance"]):
                abstracted_goals.append("seeks efficiency improvements")
            elif any(w in words for w in ["collaborate", "team", "together"]):
                abstracted_goals.append("values collaborative outcomes")
            elif any(w in words for w in ["learn", "grow", "develop"]):
                abstracted_goals.append("pursues personal growth")
            elif any(w in words for w in ["balance", "life"]):
                abstracted_goals.append("seeks work-life harmony")
            elif any(w in words for w in ["quality", "excel"]):
                abstracted_goals.append("strives for excellence")
            else:
                abstracted_goals.append("goal-oriented")

        # Remove duplicates while preserving order
        seen = set()
        unique_goals = []
        for g in abstracted_goals:
            if g not in seen:
                seen.add(g)
                unique_goals.append(g)

        # Abstract pain points
        abstracted_pain_points = []
        for pain in (persona.pain_points or []):
            words = pain.lower().split()
            if any(w in words for w in ["manual", "repetitive", "tedious"]):
                abstracted_pain_points.append("frustrated by manual processes")
            elif any(w in words for w in ["slow", "wait", "delay"]):
                abstracted_pain_points.append("impatient with slow systems")
            elif any(w in words for w in ["complex", "confusing", "unclear"]):
                abstracted_pain_points.append("dislikes unnecessary complexity")
            elif any(w in words for w in ["switch", "interrupt", "distract"]):
                abstracted_pain_points.append("struggles with interruptions")
            else:
                abstracted_pain_points.append("experiences workflow friction")

        # Remove duplicates
        seen = set()
        unique_pain_points = []
        for p in abstracted_pain_points:
            if p not in seen:
                seen.add(p)
                unique_pain_points.append(p)

        # Get motivations from additional fields
        motivations = []
        if persona.additional and "motivations" in persona.additional:
            raw_motivations = persona.additional["motivations"]
            if isinstance(raw_motivations, list):
                # Abstract motivations
                for mot in raw_motivations:
                    mot_lower = mot.lower()
                    if "recognition" in mot_lower:
                        motivations.append("seeks recognition for contributions")
                    elif "success" in mot_lower or "achieve" in mot_lower:
                        motivations.append("driven by achievement")
                    elif "growth" in mot_lower or "learn" in mot_lower:
                        motivations.append("motivated by learning opportunities")
                    elif "impact" in mot_lower:
                        motivations.append("wants to make meaningful impact")
                    else:
                        motivations.append("intrinsically motivated")

        return PsychologicalProfile(
            goals=unique_goals[:5],
            motivations=list(set(motivations))[:3],
            pain_points=unique_pain_points[:5],
            personality_traits=traits[:5],
            flaws=flaws[:3],
        )

    def _build_communication_style(self, persona: Persona) -> CommunicationStyle:
        """Build communication style from persona."""
        # Abstract quotes into speech patterns
        speech_patterns = []
        if persona.quotes:
            quote_result = self._quote_abstractor.abstract(persona.quotes)
            speech_patterns = quote_result.abstracted_content

        # Determine tone from pain points and behaviours
        tone = "professional"
        if persona.pain_points:
            pain_text = " ".join(persona.pain_points).lower()
            if "frustrat" in pain_text or "annoy" in pain_text:
                tone = "professional but frustrated"
            elif "slow" in pain_text or "wait" in pain_text:
                tone = "direct and impatient"

        # Determine vocabulary level from demographics
        vocab_level = "professional"
        if persona.demographics:
            role = persona.demographics.get("role", "").lower()
            if "developer" in role or "engineer" in role:
                vocab_level = "technical"
            elif "executive" in role or "director" in role:
                vocab_level = "executive"

        return CommunicationStyle(
            tone=tone,
            vocabulary_level=vocab_level,
            speech_patterns=speech_patterns[:5],
        )

    def _build_knowledge_boundaries(self, persona: Persona) -> KnowledgeBoundaries:
        """Build knowledge boundaries from persona."""
        knows = []
        doesnt_know = []
        can_infer = []

        # Derive knows from behaviours
        if persona.behaviours:
            behaviour_result = self._behaviour_abstractor.abstract(persona.behaviours)
            for tendency in behaviour_result.abstracted_content:
                if "data" in tendency.lower() or "metric" in tendency.lower():
                    knows.append("data analysis and metrics interpretation")
                if "collaborat" in tendency.lower():
                    knows.append("team collaboration practices")
                if "plan" in tendency.lower():
                    knows.append("project planning methodologies")

        # Derive from demographics
        if persona.demographics:
            role = persona.demographics.get("role", "").lower()
            if "marketing" in role:
                knows.append("marketing strategies and campaigns")
                doesnt_know.append("backend system implementation")
            elif "developer" in role:
                knows.append("software development practices")
                doesnt_know.append("detailed marketing strategy")
            elif "product" in role:
                knows.append("product management frameworks")
                can_infer.append("general market trends")

        # Default boundaries
        if not doesnt_know:
            doesnt_know.append("internal implementation details of unfamiliar systems")

        if not can_infer:
            can_infer.append("general industry trends based on experience")

        return KnowledgeBoundaries(
            knows=list(set(knows))[:5],
            doesnt_know=list(set(doesnt_know))[:3],
            can_infer=list(set(can_infer))[:3],
        )

    def _build_guidelines(self, persona: Persona) -> Guidelines:
        """Build roleplay guidelines."""
        additional_rules = [
            "Respond based on stated knowledge boundaries",
            "Express frustrations constructively when relevant",
            "Maintain consistent personality throughout conversation",
        ]

        return Guidelines(
            response_style=f"Answer as {persona.name} would, staying in character",
            uncertainty_handling="Acknowledge uncertainty based on knowledge boundaries",
            character_maintenance="Return to core traits if conversation drifts",
            additional_rules=additional_rules,
        )

    def _format_output(self, card: CharacterCard, format: ScriptFormat) -> str:
        """Format character card to specified format."""
        if format == ScriptFormat.CHARACTER_CARD:
            return card.to_json()
        elif format == ScriptFormat.SYSTEM_PROMPT:
            return self._format_as_system_prompt(card)
        elif format == ScriptFormat.JINJA2_TEMPLATE:
            return self._format_as_jinja2_template(card)
        else:
            return card.to_json()

    def _format_as_system_prompt(self, card: CharacterCard) -> str:
        """Format card as system prompt."""
        lines = []

        lines.append(f"You are {card.identity.name}, {card.identity.title}.")
        if card.identity.demographics_summary:
            lines.append(f"Background: {card.identity.demographics_summary}")
        lines.append("")

        lines.append("## Personality")
        for trait in card.psychological_profile.personality_traits:
            lines.append(f"- {trait}")
        lines.append("")

        lines.append("## Goals")
        for goal in card.psychological_profile.goals:
            lines.append(f"- {goal}")
        lines.append("")

        lines.append("## Frustrations")
        for pain in card.psychological_profile.pain_points:
            lines.append(f"- {pain}")
        lines.append("")

        lines.append("## Communication Style")
        lines.append(f"Tone: {card.communication_style.tone}")
        lines.append(f"Vocabulary: {card.communication_style.vocabulary_level}")
        for pattern in card.communication_style.speech_patterns:
            lines.append(f"- {pattern}")
        lines.append("")

        lines.append("## Knowledge")
        lines.append("You know about:")
        for item in card.knowledge_boundaries.knows:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("You don't know about:")
        for item in card.knowledge_boundaries.doesnt_know:
            lines.append(f"- {item}")
        lines.append("")

        lines.append("## Guidelines")
        lines.append(card.guidelines.response_style)
        lines.append(card.guidelines.uncertainty_handling)
        lines.append("")

        lines.append(f"[{card.provenance.synthetic_marker}]")

        return "\n".join(lines)

    def _format_as_jinja2_template(self, card: CharacterCard) -> str:
        """Format card as Jinja2 template."""
        template = '''You are {{ identity.name }}, {{ identity.title }}.

{% if context %}
Current context: {{ context }}
{% endif %}

## Core Traits
{% for trait in psychological_profile.personality_traits %}
- {{ trait }}
{% endfor %}

## Goals
{% for goal in psychological_profile.goals %}
- {{ goal }}
{% endfor %}

## Communication
Tone: {{ communication_style.tone }}
{% for pattern in communication_style.speech_patterns %}
- {{ pattern }}
{% endfor %}

## Knowledge Boundaries
Knows: {{ knowledge_boundaries.knows | join(", ") }}
Doesn't know: {{ knowledge_boundaries.doesnt_know | join(", ") }}

{{ guidelines.response_style }}

{% if conversation_history %}
Previous messages:
{% for msg in conversation_history %}
{{ msg.role }}: {{ msg.content }}
{% endfor %}
{% endif %}

[{{ provenance.synthetic_marker }}]
'''
        return template
