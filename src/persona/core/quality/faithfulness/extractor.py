"""
Claim extraction from personas.

This module provides functionality for extracting factual claims
from persona attributes using LLM-based analysis.
"""

import json
import re
from typing import Any

from persona.core.generation.parser import Persona
from persona.core.providers.base import LLMProvider
from persona.core.quality.faithfulness.models import Claim, ClaimType


class ClaimExtractor:
    """
    Extract factual claims from persona attributes.

    Uses LLM to identify verifiable claims from persona data,
    categorising them by type (factual, opinion, preference, etc.).

    Example:
        extractor = ClaimExtractor(llm_provider)
        claims = extractor.extract_claims(persona)
        for claim in claims:
            print(f"{claim.claim_type}: {claim.text}")
    """

    # Prompt template for claim extraction
    EXTRACTION_PROMPT = """Analyse the following persona and extract all verifiable claims.
For each claim, identify:
1. The claim text (concise statement)
2. The source field (where it came from)
3. The claim type (factual, opinion, preference, behaviour, quote, demographic, goal, pain_point)

Persona:
{persona_json}

Extract claims as JSON array:
[
  {{
    "text": "The claim text",
    "source_field": "demographics.age",
    "claim_type": "factual",
    "context": "Additional context if relevant"
  }},
  ...
]

Focus on:
- Factual statements (age, occupation, location)
- Demographic information
- Stated preferences and opinions
- Reported behaviours
- Goals and pain points
- Direct quotes

Return ONLY the JSON array, no additional text."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> None:
        """
        Initialise the claim extractor.

        Args:
            llm_provider: LLM provider for claim extraction.
            model: Model to use (defaults to provider default).
            temperature: Sampling temperature (lower = more deterministic).
        """
        self.llm_provider = llm_provider
        self.model = model
        self.temperature = temperature

    def extract_claims(self, persona: Persona) -> list[Claim]:
        """
        Extract all verifiable claims from a persona.

        Args:
            persona: The persona to analyse.

        Returns:
            List of extracted claims.

        Raises:
            RuntimeError: If LLM extraction fails.
        """
        # First try simple extraction (no LLM)
        simple_claims = self._extract_simple_claims(persona)

        # Then try LLM-based extraction for complex analysis
        try:
            llm_claims = self._extract_with_llm(persona)
            # Combine and deduplicate
            return self._deduplicate_claims(simple_claims + llm_claims)
        except Exception:
            # Fall back to simple extraction if LLM fails
            return simple_claims

    def _extract_simple_claims(self, persona: Persona) -> list[Claim]:
        """
        Extract claims using simple rule-based extraction.

        This provides a fallback if LLM extraction fails.
        """
        claims: list[Claim] = []

        # Demographics claims
        for key, value in persona.demographics.items():
            if value:
                claims.append(
                    Claim(
                        text=f"{key}: {value}",
                        source_field=f"demographics.{key}",
                        claim_type=ClaimType.DEMOGRAPHIC,
                        context=str(value),
                    )
                )

        # Goals
        for idx, goal in enumerate(persona.goals):
            claims.append(
                Claim(
                    text=goal,
                    source_field=f"goals[{idx}]",
                    claim_type=ClaimType.GOAL,
                    context=goal,
                )
            )

        # Pain points
        for idx, pain in enumerate(persona.pain_points):
            claims.append(
                Claim(
                    text=pain,
                    source_field=f"pain_points[{idx}]",
                    claim_type=ClaimType.PAIN_POINT,
                    context=pain,
                )
            )

        # Behaviours
        for idx, behaviour in enumerate(persona.behaviours):
            claims.append(
                Claim(
                    text=behaviour,
                    source_field=f"behaviours[{idx}]",
                    claim_type=ClaimType.BEHAVIOUR,
                    context=behaviour,
                )
            )

        # Quotes
        for idx, quote in enumerate(persona.quotes):
            claims.append(
                Claim(
                    text=quote,
                    source_field=f"quotes[{idx}]",
                    claim_type=ClaimType.QUOTE,
                    context=quote,
                )
            )

        return claims

    def _extract_with_llm(self, persona: Persona) -> list[Claim]:
        """
        Extract claims using LLM analysis.

        Args:
            persona: The persona to analyse.

        Returns:
            List of claims extracted by LLM.
        """
        # Build prompt
        persona_json = json.dumps(persona.to_dict(), indent=2)
        prompt = self.EXTRACTION_PROMPT.format(persona_json=persona_json)

        # Call LLM
        response = self.llm_provider.generate(
            prompt=prompt,
            model=self.model,
            temperature=self.temperature,
            max_tokens=2048,
        )

        # Parse response
        claims_data = self._parse_llm_response(response.content)

        # Convert to Claim objects
        claims: list[Claim] = []
        for item in claims_data:
            try:
                claim_type_str = item.get("claim_type", "factual").lower()
                claim_type = self._parse_claim_type(claim_type_str)

                claims.append(
                    Claim(
                        text=item.get("text", ""),
                        source_field=item.get("source_field", "unknown"),
                        claim_type=claim_type,
                        context=item.get("context", ""),
                    )
                )
            except (KeyError, ValueError):
                # Skip malformed claims
                continue

        return claims

    def _parse_llm_response(self, content: str) -> list[dict[str, Any]]:
        """
        Parse LLM response to extract claims JSON.

        Args:
            content: LLM response content.

        Returns:
            List of claim dictionaries.
        """
        # Try to find JSON array in response
        content = content.strip()

        # Remove markdown code blocks if present
        json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
        if json_match:
            content = json_match.group(1)

        # Try to parse as JSON
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "claims" in data:
                return data["claims"]
            return []
        except json.JSONDecodeError:
            # Try to find JSON array in text
            array_match = re.search(r"\[(.*)\]", content, re.DOTALL)
            if array_match:
                try:
                    return json.loads("[" + array_match.group(1) + "]")
                except json.JSONDecodeError:
                    pass
            return []

    def _parse_claim_type(self, type_str: str) -> ClaimType:
        """
        Parse claim type string to ClaimType enum.

        Args:
            type_str: Claim type as string.

        Returns:
            ClaimType enum value.
        """
        type_map = {
            "factual": ClaimType.FACTUAL,
            "opinion": ClaimType.OPINION,
            "preference": ClaimType.PREFERENCE,
            "behaviour": ClaimType.BEHAVIOUR,
            "behavior": ClaimType.BEHAVIOUR,  # American spelling
            "quote": ClaimType.QUOTE,
            "demographic": ClaimType.DEMOGRAPHIC,
            "goal": ClaimType.GOAL,
            "pain_point": ClaimType.PAIN_POINT,
            "pain point": ClaimType.PAIN_POINT,
        }
        return type_map.get(type_str.lower(), ClaimType.FACTUAL)

    def _deduplicate_claims(self, claims: list[Claim]) -> list[Claim]:
        """
        Remove duplicate claims based on text similarity.

        Args:
            claims: List of claims potentially with duplicates.

        Returns:
            Deduplicated list of claims.
        """
        seen_texts: set[str] = set()
        unique_claims: list[Claim] = []

        for claim in claims:
            # Normalise text for comparison
            normalised = claim.text.lower().strip()
            if normalised not in seen_texts and normalised:
                seen_texts.add(normalised)
                unique_claims.append(claim)

        return unique_claims
