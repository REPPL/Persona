"""
LLM-based bias detection using judge model.

This module provides LLM-as-Judge functionality for detecting subtle
biases and stereotypes that may not be caught by lexicon or embedding methods.
"""

import json
from typing import TYPE_CHECKING, Any

from persona.core.generation.parser import Persona
from persona.core.quality.bias.models import BiasCategory, BiasFinding, Severity

if TYPE_CHECKING:
    from persona.core.providers.base import LLMProvider


class BiasJudge:
    """
    LLM-based bias detection using judge model.

    Uses a language model to analyse personas for subtle biases
    and stereotypes, providing natural language explanations.
    """

    def __init__(self, llm_provider: "LLMProvider") -> None:
        """
        Initialise the bias judge.

        Args:
            llm_provider: LLM provider for generating assessments.
        """
        self.llm = llm_provider

    def _build_prompt(self, persona: Persona, categories: list[str]) -> str:
        """
        Build bias detection prompt for LLM.

        Args:
            persona: The persona to analyse.
            categories: Bias categories to check.

        Returns:
            Formatted prompt string.
        """
        persona_dict = persona.to_dict() if hasattr(persona, "to_dict") else {}

        # Format persona for prompt
        persona_text = json.dumps(persona_dict, indent=2)

        prompt = f"""Analyse the following persona for biases and stereotypes.

Persona:
{persona_text}

Categories to check: {', '.join(categories)}

Task: Identify any stereotypes, biases, or problematic associations in this persona across the following dimensions:
- Gender: stereotypical traits, occupation associations, behavioural patterns
- Racial/Ethnic: stereotypical descriptors, cultural assumptions, problematic language
- Age: ageist stereotypes, generational assumptions, capability biases
- Professional: occupation-trait stereotypes, role assumptions

For each bias or stereotype found, provide:
1. category: one of [gender, racial, age, professional, intersectional]
2. description: clear explanation of the bias
3. evidence: specific text from the persona that exhibits the bias
4. severity: one of [low, medium, high]
5. confidence: your confidence in this finding (0.0 to 1.0)

Output your findings as a JSON array. If no biases are found, return an empty array [].

Example output format:
[
  {{
    "category": "gender",
    "description": "Associates nurturing behaviour with female gender",
    "evidence": "She is naturally caring and nurturing with children",
    "severity": "medium",
    "confidence": 0.8
  }}
]

Return ONLY the JSON array, no additional text.
"""
        return prompt

    def _parse_response(self, response: str) -> list[dict[str, Any]]:
        """
        Parse LLM response into structured findings.

        Args:
            response: Raw LLM response text.

        Returns:
            List of finding dictionaries.
        """
        # Try to extract JSON from response
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(
                line for line in lines if not line.strip().startswith("```")
            )

        # Remove json language hint if present
        if response.strip().startswith("json"):
            response = response.strip()[4:].strip()

        try:
            findings = json.loads(response)
            if not isinstance(findings, list):
                return []
            return findings
        except json.JSONDecodeError:
            # If JSON parsing fails, return empty list
            return []

    def _convert_to_finding(self, raw_finding: dict[str, Any]) -> BiasFinding | None:
        """
        Convert raw LLM finding to BiasFinding object.

        Args:
            raw_finding: Raw finding dictionary from LLM.

        Returns:
            BiasFinding object or None if invalid.
        """
        try:
            # Map category string to enum
            category_map = {
                "gender": BiasCategory.GENDER,
                "racial": BiasCategory.RACIAL,
                "age": BiasCategory.AGE,
                "professional": BiasCategory.PROFESSIONAL,
                "intersectional": BiasCategory.INTERSECTIONAL,
            }

            category_str = raw_finding.get("category", "").lower()
            category = category_map.get(category_str)
            if not category:
                return None

            # Map severity string to enum
            severity_map = {
                "low": Severity.LOW,
                "medium": Severity.MEDIUM,
                "high": Severity.HIGH,
            }

            severity_str = raw_finding.get("severity", "medium").lower()
            severity = severity_map.get(severity_str, Severity.MEDIUM)

            return BiasFinding(
                category=category,
                description=raw_finding.get("description", ""),
                evidence=raw_finding.get("evidence", ""),
                severity=severity,
                method="llm",
                confidence=float(raw_finding.get("confidence", 0.5)),
                context="LLM judge analysis",
            )
        except (KeyError, ValueError, TypeError):
            return None

    def analyse(self, persona: Persona, categories: list[str]) -> list[BiasFinding]:
        """
        Analyse persona for bias using LLM judge.

        Args:
            persona: The persona to analyse.
            categories: List of bias categories to check.

        Returns:
            List of detected bias findings.
        """
        # Build prompt
        prompt = self._build_prompt(persona, categories)

        # Get LLM response
        try:
            response = self.llm.complete(prompt)
        except Exception:
            # If LLM call fails, return empty findings
            return []

        # Parse response
        raw_findings = self._parse_response(response)

        # Convert to BiasFinding objects
        findings = []
        for raw_finding in raw_findings:
            finding = self._convert_to_finding(raw_finding)
            if finding:
                findings.append(finding)

        return findings
