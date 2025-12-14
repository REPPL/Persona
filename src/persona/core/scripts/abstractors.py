"""
Abstractors for transforming persona data into privacy-safe patterns.

These abstractors ensure that conversation scripts don't expose
raw quotes or specific incidents from source data.
"""

from dataclasses import dataclass, field
from typing import Any
import re

from persona.core.generation.parser import Persona


@dataclass
class AbstractorResult:
    """Result from an abstraction operation."""

    abstracted_content: list[str]
    confidence: float = 1.0
    source_count: int = 0


class QuoteAbstractor:
    """
    Extract linguistic features without exposing raw quotes.

    Transforms direct quotes into general speech patterns and
    communication characteristics without revealing the original text.

    Example:
        abstractor = QuoteAbstractor()
        result = abstractor.abstract(["I need this done yesterday!"])
        # Returns patterns like "uses urgency language", "direct communication style"
    """

    # Linguistic pattern indicators
    URGENCY_WORDS = {"urgent", "asap", "immediately", "yesterday", "now", "quickly"}
    FRUSTRATION_WORDS = {"frustrated", "annoyed", "hate", "terrible", "awful", "broken"}
    POSITIVE_WORDS = {"love", "great", "excellent", "perfect", "amazing", "wonderful"}
    TECHNICAL_WORDS = {"api", "database", "server", "code", "system", "integration"}
    PROFESSIONAL_WORDS = {"stakeholder", "deliverable", "alignment", "synergy", "metrics"}

    def abstract(self, quotes: list[str]) -> AbstractorResult:
        """
        Abstract quotes into linguistic patterns.

        Args:
            quotes: List of direct quotes.

        Returns:
            AbstractorResult with abstracted patterns.
        """
        if not quotes:
            return AbstractorResult(abstracted_content=[], source_count=0)

        patterns = []

        # Analyze all quotes
        all_text = " ".join(quotes).lower()

        # Detect urgency
        if any(word in all_text for word in self.URGENCY_WORDS):
            patterns.append("uses urgency language")

        # Detect frustration
        if any(word in all_text for word in self.FRUSTRATION_WORDS):
            patterns.append("expresses frustration directly")

        # Detect positive sentiment
        if any(word in all_text for word in self.POSITIVE_WORDS):
            patterns.append("uses positive reinforcement")

        # Detect technical language
        if any(word in all_text for word in self.TECHNICAL_WORDS):
            patterns.append("comfortable with technical terminology")

        # Detect professional jargon
        if any(word in all_text for word in self.PROFESSIONAL_WORDS):
            patterns.append("uses professional/business language")

        # Detect question patterns
        question_count = sum(1 for q in quotes if "?" in q)
        if question_count > len(quotes) / 2:
            patterns.append("frequently asks clarifying questions")

        # Detect length patterns
        avg_length = sum(len(q) for q in quotes) / len(quotes)
        if avg_length < 50:
            patterns.append("prefers concise communication")
        elif avg_length > 150:
            patterns.append("provides detailed explanations")

        # Detect exclamation patterns
        exclamation_count = sum(1 for q in quotes if "!" in q)
        if exclamation_count > len(quotes) / 3:
            patterns.append("uses emphatic expressions")

        return AbstractorResult(
            abstracted_content=patterns,
            confidence=0.8 if patterns else 0.5,
            source_count=len(quotes),
        )


class ScenarioGeneraliser:
    """
    Abstract specific incidents into general patterns.

    Transforms specific events or scenarios into generalised
    behaviour patterns without revealing the original context.

    Example:
        generaliser = ScenarioGeneraliser()
        result = generaliser.generalise(["Stayed up all night to fix a production bug"])
        # Returns patterns like "willing to work extra hours for critical issues"
    """

    def generalise(self, scenarios: list[str]) -> AbstractorResult:
        """
        Generalise specific scenarios into patterns.

        Args:
            scenarios: List of specific scenarios or incidents.

        Returns:
            AbstractorResult with generalised patterns.
        """
        if not scenarios:
            return AbstractorResult(abstracted_content=[], source_count=0)

        patterns = []
        all_text = " ".join(scenarios).lower()

        # Time-related patterns
        if any(word in all_text for word in ["late", "night", "weekend", "overtime", "extra"]):
            patterns.append("willing to invest extra time when needed")

        # Problem-solving patterns
        if any(word in all_text for word in ["fix", "solve", "resolve", "debug", "troubleshoot"]):
            patterns.append("proactive problem-solver")

        # Collaboration patterns
        if any(word in all_text for word in ["team", "collaborate", "together", "help", "support"]):
            patterns.append("values teamwork and collaboration")

        # Learning patterns
        if any(word in all_text for word in ["learn", "research", "study", "understand", "explore"]):
            patterns.append("continuous learner")

        # Leadership patterns
        if any(word in all_text for word in ["lead", "manage", "organize", "coordinate", "delegate"]):
            patterns.append("takes initiative in leadership situations")

        # Quality patterns
        if any(word in all_text for word in ["quality", "detail", "careful", "thorough", "review"]):
            patterns.append("quality-focused approach")

        return AbstractorResult(
            abstracted_content=patterns,
            confidence=0.75 if patterns else 0.5,
            source_count=len(scenarios),
        )


class BehaviourAbstractor:
    """
    Derive general tendencies from specific behaviours.

    Transforms specific behavioural observations into general
    tendencies without revealing specific actions.
    """

    def abstract(self, behaviours: list[str]) -> AbstractorResult:
        """
        Abstract behaviours into tendencies.

        Args:
            behaviours: List of observed behaviours.

        Returns:
            AbstractorResult with abstracted tendencies.
        """
        if not behaviours:
            return AbstractorResult(abstracted_content=[], source_count=0)

        tendencies = []
        all_text = " ".join(behaviours).lower()

        # Morning/routine patterns
        if any(word in all_text for word in ["morning", "first thing", "start", "routine"]):
            tendencies.append("structured daily routine")

        # Multi-tasking patterns
        if any(word in all_text for word in ["multiple", "juggling", "parallel", "simultaneously"]):
            tendencies.append("handles multiple priorities")

        # Communication patterns
        if any(word in all_text for word in ["check", "review", "monitor", "track"]):
            tendencies.append("monitors progress regularly")

        # Collaboration patterns
        if any(word in all_text for word in ["collaborate", "meet", "discuss", "sync"]):
            tendencies.append("collaborative working style")

        # Planning patterns
        if any(word in all_text for word in ["plan", "schedule", "organize", "prioritize"]):
            tendencies.append("plans ahead")

        # Analysis patterns
        if any(word in all_text for word in ["analyz", "dashboard", "data", "metrics", "report"]):
            tendencies.append("data-informed decision maker")

        return AbstractorResult(
            abstracted_content=tendencies,
            confidence=0.8 if tendencies else 0.5,
            source_count=len(behaviours),
        )


class CharacterSynthesiser:
    """
    Infer personality traits from persona data.

    Synthesises personality characteristics from goals, pain points,
    and behaviours without direct attribution.
    """

    def synthesise(self, persona: Persona) -> AbstractorResult:
        """
        Synthesise personality traits from persona.

        Args:
            persona: The persona to analyse.

        Returns:
            AbstractorResult with synthesised traits.
        """
        traits = []
        flaws = []

        # Analyse goals for positive traits
        goals_text = " ".join(persona.goals).lower() if persona.goals else ""

        if "efficien" in goals_text or "streamline" in goals_text:
            traits.append("efficiency-focused")

        if "collaborat" in goals_text or "team" in goals_text:
            traits.append("values collaboration")

        if "learn" in goals_text or "grow" in goals_text:
            traits.append("growth-oriented")

        if "quality" in goals_text or "excel" in goals_text:
            traits.append("excellence-driven")

        if "balance" in goals_text:
            traits.append("seeks balance")

        # Analyse pain points for flaws
        pain_text = " ".join(persona.pain_points).lower() if persona.pain_points else ""

        if "slow" in pain_text or "wait" in pain_text:
            flaws.append("impatient with delays")

        if "manual" in pain_text or "repetit" in pain_text:
            flaws.append("frustrated by inefficiency")

        if "complex" in pain_text or "confus" in pain_text:
            flaws.append("prefers simplicity")

        if "switch" in pain_text or "interrupt" in pain_text:
            flaws.append("disrupted by context switching")

        # Analyse demographics for context
        if persona.demographics:
            role = persona.demographics.get("role", "").lower()
            if "manager" in role:
                traits.append("leadership-oriented")
            if "developer" in role or "engineer" in role:
                traits.append("technically-minded")
            if "design" in role:
                traits.append("visually-oriented")

        # Default traits if none detected
        if not traits:
            traits.append("goal-oriented")

        return AbstractorResult(
            abstracted_content=traits + [f"FLAW: {f}" for f in flaws],
            confidence=0.7,
            source_count=len(persona.goals or []) + len(persona.pain_points or []),
        )

    def get_traits_and_flaws(
        self,
        persona: Persona,
    ) -> tuple[list[str], list[str]]:
        """
        Get separate traits and flaws lists.

        Args:
            persona: The persona to analyse.

        Returns:
            Tuple of (traits, flaws).
        """
        result = self.synthesise(persona)
        traits = []
        flaws = []

        for item in result.abstracted_content:
            if item.startswith("FLAW: "):
                flaws.append(item[6:])
            else:
                traits.append(item)

        return traits, flaws
