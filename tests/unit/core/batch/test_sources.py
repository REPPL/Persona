"""Tests for data file listing (F-064)."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from persona.core.batch.sources import (
    DataSourceTracker,
    SourceMetadata,
    SourceSummary,
    track_sources,
)


class TestSourceMetadata:
    """Tests for SourceMetadata."""
    
    def test_to_dict(self):
        """Converts to dictionary."""
        from datetime import datetime
        
        metadata = SourceMetadata(
            path=Path("/test/file.md"),
            relative_path="file.md",
            size_bytes=100,
            modified=datetime(2024, 1, 1, 12, 0, 0),
            format="markdown",
            sha256="abc123",
            tokens=50,
        )
        
        data = metadata.to_dict()
        
        assert data["relative_path"] == "file.md"
        assert data["size_bytes"] == 100
        assert data["format"] == "markdown"
        assert data["sha256"] == "abc123"


class TestSourceSummary:
    """Tests for SourceSummary."""
    
    def test_empty_summary(self):
        """Creates empty summary."""
        summary = SourceSummary()
        
        assert summary.total_files == 0
        assert summary.total_size_bytes == 0
    
    def test_to_dict(self):
        """Converts to dictionary."""
        summary = SourceSummary(total_files=5, total_size_bytes=1000)
        data = summary.to_dict()
        
        assert data["total_files"] == 5
        assert data["total_size_bytes"] == 1000
    
    def test_to_markdown_table_empty(self):
        """Generates message for empty sources."""
        summary = SourceSummary()
        table = summary.to_markdown_table()
        
        assert "No data sources recorded" in table
    
    def test_to_markdown_table_with_files(self):
        """Generates markdown table."""
        from datetime import datetime
        
        metadata = SourceMetadata(
            path=Path("/test/file.md"),
            relative_path="file.md",
            size_bytes=1024,
            modified=datetime(2024, 1, 1),
            format="markdown",
            sha256="abc123",
            tokens=100,
        )
        summary = SourceSummary(
            files=[metadata],
            total_files=1,
            total_size_bytes=1024,
            total_tokens=100,
        )
        
        table = summary.to_markdown_table()
        
        assert "| File |" in table
        assert "file.md" in table
        assert "1.0 KB" in table


class TestDataSourceTracker:
    """Tests for DataSourceTracker."""
    
    def test_add_file(self):
        """Adds file and returns metadata."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Test content")
            
            tracker = DataSourceTracker(base_path=Path(tmpdir))
            metadata = tracker.add_file(path)
            
            assert metadata.format == "markdown"
            assert metadata.size_bytes > 0
            assert metadata.sha256 is not None
    
    def test_add_file_with_content(self):
        """Adds file with pre-loaded content."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Test content")
            
            tracker = DataSourceTracker(base_path=Path(tmpdir))
            metadata = tracker.add_file(path, content="Custom content")
            
            # Hash should be of custom content
            assert metadata.sha256 is not None
    
    def test_add_files(self):
        """Adds multiple files."""
        with TemporaryDirectory() as tmpdir:
            path1 = Path(tmpdir) / "a.md"
            path2 = Path(tmpdir) / "b.csv"
            path1.write_text("Content A")
            path2.write_text("col1,col2\n1,2")
            
            tracker = DataSourceTracker(base_path=Path(tmpdir))
            metadatas = tracker.add_files([path1, path2])
            
            assert len(metadatas) == 2
    
    def test_get_summary(self):
        """Gets summary of tracked sources."""
        with TemporaryDirectory() as tmpdir:
            path1 = Path(tmpdir) / "a.md"
            path2 = Path(tmpdir) / "b.md"
            path1.write_text("Content A")
            path2.write_text("Content B")
            
            tracker = DataSourceTracker(base_path=Path(tmpdir))
            tracker.add_files([path1, path2])
            
            summary = tracker.get_summary()
            
            assert summary.total_files == 2
            assert summary.total_size_bytes > 0
    
    def test_get_metadata(self):
        """Gets metadata for output."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Content")
            
            tracker = DataSourceTracker(base_path=Path(tmpdir))
            tracker.add_file(path)
            
            metadata = tracker.get_metadata()
            
            assert "data_sources" in metadata
    
    def test_generate_readme_section(self):
        """Generates README section."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Content")
            
            tracker = DataSourceTracker(base_path=Path(tmpdir))
            tracker.add_file(path)
            
            section = tracker.generate_readme_section()
            
            assert "## Data Sources" in section
            assert "test.md" in section
    
    def test_verify_integrity_success(self):
        """Verifies unchanged files pass."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Original content")
            
            tracker = DataSourceTracker(base_path=Path(tmpdir))
            tracker.add_file(path)
            
            results = tracker.verify_integrity()
            
            assert len(results) == 1
            assert results[0][1] is True  # is_valid
    
    def test_verify_integrity_failure(self):
        """Detects modified files."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Original content")
            
            tracker = DataSourceTracker(base_path=Path(tmpdir))
            tracker.add_file(path)
            
            # Modify file
            path.write_text("Modified content")
            
            results = tracker.verify_integrity()
            
            assert len(results) == 1
            assert results[0][1] is False  # is_valid
            assert "mismatch" in results[0][2].lower()
    
    def test_verify_integrity_missing(self):
        """Detects missing files."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Content")
            
            tracker = DataSourceTracker(base_path=Path(tmpdir))
            tracker.add_file(path)
            
            # Delete file
            path.unlink()
            
            results = tracker.verify_integrity()
            
            assert results[0][1] is False
            assert "not found" in results[0][2].lower()
    
    def test_clear(self):
        """Clears tracked sources."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Content")
            
            tracker = DataSourceTracker(base_path=Path(tmpdir))
            tracker.add_file(path)
            tracker.clear()
            
            summary = tracker.get_summary()
            assert summary.total_files == 0
    
    def test_detect_format_csv(self):
        """Detects CSV format."""
        tracker = DataSourceTracker()
        format_type = tracker._detect_format(Path("test.csv"))
        
        assert format_type == "csv"
    
    def test_detect_format_json(self):
        """Detects JSON format."""
        tracker = DataSourceTracker()
        format_type = tracker._detect_format(Path("test.json"))
        
        assert format_type == "json"
    
    def test_detect_format_yaml(self):
        """Detects YAML format."""
        tracker = DataSourceTracker()
        
        assert tracker._detect_format(Path("test.yaml")) == "yaml"
        assert tracker._detect_format(Path("test.yml")) == "yaml"


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_track_sources(self):
        """track_sources convenience function works."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Content")
            
            summary = track_sources([path], base_path=Path(tmpdir))
            
            assert summary.total_files == 1

