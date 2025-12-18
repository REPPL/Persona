"""Unit tests for metrics module."""

import pytest
from persona.core.quality.diversity.metrics import (
    calculate_hapax_ratio,
    calculate_mattr,
    calculate_mtld,
    calculate_ttr,
    interpret_mtld,
)


class TestCalculateTTR:
    """Tests for calculate_ttr function."""

    def test_ttr_empty_tokens(self):
        """Test TTR with empty token list."""
        ttr = calculate_ttr([])
        assert ttr == 0.0

    def test_ttr_all_unique(self):
        """Test TTR when all tokens are unique."""
        tokens = ["hello", "world", "foo", "bar"]
        ttr = calculate_ttr(tokens)
        assert ttr == 1.0

    def test_ttr_all_same(self):
        """Test TTR when all tokens are the same."""
        tokens = ["hello", "hello", "hello", "hello"]
        ttr = calculate_ttr(tokens)
        assert ttr == 0.25

    def test_ttr_mixed(self):
        """Test TTR with mixed tokens."""
        tokens = ["hello", "world", "hello", "foo", "world", "hello"]
        # 3 unique / 6 total = 0.5
        ttr = calculate_ttr(tokens)
        assert ttr == pytest.approx(0.5)

    def test_ttr_single_token(self):
        """Test TTR with single token."""
        tokens = ["hello"]
        ttr = calculate_ttr(tokens)
        assert ttr == 1.0


class TestCalculateMATTR:
    """Tests for calculate_mattr function."""

    def test_mattr_empty_tokens(self):
        """Test MATTR with empty token list."""
        mattr = calculate_mattr([])
        assert mattr == 0.0

    def test_mattr_fewer_than_window(self):
        """Test MATTR with fewer tokens than window size."""
        tokens = ["hello", "world", "foo"]
        mattr = calculate_mattr(tokens, window_size=50)
        # Should fall back to TTR
        ttr = calculate_ttr(tokens)
        assert mattr == ttr

    def test_mattr_exact_window_size(self):
        """Test MATTR with exactly window size tokens."""
        tokens = ["hello"] * 25 + ["world"] * 25  # 50 tokens
        mattr = calculate_mattr(tokens, window_size=50)
        # Only one window, should equal TTR of that window
        ttr = calculate_ttr(tokens)
        assert mattr == ttr

    def test_mattr_multiple_windows(self):
        """Test MATTR with multiple windows."""
        # Create tokens with varying diversity
        tokens = ["a"] * 30 + ["b"] * 30 + ["c"] * 30  # 90 tokens
        mattr = calculate_mattr(tokens, window_size=50)
        # MATTR should be between 0 and 1
        assert 0.0 <= mattr <= 1.0

    def test_mattr_high_diversity(self):
        """Test MATTR with high diversity text."""
        tokens = [f"word{i}" for i in range(100)]
        mattr = calculate_mattr(tokens, window_size=50)
        # All unique, should be 1.0
        assert mattr == pytest.approx(1.0)

    def test_mattr_window_size_parameter(self):
        """Test MATTR with different window sizes."""
        tokens = ["a", "b", "c"] * 20  # 60 tokens
        mattr_10 = calculate_mattr(tokens, window_size=10)
        mattr_20 = calculate_mattr(tokens, window_size=20)
        # Different window sizes should give different results
        assert mattr_10 != mattr_20


class TestCalculateMTLD:
    """Tests for calculate_mtld function."""

    def test_mtld_empty_tokens(self):
        """Test MTLD with empty token list."""
        mtld = calculate_mtld([])
        assert mtld == 0.0

    def test_mtld_too_few_tokens(self):
        """Test MTLD with too few tokens."""
        tokens = ["hello", "world"]
        mtld = calculate_mtld(tokens)
        assert mtld == 0.0

    def test_mtld_high_diversity(self):
        """Test MTLD with high diversity text."""
        tokens = [f"word{i}" for i in range(100)]
        mtld = calculate_mtld(tokens)
        # High diversity should give high MTLD
        assert mtld > 50

    def test_mtld_low_diversity(self):
        """Test MTLD with low diversity text."""
        tokens = ["hello", "world"] * 50  # Only 2 unique words
        mtld = calculate_mtld(tokens)
        # Low diversity should give low MTLD
        assert mtld < 30

    def test_mtld_bidirectional(self):
        """Test that MTLD is bidirectional."""
        tokens = ["a"] * 30 + ["b"] * 30 + ["c"] * 30
        mtld = calculate_mtld(tokens)
        # MTLD should be average of forward and reverse
        assert mtld > 0

    def test_mtld_threshold_parameter(self):
        """Test MTLD with different thresholds."""
        tokens = ["a", "b", "c", "d", "e"] * 20
        mtld_default = calculate_mtld(tokens, threshold=0.72)
        mtld_high = calculate_mtld(tokens, threshold=0.9)
        # Different thresholds should give different results
        assert mtld_default != mtld_high

    def test_mtld_realistic_text(self):
        """Test MTLD with realistic text simulation."""
        # Simulate realistic text with some repetition
        common_words = ["the", "a", "is", "in", "to", "and"]
        unique_words = [f"word{i}" for i in range(50)]
        tokens = common_words * 10 + unique_words
        mtld = calculate_mtld(tokens)
        # Should give reasonable MTLD
        assert 20 < mtld < 100


class TestCalculateHapaxRatio:
    """Tests for calculate_hapax_ratio function."""

    def test_hapax_ratio_empty_tokens(self):
        """Test hapax ratio with empty token list."""
        ratio = calculate_hapax_ratio([])
        assert ratio == 0.0

    def test_hapax_ratio_all_unique(self):
        """Test hapax ratio when all tokens appear once."""
        tokens = ["hello", "world", "foo", "bar"]
        ratio = calculate_hapax_ratio(tokens)
        assert ratio == 1.0

    def test_hapax_ratio_no_unique(self):
        """Test hapax ratio when no tokens appear once."""
        tokens = ["hello", "hello", "world", "world"]
        ratio = calculate_hapax_ratio(tokens)
        assert ratio == 0.0

    def test_hapax_ratio_mixed(self):
        """Test hapax ratio with mixed frequencies."""
        tokens = ["hello", "hello", "world", "foo", "bar"]
        # 3 hapax (world, foo, bar) / 5 total = 0.6
        ratio = calculate_hapax_ratio(tokens)
        assert ratio == pytest.approx(0.6)

    def test_hapax_ratio_single_token(self):
        """Test hapax ratio with single token."""
        tokens = ["hello"]
        ratio = calculate_hapax_ratio(tokens)
        assert ratio == 1.0

    def test_hapax_ratio_high_repetition(self):
        """Test hapax ratio with high repetition."""
        tokens = ["the"] * 50 + ["a"] * 30 + ["unique"]
        # Only 1 hapax / 81 total
        ratio = calculate_hapax_ratio(tokens)
        assert ratio == pytest.approx(1 / 81)


class TestInterpretMTLD:
    """Tests for interpret_mtld function."""

    def test_interpret_poor(self):
        """Test interpretation of poor MTLD."""
        assert interpret_mtld(0) == "poor"
        assert interpret_mtld(15) == "poor"
        assert interpret_mtld(29.9) == "poor"

    def test_interpret_below_average(self):
        """Test interpretation of below average MTLD."""
        assert interpret_mtld(30) == "below_average"
        assert interpret_mtld(40) == "below_average"
        assert interpret_mtld(49.9) == "below_average"

    def test_interpret_average(self):
        """Test interpretation of average MTLD."""
        assert interpret_mtld(50) == "average"
        assert interpret_mtld(60) == "average"
        assert interpret_mtld(69.9) == "average"

    def test_interpret_good(self):
        """Test interpretation of good MTLD."""
        assert interpret_mtld(70) == "good"
        assert interpret_mtld(85) == "good"
        assert interpret_mtld(99.9) == "good"

    def test_interpret_excellent(self):
        """Test interpretation of excellent MTLD."""
        assert interpret_mtld(100) == "excellent"
        assert interpret_mtld(150) == "excellent"
        assert interpret_mtld(1000) == "excellent"
