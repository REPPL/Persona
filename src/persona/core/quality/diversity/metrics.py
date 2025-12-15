"""
Lexical diversity metric calculations.

This module implements the core algorithms for calculating various
lexical diversity measures.
"""

from collections import Counter


def calculate_ttr(tokens: list[str]) -> float:
    """
    Calculate Type-Token Ratio.

    TTR = unique_tokens / total_tokens

    Args:
        tokens: List of tokens.

    Returns:
        TTR value (0-1). Returns 0 if no tokens.
    """
    if not tokens:
        return 0.0

    unique = len(set(tokens))
    total = len(tokens)

    return unique / total


def calculate_mattr(tokens: list[str], window_size: int = 50) -> float:
    """
    Calculate Moving-Average Type-Token Ratio.

    Computes TTR for overlapping windows and averages the results.
    This provides a more stable measure than raw TTR for texts of different lengths.

    Args:
        tokens: List of tokens.
        window_size: Size of sliding window (default: 50).

    Returns:
        MATTR value (0-1). Returns TTR if fewer tokens than window size.
    """
    if not tokens:
        return 0.0

    if len(tokens) < window_size:
        # Fall back to TTR if not enough tokens
        return calculate_ttr(tokens)

    ttr_values: list[float] = []

    # Slide window through tokens
    for i in range(len(tokens) - window_size + 1):
        window = tokens[i : i + window_size]
        window_ttr = calculate_ttr(window)
        ttr_values.append(window_ttr)

    # Average all window TTRs
    return sum(ttr_values) / len(ttr_values) if ttr_values else 0.0


def calculate_mtld(tokens: list[str], threshold: float = 0.72) -> float:
    """
    Calculate Measure of Textual Lexical Diversity (MTLD).

    Implements the McCarthy & Jarvis (2010) algorithm:
    - Count factors (segments) where TTR drops below threshold
    - Calculate bidirectionally (forward and reverse)
    - Average the two directions

    Args:
        tokens: List of tokens.
        threshold: TTR threshold for factor completion (default: 0.72).

    Returns:
        MTLD value. Higher values indicate greater diversity.
        Returns 0 if no tokens.
    """
    if not tokens:
        return 0.0

    if len(tokens) < 10:
        # Not enough tokens for meaningful MTLD
        return 0.0

    # Calculate forward MTLD
    forward_mtld = _mtld_directional(tokens, threshold)

    # Calculate reverse MTLD
    reverse_mtld = _mtld_directional(list(reversed(tokens)), threshold)

    # Average both directions
    return (forward_mtld + reverse_mtld) / 2.0


def _mtld_directional(tokens: list[str], threshold: float) -> float:
    """
    Calculate MTLD in one direction.

    Args:
        tokens: List of tokens (in processing order).
        threshold: TTR threshold for factor completion.

    Returns:
        MTLD value for this direction.
    """
    if not tokens:
        return 0.0

    factors = 0.0
    types: set[str] = set()
    token_count = 0

    for token in tokens:
        types.add(token)
        token_count += 1

        # Calculate current TTR
        ttr = len(types) / token_count

        # Check if we've completed a factor
        if ttr <= threshold:
            factors += 1.0
            # Reset for next factor
            types = set()
            token_count = 0

    # Handle partial factor at the end
    if token_count > 0:
        partial_ttr = len(types) / token_count
        # Add partial factor proportionally
        if partial_ttr < 1.0:  # Avoid division by zero
            partial_factor = (1.0 - partial_ttr) / (1.0 - threshold)
            factors += partial_factor

    # Calculate MTLD (average factor length)
    if factors > 0:
        return len(tokens) / factors
    else:
        # No factors completed (very high diversity)
        return float(len(tokens))


def calculate_hapax_ratio(tokens: list[str]) -> float:
    """
    Calculate hapax legomena ratio.

    Hapax legomena are words that appear exactly once.
    Higher ratios indicate greater lexical richness.

    Args:
        tokens: List of tokens.

    Returns:
        Hapax ratio (0-1). Returns 0 if no tokens.
    """
    if not tokens:
        return 0.0

    # Count token frequencies
    frequency = Counter(tokens)

    # Count hapax legomena (frequency = 1)
    hapax_count = sum(1 for count in frequency.values() if count == 1)

    return hapax_count / len(tokens)


def interpret_mtld(mtld: float) -> str:
    """
    Interpret MTLD score into a human-readable level.

    Thresholds:
    - < 30: poor
    - 30-50: below_average
    - 50-70: average
    - 70-100: good
    - > 100: excellent

    Args:
        mtld: MTLD score.

    Returns:
        Interpretation level as string.
    """
    if mtld < 30:
        return "poor"
    elif mtld < 50:
        return "below_average"
    elif mtld < 70:
        return "average"
    elif mtld < 100:
        return "good"
    else:
        return "excellent"
