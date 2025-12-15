"""
Lexical diversity analyser for personas.

This module provides the main analyser class that orchestrates
text extraction, tokenisation, and metric calculation.
"""

from collections import Counter

from persona.core.generation.parser import Persona
from persona.core.quality.diversity.metrics import (
    calculate_hapax_ratio,
    calculate_mattr,
    calculate_mtld,
    calculate_ttr,
    interpret_mtld,
)
from persona.core.quality.diversity.models import (
    BatchDiversityReport,
    DiversityConfig,
    DiversityReport,
    InterpretationLevel,
)
from persona.core.quality.diversity.tokeniser import extract_persona_text, tokenise


class LexicalDiversityAnalyser:
    """
    Analyse lexical diversity of personas.

    Provides comprehensive lexical diversity analysis including:
    - TTR (Type-Token Ratio)
    - MATTR (Moving-Average Type-Token Ratio)
    - MTLD (Measure of Textual Lexical Diversity)
    - Hapax Ratio (proportion of words appearing once)

    Example:
        analyser = LexicalDiversityAnalyser()
        report = analyser.analyse(persona)
        print(f"MTLD: {report.mtld} ({report.interpretation.value})")

        # Batch analysis
        batch_report = analyser.analyse_batch(personas)
        print(f"Average MTLD: {batch_report.average_mtld}")
    """

    def __init__(self, config: DiversityConfig | None = None) -> None:
        """
        Initialise the lexical diversity analyser.

        Args:
            config: Diversity configuration. Uses defaults if not provided.
        """
        self.config = config or DiversityConfig()

    def analyse(self, persona: Persona) -> DiversityReport:
        """
        Analyse lexical diversity of a single persona.

        Args:
            persona: The persona to analyse.

        Returns:
            DiversityReport with comprehensive metrics.
        """
        # Extract text
        text = extract_persona_text(persona)

        # Tokenise
        tokens = tokenise(text)

        # Calculate metrics
        total_tokens = len(tokens)
        unique_tokens = len(set(tokens))

        if total_tokens >= self.config.min_tokens:
            ttr = calculate_ttr(tokens)
            mattr = calculate_mattr(tokens, self.config.mattr_window_size)
            mtld = calculate_mtld(tokens, self.config.mtld_threshold)
            hapax_ratio = calculate_hapax_ratio(tokens)
        else:
            # Not enough tokens for reliable analysis
            ttr = calculate_ttr(tokens) if tokens else 0.0
            mattr = 0.0
            mtld = 0.0
            hapax_ratio = 0.0

        # Interpret MTLD
        interpretation_str = interpret_mtld(mtld)
        interpretation = InterpretationLevel(interpretation_str)

        # Calculate token frequency
        token_frequency = dict(Counter(tokens))

        return DiversityReport(
            persona_id=persona.id,
            persona_name=persona.name,
            total_tokens=total_tokens,
            unique_tokens=unique_tokens,
            ttr=ttr,
            mattr=mattr,
            mtld=mtld,
            hapax_ratio=hapax_ratio,
            interpretation=interpretation,
            token_frequency=token_frequency,
        )

    def analyse_batch(self, personas: list[Persona]) -> BatchDiversityReport:
        """
        Analyse lexical diversity for multiple personas.

        Args:
            personas: List of personas to analyse.

        Returns:
            BatchDiversityReport with individual and aggregate metrics.
        """
        if not personas:
            return BatchDiversityReport(
                reports=[],
                average_ttr=0.0,
                average_mattr=0.0,
                average_mtld=0.0,
                average_hapax_ratio=0.0,
            )

        # Analyse each persona
        reports = [self.analyse(persona) for persona in personas]

        # Calculate averages
        average_ttr = sum(r.ttr for r in reports) / len(reports)
        average_mattr = sum(r.mattr for r in reports) / len(reports)
        average_mtld = sum(r.mtld for r in reports) / len(reports)
        average_hapax_ratio = sum(r.hapax_ratio for r in reports) / len(reports)

        return BatchDiversityReport(
            reports=reports,
            average_ttr=average_ttr,
            average_mattr=average_mattr,
            average_mtld=average_mtld,
            average_hapax_ratio=average_hapax_ratio,
        )
