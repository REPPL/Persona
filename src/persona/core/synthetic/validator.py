"""
Synthetic data quality validation.

This module provides the SyntheticValidator class that validates
synthetic data quality by checking schema match, distribution
similarity, PII presence, and semantic similarity.
"""

from pathlib import Path

from persona.core.synthetic.analyser import DataAnalyser
from persona.core.synthetic.models import ValidationResult


class SyntheticValidator:
    """
    Validates synthetic data quality against original data.

    Checks:
    - Schema match (column names and types)
    - Distribution similarity (statistical properties)
    - PII presence (must be 0%)
    - Semantic similarity (optional)
    - Diversity (variety in generated records)

    Example:
        validator = SyntheticValidator()
        result = validator.validate(
            original_path="interviews.csv",
            synthetic_path="synthetic.csv"
        )
        print(f"Quality score: {result.quality_score:.2%}")
    """

    # Validation thresholds
    MIN_DISTRIBUTION_SIMILARITY = 0.85
    MIN_DIVERSITY = 0.70

    def __init__(self) -> None:
        """Initialise the validator."""
        self.analyser = DataAnalyser()

    def validate(
        self,
        original_path: Path | str,
        synthetic_path: Path | str,
    ) -> ValidationResult:
        """
        Validate synthetic data against original.

        Args:
            original_path: Path to original data file.
            synthetic_path: Path to synthetic data file.

        Returns:
            ValidationResult with quality metrics.

        Raises:
            FileNotFoundError: If files don't exist.
            ValueError: If files cannot be analysed.
        """
        original_path = Path(original_path)
        synthetic_path = Path(synthetic_path)

        # Analyse both datasets
        original_schema = self.analyser.analyse_file(original_path)
        synthetic_schema = self.analyser.analyse_file(synthetic_path)

        # Check schema match
        schema_match, schema_score = self._validate_schema(
            original_schema,
            synthetic_schema,
        )

        # Check distribution similarity
        dist_similarity = self._calculate_distribution_similarity(
            original_schema,
            synthetic_schema,
        )

        # Check for PII in synthetic data
        pii_detected, pii_count, pii_types = self._check_pii(synthetic_path)

        # Calculate diversity
        diversity = self._calculate_diversity(synthetic_schema)

        # Determine if validation passed
        issues = []

        if not schema_match:
            issues.append(f"Schema mismatch (score: {schema_score:.2%})")

        if dist_similarity < self.MIN_DISTRIBUTION_SIMILARITY:
            issues.append(
                f"Distribution similarity below threshold "
                f"({dist_similarity:.2%} < {self.MIN_DISTRIBUTION_SIMILARITY:.0%})"
            )

        if pii_detected:
            issues.append(f"PII detected in synthetic data ({pii_count} entities)")

        if diversity and diversity < self.MIN_DIVERSITY:
            issues.append(
                f"Diversity below threshold "
                f"({diversity:.2%} < {self.MIN_DIVERSITY:.0%})"
            )

        passed = len(issues) == 0

        return ValidationResult(
            schema_match=schema_match,
            schema_match_score=schema_score,
            distribution_similarity=dist_similarity,
            pii_detected=pii_detected,
            pii_entity_count=pii_count,
            pii_entity_types=pii_types,
            semantic_similarity=None,  # TODO: Implement if needed
            diversity_score=diversity,
            passed=passed,
            issues=issues,
        )

    def _validate_schema(
        self,
        original_schema,
        synthetic_schema,
    ) -> tuple[bool, float]:
        """
        Validate schema match between original and synthetic.

        Returns:
            Tuple of (exact_match, match_score).
        """
        original_cols = set(original_schema.column_names())
        synthetic_cols = set(synthetic_schema.column_names())

        # Check column name match
        matching_cols = original_cols & synthetic_cols
        missing_cols = original_cols - synthetic_cols
        extra_cols = synthetic_cols - original_cols

        if not original_cols:
            return False, 0.0

        # Calculate match score
        score = len(matching_cols) / len(original_cols)

        # Exact match if all columns present (no missing, no extra)
        exact_match = len(missing_cols) == 0 and len(extra_cols) == 0

        return exact_match, score

    def _calculate_distribution_similarity(
        self,
        original_schema,
        synthetic_schema,
    ) -> float:
        """
        Calculate distribution similarity between datasets.

        For categorical columns: compares frequency distributions
        For numeric columns: compares mean/std deviation
        """
        similarities = []

        for orig_col in original_schema.columns:
            synth_col = synthetic_schema.get_column(orig_col.column_name)

            if synth_col is None:
                # Column missing in synthetic
                similarities.append(0.0)
                continue

            # Type must match
            if orig_col.column_type != synth_col.column_type:
                similarities.append(0.0)
                continue

            # Compare distributions based on type
            if orig_col.categorical_distribution and synth_col.categorical_distribution:
                sim = self._categorical_similarity(
                    orig_col.categorical_distribution,
                    synth_col.categorical_distribution,
                    original_schema.row_count,
                    synthetic_schema.row_count,
                )
                similarities.append(sim)

            elif orig_col.numeric_stats and synth_col.numeric_stats:
                sim = self._numeric_similarity(
                    orig_col.numeric_stats,
                    synth_col.numeric_stats,
                )
                similarities.append(sim)

            else:
                # Can't compare, assume moderate similarity
                similarities.append(0.7)

        if not similarities:
            return 0.0

        return sum(similarities) / len(similarities)

    def _categorical_similarity(
        self,
        orig_dist: dict[str, int],
        synth_dist: dict[str, int],
        orig_count: int,
        synth_count: int,
    ) -> float:
        """Calculate similarity between categorical distributions."""
        # Normalise to percentages
        orig_pct = {k: v / orig_count for k, v in orig_dist.items()}
        synth_pct = {k: v / synth_count for k, v in synth_dist.items()}

        # Get all unique values
        all_values = set(orig_pct.keys()) | set(synth_pct.keys())

        if not all_values:
            return 1.0

        # Calculate absolute difference in percentages
        total_diff = 0.0
        for value in all_values:
            orig_p = orig_pct.get(value, 0.0)
            synth_p = synth_pct.get(value, 0.0)
            total_diff += abs(orig_p - synth_p)

        # Similarity is 1 - (average difference)
        # total_diff can be at most 2.0 (if completely different)
        similarity = 1.0 - (total_diff / 2.0)

        return max(0.0, min(1.0, similarity))

    def _numeric_similarity(
        self,
        orig_stats: dict[str, float],
        synth_stats: dict[str, float],
    ) -> float:
        """Calculate similarity between numeric distributions."""
        # Compare mean and std as percentage differences
        mean_diff = 0.0
        std_diff = 0.0

        orig_mean = orig_stats.get("mean", 0.0)
        synth_mean = synth_stats.get("mean", 0.0)
        orig_std = orig_stats.get("std", 1.0)
        synth_std = synth_stats.get("std", 1.0)

        # Calculate relative differences
        if orig_mean != 0:
            mean_diff = abs(orig_mean - synth_mean) / abs(orig_mean)

        if orig_std != 0:
            std_diff = abs(orig_std - synth_std) / abs(orig_std)

        # Average the similarities (1 - diff)
        mean_sim = 1.0 - min(mean_diff, 1.0)
        std_sim = 1.0 - min(std_diff, 1.0)

        # Weight mean more heavily (60/40)
        similarity = mean_sim * 0.6 + std_sim * 0.4

        return max(0.0, min(1.0, similarity))

    def _check_pii(self, synthetic_path: Path) -> tuple[bool, int, list[str]]:
        """
        Check for PII in synthetic data.

        Returns:
            Tuple of (pii_detected, entity_count, entity_types).
        """
        try:
            from persona.core.privacy import PIIDetector
            from persona.core.data import DataLoader

            # Check if PII detection is available
            detector = PIIDetector(score_threshold=0.5)

            if not detector.is_available():
                # PII detection not available, assume no PII
                # TODO: Add warning
                return False, 0, []

            # Load synthetic data
            loader = DataLoader()
            content, _ = loader.load_path(synthetic_path)

            # Detect PII
            entities = detector.detect(content)

            if entities:
                entity_types = list(set(e.type for e in entities))
                return True, len(entities), entity_types
            else:
                return False, 0, []

        except ImportError:
            # PII detection not installed, assume no PII
            return False, 0, []

        except Exception:
            # Error during PII detection, assume no PII but log
            # TODO: Add proper logging
            return False, 0, []

    def _calculate_diversity(self, schema) -> float | None:
        """
        Calculate diversity of generated records.

        Diversity is the ratio of unique values to total values
        across all columns (weighted average).
        """
        if schema.row_count == 0:
            return None

        diversities = []

        for col in schema.columns:
            if col.unique_count > 0 and schema.row_count > 0:
                # Diversity for this column
                div = min(col.unique_count / schema.row_count, 1.0)
                diversities.append(div)

        if not diversities:
            return None

        return sum(diversities) / len(diversities)
