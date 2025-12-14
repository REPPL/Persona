"""Tests for experiment editor."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from persona.core.experiments import (
    ExperimentManager,
    ExperimentEditor,
    EditHistoryEntry,
)


class TestEditHistoryEntry:
    """Tests for EditHistoryEntry dataclass."""

    def test_create_entry(self):
        """Test creating a history entry."""
        entry = EditHistoryEntry(
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            field="count",
            old_value=3,
            new_value=5,
            action="update",
        )
        assert entry.field == "count"
        assert entry.old_value == 3
        assert entry.new_value == 5

    def test_to_dict(self):
        """Test converting entry to dictionary."""
        entry = EditHistoryEntry(
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            field="model",
            old_value=None,
            new_value="gpt-4o",
            action="update",
        )
        data = entry.to_dict()
        assert data["field"] == "model"
        assert data["old_value"] is None
        assert data["new_value"] == "gpt-4o"
        assert "timestamp" in data

    def test_from_dict(self):
        """Test creating entry from dictionary."""
        data = {
            "timestamp": "2024-01-15T10:30:00",
            "field": "provider",
            "old_value": "anthropic",
            "new_value": "openai",
            "action": "update",
        }
        entry = EditHistoryEntry.from_dict(data)
        assert entry.field == "provider"
        assert entry.old_value == "anthropic"
        assert entry.new_value == "openai"

    def test_from_dict_defaults(self):
        """Test defaults when creating from dictionary."""
        data = {
            "timestamp": "2024-01-15T10:30:00",
            "field": "count",
        }
        entry = EditHistoryEntry.from_dict(data)
        assert entry.old_value is None
        assert entry.new_value is None
        assert entry.action == "update"


class TestExperimentEditor:
    """Tests for ExperimentEditor class."""

    def test_set_field_count(self):
        """Test setting count field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            config = editor.set_field("test-exp", "count", 10)

            assert config.count == 10

    def test_set_field_provider(self):
        """Test setting provider field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            config = editor.set_field("test-exp", "provider", "openai")

            assert config.provider == "openai"

    def test_set_field_model(self):
        """Test setting model field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            config = editor.set_field("test-exp", "model", "gpt-4o")

            assert config.model == "gpt-4o"

    def test_set_field_nested_path(self):
        """Test setting field with nested path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            config = editor.set_field("test-exp", "generation.model", "claude-3-opus")

            assert config.model == "claude-3-opus"

    def test_set_field_invalid_path(self):
        """Test setting field with invalid nested path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)

            with pytest.raises(ValueError, match="Invalid field path"):
                editor.set_field("test-exp", "invalid.nested.path", "value")

    def test_set_field_invalid_field(self):
        """Test setting invalid field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)

            with pytest.raises(ValueError, match="Invalid field"):
                editor.set_field("test-exp", "nonexistent", "value")

    def test_set_field_nonexistent_experiment(self):
        """Test setting field on nonexistent experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)

            editor = ExperimentEditor(manager)

            with pytest.raises(FileNotFoundError):
                editor.set_field("nonexistent", "count", 5)

    def test_set_field_type_coercion(self):
        """Test that count is converted to int."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            config = editor.set_field("test-exp", "count", "7")

            assert config.count == 7
            assert isinstance(config.count, int)

    def test_set_fields_multiple(self):
        """Test setting multiple fields at once."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            config = editor.set_fields("test-exp", {
                "count": 5,
                "provider": "openai",
                "model": "gpt-4o",
            })

            assert config.count == 5
            assert config.provider == "openai"
            assert config.model == "gpt-4o"

    def test_set_field_creates_history(self):
        """Test that setting field creates history entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            editor.set_field("test-exp", "count", 10)

            history = editor.get_history("test-exp")
            assert len(history) == 1
            assert history[0].field == "count"
            assert history[0].old_value == 3
            assert history[0].new_value == 10

    def test_set_field_no_history(self):
        """Test setting field without saving history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            editor.set_field("test-exp", "count", 10, save_history=False)

            history = editor.get_history("test-exp")
            assert len(history) == 0

    def test_add_source(self):
        """Test adding a data source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            # Create a source file
            source_path = Path(tmpdir) / "test-data.csv"
            source_path.write_text("col1,col2\na,b\n")

            editor = ExperimentEditor(manager)
            dest = editor.add_source("test-exp", source_path)

            assert dest.exists()
            assert dest.name == "test-data.csv"

    def test_add_source_nonexistent(self):
        """Test adding nonexistent source file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)

            with pytest.raises(FileNotFoundError):
                editor.add_source("test-exp", Path("/nonexistent/file.csv"))

    def test_add_source_already_exists(self):
        """Test adding source that already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            # Create source file
            source_path = Path(tmpdir) / "data.csv"
            source_path.write_text("col1,col2\n")

            editor = ExperimentEditor(manager)
            editor.add_source("test-exp", source_path)

            # Try to add again
            with pytest.raises(ValueError, match="already exists"):
                editor.add_source("test-exp", source_path)

    def test_remove_source(self):
        """Test removing a data source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            # Add a source first
            source_path = Path(tmpdir) / "data.csv"
            source_path.write_text("col1,col2\n")

            editor = ExperimentEditor(manager)
            editor.add_source("test-exp", source_path)

            # Now remove it
            result = editor.remove_source("test-exp", "data.csv")
            assert result is True

            # Verify it's gone
            sources = editor.list_sources("test-exp")
            assert "data.csv" not in sources

    def test_remove_source_nonexistent(self):
        """Test removing nonexistent source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)

            with pytest.raises(FileNotFoundError):
                editor.remove_source("test-exp", "nonexistent.csv")

    def test_list_sources(self):
        """Test listing data sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            exp = manager.create("test-exp")

            # Add some files directly
            (exp.data_dir / "file1.csv").write_text("a,b\n")
            (exp.data_dir / "file2.json").write_text("{}\n")
            (exp.data_dir / ".hidden").write_text("hidden\n")

            editor = ExperimentEditor(manager)
            sources = editor.list_sources("test-exp")

            assert "file1.csv" in sources
            assert "file2.json" in sources
            assert ".hidden" not in sources

    def test_list_sources_empty(self):
        """Test listing sources when none exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            sources = editor.list_sources("test-exp")

            assert sources == []

    def test_get_history_empty(self):
        """Test getting history when none exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            history = editor.get_history("test-exp")

            assert history == []

    def test_get_history_with_entries(self):
        """Test getting history with entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            editor.set_field("test-exp", "count", 5)
            editor.set_field("test-exp", "provider", "openai")

            history = editor.get_history("test-exp")

            assert len(history) == 2
            assert history[0].field == "count"
            assert history[1].field == "provider"

    def test_rollback_single_edit(self):
        """Test rolling back a single edit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            editor.set_field("test-exp", "count", 10)

            # Verify change
            exp = manager.load("test-exp")
            assert exp.config.count == 10

            # Rollback
            config = editor.rollback("test-exp", 1)
            assert config.count == 3  # Original value

    def test_rollback_multiple_edits(self):
        """Test rolling back multiple edits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            editor.set_field("test-exp", "count", 5)
            editor.set_field("test-exp", "count", 10)
            editor.set_field("test-exp", "count", 15)

            # Rollback 2 edits
            config = editor.rollback("test-exp", 2)
            assert config.count == 5

    def test_rollback_no_history(self):
        """Test rollback when no history exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            result = editor.rollback("test-exp")

            assert result is None

    def test_rollback_too_many_steps(self):
        """Test rollback with more steps than available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            editor.set_field("test-exp", "count", 10)

            with pytest.raises(ValueError, match="Cannot rollback"):
                editor.rollback("test-exp", 5)

    def test_rollback_updates_history(self):
        """Test that rollback updates history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            editor.set_field("test-exp", "count", 5)
            editor.set_field("test-exp", "count", 10)

            assert len(editor.get_history("test-exp")) == 2

            editor.rollback("test-exp", 1)

            assert len(editor.get_history("test-exp")) == 1

    def test_rollback_add_source(self):
        """Test rolling back an add_source operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            # Create source file
            source_path = Path(tmpdir) / "data.csv"
            source_path.write_text("col1,col2\n")

            editor = ExperimentEditor(manager)
            editor.add_source("test-exp", source_path)

            # Verify source exists
            sources = editor.list_sources("test-exp")
            assert "data.csv" in sources

            # Rollback
            editor.rollback("test-exp", 1)

            # Verify source removed
            sources = editor.list_sources("test-exp")
            assert "data.csv" not in sources

    def test_clear_history(self):
        """Test clearing edit history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)
            editor.set_field("test-exp", "count", 5)
            editor.set_field("test-exp", "count", 10)

            assert len(editor.get_history("test-exp")) == 2

            editor.clear_history("test-exp")

            assert len(editor.get_history("test-exp")) == 0

    def test_clear_history_no_file(self):
        """Test clearing history when no history file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            editor = ExperimentEditor(manager)

            # Should not raise
            editor.clear_history("test-exp")

    def test_persistence(self):
        """Test that changes persist across editor instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            # First editor makes changes
            editor1 = ExperimentEditor(manager)
            editor1.set_field("test-exp", "count", 10)

            # Second editor should see the changes
            editor2 = ExperimentEditor(manager)
            exp = manager.load("test-exp")
            assert exp.config.count == 10

            # History should also persist
            history = editor2.get_history("test-exp")
            assert len(history) == 1
