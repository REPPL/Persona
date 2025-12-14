"""Tests for persona count estimation (F-065)."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from persona.core.batch.estimator import (
    PersonaEstimator,
    CountEstimate,
    EstimationFactors,
    estimate_personas,
)


class TestEstimationFactors:
    """Tests for EstimationFactors."""
    
    def test_default_values(self):
        """Has sensible defaults."""
        factors = EstimationFactors()
        
        assert factors.total_tokens == 0
        assert factors.file_count == 0
        assert factors.theme_count == 0
    
    def test_to_dict(self):
        """Converts to dictionary."""
        factors = EstimationFactors(
            total_tokens=50000,
            file_count=10,
            theme_count=5,
        )
        data = factors.to_dict()
        
        assert data["total_tokens"] == 50000
        assert data["file_count"] == 10
        assert data["theme_count"] == 5


class TestCountEstimate:
    """Tests for CountEstimate."""
    
    def test_range_property(self):
        """Gets range as tuple."""
        estimate = CountEstimate(
            recommended=5,
            min_count=3,
            max_count=7,
            confidence=0.8,
            reasoning="Test",
        )
        
        assert estimate.range == (3, 7)
    
    def test_to_dict(self):
        """Converts to dictionary."""
        estimate = CountEstimate(
            recommended=5,
            min_count=3,
            max_count=7,
            confidence=0.8,
            reasoning="Test reasoning",
        )
        data = estimate.to_dict()
        
        assert data["recommended"] == 5
        assert data["min"] == 3
        assert data["max"] == 7
        assert data["confidence"] == 0.8
        assert data["reasoning"] == "Test reasoning"
    
    def test_to_display(self):
        """Generates display output."""
        factors = EstimationFactors(
            total_tokens=50000,
            file_count=10,
            theme_count=5,
        )
        estimate = CountEstimate(
            recommended=5,
            min_count=3,
            max_count=7,
            confidence=0.8,
            reasoning="Test",
            factors=factors,
        )
        
        display = estimate.to_display()
        
        assert "Persona Count Estimation" in display
        assert "Files: 10" in display
        assert "50,000" in display  # Formatted token count


class TestPersonaEstimator:
    """Tests for PersonaEstimator."""
    
    def test_estimate_minimal_content(self):
        """Estimates with minimal content."""
        estimator = PersonaEstimator()
        estimate = estimator.estimate(content="Short text", file_count=1)
        
        assert estimate.recommended >= 2  # Minimum
        assert estimate.confidence > 0
    
    def test_estimate_with_token_count(self):
        """Uses pre-calculated token count."""
        estimator = PersonaEstimator()
        estimate = estimator.estimate(
            content=None,
            file_count=10,
            token_count=75000,
        )
        
        # 75000 tokens / 7500 per persona = ~10, but capped by file_count
        assert estimate.recommended <= 10
    
    def test_estimate_respects_maximum(self):
        """Respects maximum personas."""
        estimator = PersonaEstimator(max_personas=5)
        estimate = estimator.estimate(
            content="X" * 400000,  # Large content
            file_count=100,
            token_count=100000,
        )
        
        assert estimate.max_count <= 5
    
    def test_estimate_respects_minimum(self):
        """Respects minimum personas."""
        estimator = PersonaEstimator(min_personas=3)
        estimate = estimator.estimate(
            content="Short content " * 100,
            file_count=10,  # Need enough files to support minimum
            token_count=30000,
        )

        assert estimate.min_count >= 3
    
    def test_estimate_range_valid(self):
        """Range is always valid (min <= max)."""
        estimator = PersonaEstimator()
        estimate = estimator.estimate(content="Test", file_count=1)
        
        assert estimate.min_count <= estimate.max_count
    
    def test_estimate_from_files(self):
        """Estimates from file paths."""
        with TemporaryDirectory() as tmpdir:
            # Create test files
            for i in range(5):
                path = Path(tmpdir) / f"file{i}.md"
                path.write_text("Content " * 100)
            
            paths = list(Path(tmpdir).glob("*.md"))
            
            estimator = PersonaEstimator()
            estimate = estimator.estimate_from_files(paths)
            
            assert estimate.factors.file_count == 5
    
    def test_extract_themes(self):
        """Extracts themes from content."""
        estimator = PersonaEstimator()
        
        content = """
        The user experience design focuses on usability testing.
        Usability testing reveals design patterns that improve
        user experience and design quality.
        """
        
        themes = estimator._extract_themes(content)
        
        assert len(themes) > 0
        # Should find repeated significant words
    
    def test_extract_themes_empty(self):
        """Handles empty content."""
        estimator = PersonaEstimator()
        themes = estimator._extract_themes("")
        
        assert themes == []
    
    def test_calculate_richness(self):
        """Calculates data richness score."""
        estimator = PersonaEstimator()
        
        # Diverse text should have higher richness
        diverse_text = "apple banana cherry date elderberry fig grape honeydew"
        repetitive_text = "word word word word word word word word"
        
        diverse_score = estimator._calculate_richness(diverse_text)
        repetitive_score = estimator._calculate_richness(repetitive_text)
        
        assert diverse_score > repetitive_score
    
    def test_calculate_richness_empty(self):
        """Handles empty content."""
        estimator = PersonaEstimator()
        score = estimator._calculate_richness("")
        
        assert score == 0.0
    
    def test_confidence_increases_with_data(self):
        """More data increases confidence."""
        estimator = PersonaEstimator()
        
        small_estimate = estimator.estimate(
            content="Small content",
            file_count=1,
            token_count=1000,
        )
        
        large_estimate = estimator.estimate(
            content="Large " * 10000,
            file_count=10,
            token_count=100000,
        )
        
        assert large_estimate.confidence >= small_estimate.confidence
    
    def test_reasoning_generated(self):
        """Generates human-readable reasoning."""
        estimator = PersonaEstimator()
        estimate = estimator.estimate(
            content="Test content",
            file_count=5,
            token_count=50000,
        )
        
        assert len(estimate.reasoning) > 0
        assert "token" in estimate.reasoning.lower()
    
    def test_custom_tokens_per_persona(self):
        """Uses custom tokens per persona."""
        estimator = PersonaEstimator(tokens_per_persona=5000)
        # Create content with enough themes to not limit the estimate
        content = " ".join([f"topic{i} " * 5 for i in range(15)])
        estimate = estimator.estimate(
            content=content,
            file_count=20,
            token_count=50000,
        )

        # 50000 / 5000 = 10 personas, capped by themes/files
        assert estimate.recommended >= 2


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_estimate_personas(self):
        """estimate_personas convenience function works."""
        estimate = estimate_personas(
            content="Test content for persona generation",
            file_count=3,
        )
        
        assert estimate.recommended >= 2
        assert estimate.confidence > 0

