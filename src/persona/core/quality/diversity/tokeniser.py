"""
Text extraction and tokenisation for lexical diversity analysis.

This module provides utilities to extract text content from personas
and tokenise it for diversity analysis.
"""

import re
from typing import Any

from persona.core.generation.parser import Persona


def extract_persona_text(persona: Persona) -> str:
    """
    Extract all text content from a persona.

    Combines name, demographics, goals, pain points, behaviours, and quotes
    into a single text string for analysis.

    Args:
        persona: The persona to extract text from.

    Returns:
        Combined text string.
    """
    parts: list[str] = []

    # Add name
    if persona.name:
        parts.append(persona.name)

    # Add demographics values
    if persona.demographics:
        for value in persona.demographics.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, (list, tuple)):
                parts.extend(str(v) for v in value)
            elif value is not None:
                parts.append(str(value))

    # Add goals
    if persona.goals:
        parts.extend(persona.goals)

    # Add pain points
    if persona.pain_points:
        parts.extend(persona.pain_points)

    # Add behaviours
    if persona.behaviours:
        parts.extend(persona.behaviours)

    # Add quotes
    if persona.quotes:
        parts.extend(persona.quotes)

    # Add additional fields (if they are strings or lists)
    if persona.additional:
        for value in persona.additional.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list):
                parts.extend(str(v) for v in value)

    return " ".join(parts)


def tokenise(text: str) -> list[str]:
    """
    Tokenise text for lexical diversity analysis.

    Performs case normalisation and splits on word boundaries.
    Removes punctuation and filters out short tokens.

    Args:
        text: Text to tokenise.

    Returns:
        List of normalised tokens.
    """
    # Convert to lowercase
    text = text.lower()

    # Replace contractions to preserve them as single tokens
    contractions = {
        "i'm": "i am",
        "i've": "i have",
        "i'd": "i would",
        "i'll": "i will",
        "you're": "you are",
        "you've": "you have",
        "you'd": "you would",
        "you'll": "you will",
        "he's": "he is",
        "she's": "she is",
        "it's": "it is",
        "we're": "we are",
        "we've": "we have",
        "we'd": "we would",
        "we'll": "we will",
        "they're": "they are",
        "they've": "they have",
        "they'd": "they would",
        "they'll": "they will",
        "isn't": "is not",
        "aren't": "are not",
        "wasn't": "was not",
        "weren't": "were not",
        "hasn't": "has not",
        "haven't": "have not",
        "hadn't": "had not",
        "doesn't": "does not",
        "don't": "do not",
        "didn't": "did not",
        "won't": "will not",
        "wouldn't": "would not",
        "can't": "cannot",
        "couldn't": "could not",
        "shouldn't": "should not",
        "mightn't": "might not",
        "mustn't": "must not",
    }

    for contraction, expansion in contractions.items():
        text = text.replace(contraction, expansion)

    # Extract word tokens (alphanumeric sequences)
    tokens = re.findall(r"\b[a-z0-9]+\b", text)

    # Filter out very short tokens (< 2 characters) and pure numbers
    tokens = [
        t for t in tokens
        if len(t) >= 2 and not t.isdigit()
    ]

    return tokens
