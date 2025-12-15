"""Tests for TUI widgets."""

import pytest
from decimal import Decimal

from persona.tui.widgets.cost_tracker import CostTracker
from persona.tui.widgets.progress_panel import ProgressPanel
from persona.tui.widgets.quality_badge import QualityBadge


def test_cost_tracker_initialization():
    """Test cost tracker initialization."""
    tracker = CostTracker()
    assert tracker.session_cost == Decimal("0")
    assert tracker.total_cost == Decimal("0")
    assert len(tracker.costs_by_provider) == 0
    assert tracker.budget_limit is None


def test_cost_tracker_get_methods():
    """Test cost tracker getter methods."""
    tracker = CostTracker()
    assert tracker.get_session_cost() == Decimal("0")
    assert tracker.get_total_cost() == Decimal("0")
    assert tracker.get_breakdown() == {}


def test_progress_panel_initialization():
    """Test progress panel initialization."""
    panel = ProgressPanel()
    assert panel.current_progress == 0.0
    assert panel.current_status == "Idle"
    assert panel.personas_generated == 0
    assert panel.personas_total == 0
    assert panel.tokens_used == 0
    assert panel.estimated_cost == 0.0


def test_progress_panel_data_update():
    """Test updating progress panel data (without DOM access)."""
    panel = ProgressPanel()

    # Update internal state
    panel.current_progress = 0.5
    panel.current_status = "Generating..."

    assert panel.current_progress == 0.5
    assert panel.current_status == "Generating..."


def test_progress_panel_personas_data():
    """Test setting persona count data."""
    panel = ProgressPanel()

    panel.personas_generated = 3
    panel.personas_total = 10

    assert panel.personas_generated == 3
    assert panel.personas_total == 10


def test_progress_panel_is_active():
    """Test checking if panel is active."""
    panel = ProgressPanel()

    assert not panel.is_active()  # 0 progress

    panel.current_progress = 0.5
    assert panel.is_active()  # Mid-progress

    panel.current_progress = 1.0
    assert not panel.is_active()  # Complete


def test_quality_badge_initialization():
    """Test quality badge initialization."""
    badge = QualityBadge(87.5)
    assert badge.score == 87.5
    assert badge.show_label is True


def test_quality_badge_level_excellent():
    """Test quality badge level for excellent score."""
    badge = QualityBadge(90)
    assert badge._get_level_text() == "Excellent"


def test_quality_badge_level_good():
    """Test quality badge level for good score."""
    badge = QualityBadge(75)
    assert badge._get_level_text() == "Good"


def test_quality_badge_level_acceptable():
    """Test quality badge level for acceptable score."""
    badge = QualityBadge(60)
    assert badge._get_level_text() == "Acceptable"


def test_quality_badge_level_poor():
    """Test quality badge level for poor score."""
    badge = QualityBadge(40)
    assert badge._get_level_text() == "Poor"


def test_quality_badge_level_failing():
    """Test quality badge level for failing score."""
    badge = QualityBadge(20)
    assert badge._get_level_text() == "Failing"


def test_quality_badge_update_score():
    """Test updating badge score."""
    badge = QualityBadge(50)
    assert badge.score == 50

    badge.update_score(90)
    assert badge.score == 90
