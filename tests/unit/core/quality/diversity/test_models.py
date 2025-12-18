"""Unit tests for diversity data models."""


from persona.core.quality.diversity.models import (
    BatchDiversityReport,
    DiversityConfig,
    DiversityReport,
    InterpretationLevel,
)


class TestDiversityConfig:
    """Tests for DiversityConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DiversityConfig()
        assert config.mattr_window_size == 50
        assert config.mtld_threshold == 0.72
        assert config.min_tokens == 50

    def test_custom_config(self):
        """Test custom configuration values."""
        config = DiversityConfig(
            mattr_window_size=100,
            mtld_threshold=0.8,
            min_tokens=30,
        )
        assert config.mattr_window_size == 100
        assert config.mtld_threshold == 0.8
        assert config.min_tokens == 30

    def test_to_dict(self):
        """Test serialisation to dictionary."""
        config = DiversityConfig(
            mattr_window_size=60,
            mtld_threshold=0.75,
            min_tokens=40,
        )
        data = config.to_dict()
        assert data["mattr_window_size"] == 60
        assert data["mtld_threshold"] == 0.75
        assert data["min_tokens"] == 40


class TestDiversityReport:
    """Tests for DiversityReport model."""

    def test_create_report(self):
        """Test creating a diversity report."""
        report = DiversityReport(
            persona_id="p1",
            persona_name="Alice",
            total_tokens=100,
            unique_tokens=50,
            ttr=0.5,
            mattr=0.55,
            mtld=65.0,
            hapax_ratio=0.3,
            interpretation=InterpretationLevel.AVERAGE,
            token_frequency={"hello": 5, "world": 3},
        )
        assert report.persona_id == "p1"
        assert report.persona_name == "Alice"
        assert report.total_tokens == 100
        assert report.unique_tokens == 50
        assert report.ttr == 0.5
        assert report.mattr == 0.55
        assert report.mtld == 65.0
        assert report.hapax_ratio == 0.3
        assert report.interpretation == InterpretationLevel.AVERAGE

    def test_report_auto_timestamp(self):
        """Test that timestamp is auto-generated."""
        report = DiversityReport(
            persona_id="p1",
            persona_name="Alice",
            total_tokens=100,
            unique_tokens=50,
            ttr=0.5,
            mattr=0.55,
            mtld=65.0,
            hapax_ratio=0.3,
            interpretation=InterpretationLevel.AVERAGE,
        )
        assert report.generated_at != ""
        assert "T" in report.generated_at  # ISO format

    def test_report_custom_timestamp(self):
        """Test setting custom timestamp."""
        timestamp = "2025-01-01T12:00:00"
        report = DiversityReport(
            persona_id="p1",
            persona_name="Alice",
            total_tokens=100,
            unique_tokens=50,
            ttr=0.5,
            mattr=0.55,
            mtld=65.0,
            hapax_ratio=0.3,
            interpretation=InterpretationLevel.AVERAGE,
            generated_at=timestamp,
        )
        assert report.generated_at == timestamp

    def test_report_to_dict(self):
        """Test serialisation to dictionary."""
        report = DiversityReport(
            persona_id="p1",
            persona_name="Alice",
            total_tokens=100,
            unique_tokens=50,
            ttr=0.5234,
            mattr=0.5567,
            mtld=65.123,
            hapax_ratio=0.3456,
            interpretation=InterpretationLevel.AVERAGE,
            token_frequency={"hello": 5, "world": 3, "foo": 2},
        )
        data = report.to_dict()

        assert data["persona_id"] == "p1"
        assert data["persona_name"] == "Alice"
        assert data["total_tokens"] == 100
        assert data["unique_tokens"] == 50
        assert data["ttr"] == 0.5234  # Rounded to 4 decimals
        assert data["mattr"] == 0.5567
        assert data["mtld"] == 65.12  # Rounded to 2 decimals
        assert data["hapax_ratio"] == 0.3456
        assert data["interpretation"] == "average"
        assert "top_tokens" in data
        assert len(data["top_tokens"]) <= 10

    def test_report_top_tokens_limited(self):
        """Test that top tokens are limited to 10."""
        freq = {f"word{i}": i for i in range(20)}
        report = DiversityReport(
            persona_id="p1",
            persona_name="Alice",
            total_tokens=100,
            unique_tokens=50,
            ttr=0.5,
            mattr=0.55,
            mtld=65.0,
            hapax_ratio=0.3,
            interpretation=InterpretationLevel.AVERAGE,
            token_frequency=freq,
        )
        data = report.to_dict()
        assert len(data["top_tokens"]) == 10


class TestBatchDiversityReport:
    """Tests for BatchDiversityReport model."""

    def test_create_batch_report(self):
        """Test creating a batch diversity report."""
        reports = [
            DiversityReport(
                persona_id="p1",
                persona_name="Alice",
                total_tokens=100,
                unique_tokens=50,
                ttr=0.5,
                mattr=0.55,
                mtld=65.0,
                hapax_ratio=0.3,
                interpretation=InterpretationLevel.AVERAGE,
            ),
            DiversityReport(
                persona_id="p2",
                persona_name="Bob",
                total_tokens=120,
                unique_tokens=80,
                ttr=0.67,
                mattr=0.7,
                mtld=85.0,
                hapax_ratio=0.5,
                interpretation=InterpretationLevel.GOOD,
            ),
        ]
        batch = BatchDiversityReport(
            reports=reports,
            average_ttr=0.585,
            average_mattr=0.625,
            average_mtld=75.0,
            average_hapax_ratio=0.4,
        )
        assert len(batch.reports) == 2
        assert batch.average_ttr == 0.585
        assert batch.average_mattr == 0.625
        assert batch.average_mtld == 75.0
        assert batch.average_hapax_ratio == 0.4

    def test_batch_persona_count(self):
        """Test persona_count property."""
        reports = [
            DiversityReport(
                persona_id=f"p{i}",
                persona_name=f"Person {i}",
                total_tokens=100,
                unique_tokens=50,
                ttr=0.5,
                mattr=0.55,
                mtld=65.0,
                hapax_ratio=0.3,
                interpretation=InterpretationLevel.AVERAGE,
            )
            for i in range(5)
        ]
        batch = BatchDiversityReport(
            reports=reports,
            average_ttr=0.5,
            average_mattr=0.55,
            average_mtld=65.0,
            average_hapax_ratio=0.3,
        )
        assert batch.persona_count == 5

    def test_batch_auto_timestamp(self):
        """Test that timestamp is auto-generated."""
        batch = BatchDiversityReport(
            reports=[],
            average_ttr=0.0,
            average_mattr=0.0,
            average_mtld=0.0,
            average_hapax_ratio=0.0,
        )
        assert batch.generated_at != ""
        assert "T" in batch.generated_at

    def test_get_by_interpretation(self):
        """Test filtering reports by interpretation level."""
        reports = [
            DiversityReport(
                persona_id="p1",
                persona_name="Poor",
                total_tokens=100,
                unique_tokens=10,
                ttr=0.1,
                mattr=0.1,
                mtld=20.0,
                hapax_ratio=0.05,
                interpretation=InterpretationLevel.POOR,
            ),
            DiversityReport(
                persona_id="p2",
                persona_name="Good",
                total_tokens=100,
                unique_tokens=70,
                ttr=0.7,
                mattr=0.75,
                mtld=85.0,
                hapax_ratio=0.5,
                interpretation=InterpretationLevel.GOOD,
            ),
            DiversityReport(
                persona_id="p3",
                persona_name="Excellent",
                total_tokens=100,
                unique_tokens=90,
                ttr=0.9,
                mattr=0.95,
                mtld=120.0,
                hapax_ratio=0.7,
                interpretation=InterpretationLevel.EXCELLENT,
            ),
        ]
        batch = BatchDiversityReport(
            reports=reports,
            average_ttr=0.57,
            average_mattr=0.6,
            average_mtld=75.0,
            average_hapax_ratio=0.42,
        )

        poor = batch.get_by_interpretation(InterpretationLevel.POOR)
        assert len(poor) == 1
        assert poor[0].persona_name == "Poor"

        good = batch.get_by_interpretation(InterpretationLevel.GOOD)
        assert len(good) == 1
        assert good[0].persona_name == "Good"

        excellent = batch.get_by_interpretation(InterpretationLevel.EXCELLENT)
        assert len(excellent) == 1
        assert excellent[0].persona_name == "Excellent"

    def test_batch_to_dict(self):
        """Test serialisation to dictionary."""
        reports = [
            DiversityReport(
                persona_id="p1",
                persona_name="Alice",
                total_tokens=100,
                unique_tokens=50,
                ttr=0.5,
                mattr=0.55,
                mtld=65.0,
                hapax_ratio=0.3,
                interpretation=InterpretationLevel.AVERAGE,
            ),
        ]
        batch = BatchDiversityReport(
            reports=reports,
            average_ttr=0.5234,
            average_mattr=0.5567,
            average_mtld=65.123,
            average_hapax_ratio=0.3456,
        )
        data = batch.to_dict()

        assert data["persona_count"] == 1
        assert data["average_ttr"] == 0.5234  # Rounded to 4 decimals
        assert data["average_mattr"] == 0.5567
        assert data["average_mtld"] == 65.12  # Rounded to 2 decimals
        assert data["average_hapax_ratio"] == 0.3456
        assert "individual_reports" in data
        assert len(data["individual_reports"]) == 1


class TestInterpretationLevel:
    """Tests for InterpretationLevel enum."""

    def test_interpretation_levels(self):
        """Test that all interpretation levels exist."""
        assert InterpretationLevel.POOR.value == "poor"
        assert InterpretationLevel.BELOW_AVERAGE.value == "below_average"
        assert InterpretationLevel.AVERAGE.value == "average"
        assert InterpretationLevel.GOOD.value == "good"
        assert InterpretationLevel.EXCELLENT.value == "excellent"

    def test_interpretation_from_string(self):
        """Test creating interpretation level from string."""
        assert InterpretationLevel("poor") == InterpretationLevel.POOR
        assert InterpretationLevel("average") == InterpretationLevel.AVERAGE
        assert InterpretationLevel("excellent") == InterpretationLevel.EXCELLENT
