"""Tests for multi-file handling (F-060)."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from persona.core.batch.combiner import (
    FileCombiner,
    FileContent,
    CombinedContent,
    SeparatorStyle,
    combine_files,
)


class TestFileCombiner:
    """Tests for FileCombiner."""
    
    def test_combine_empty_list(self):
        """Combines empty file list."""
        combiner = FileCombiner()
        result = combiner.combine([])
        
        assert result.source_count == 0
        assert result.content == ""
    
    def test_combine_single_file(self):
        """Combines single file."""
        combiner = FileCombiner()
        files = [
            FileContent(
                path=Path("test.md"),
                content="Test content",
                format="markdown",
                size_bytes=12,
            )
        ]
        
        result = combiner.combine(files)
        
        assert result.source_count == 1
        assert "Test content" in result.content
        assert "test.md" in result.content
    
    def test_combine_multiple_files(self):
        """Combines multiple files with separators."""
        combiner = FileCombiner()
        files = [
            FileContent(
                path=Path("a.md"),
                content="Content A",
                format="markdown",
                size_bytes=9,
            ),
            FileContent(
                path=Path("b.md"),
                content="Content B",
                format="markdown",
                size_bytes=9,
            ),
        ]
        
        result = combiner.combine(files)
        
        assert result.source_count == 2
        assert "Content A" in result.content
        assert "Content B" in result.content
        assert "a.md" in result.content
        assert "b.md" in result.content
    
    def test_minimal_style(self):
        """Uses minimal separator style."""
        combiner = FileCombiner(style=SeparatorStyle.MINIMAL)
        files = [
            FileContent(
                path=Path("test.md"),
                content="Content",
                format="markdown",
                size_bytes=7,
            )
        ]
        
        result = combiner.combine(files)
        
        # Minimal style has less metadata
        assert "SOURCE: test.md" in result.content
        assert "INDEX" not in result.content
    
    def test_standard_style(self):
        """Uses standard separator style."""
        combiner = FileCombiner(style=SeparatorStyle.STANDARD)
        files = [
            FileContent(
                path=Path("test.md"),
                content="Content",
                format="markdown",
                size_bytes=7,
            )
        ]
        
        result = combiner.combine(files)
        
        assert "SOURCE: test.md" in result.content
        assert "INDEX: 1 of 1" in result.content
    
    def test_detailed_style(self):
        """Uses detailed separator style."""
        combiner = FileCombiner(style=SeparatorStyle.DETAILED)
        files = [
            FileContent(
                path=Path("test.md"),
                content="Content",
                format="markdown",
                size_bytes=7,
            )
        ]
        
        result = combiner.combine(files)
        
        assert "SOURCE: test.md" in result.content
        assert "SIZE:" in result.content
    
    def test_custom_template(self):
        """Uses custom separator template."""
        template = "=== {{ filename }} ===\n{{ content }}\n==="
        combiner = FileCombiner()
        combiner.set_custom_template(template)
        
        files = [
            FileContent(
                path=Path("test.md"),
                content="Content",
                format="markdown",
                size_bytes=7,
            )
        ]
        
        result = combiner.combine(files)
        
        assert "=== test.md ===" in result.content
    
    def test_tracks_sources(self):
        """Tracks source information."""
        combiner = FileCombiner()
        files = [
            FileContent(
                path=Path("a.md"),
                content="A",
                format="markdown",
                size_bytes=1,
            ),
            FileContent(
                path=Path("b.md"),
                content="B",
                format="markdown",
                size_bytes=1,
            ),
        ]
        
        result = combiner.combine(files)
        
        assert len(result.sources) == 2
        assert result.sources[0]["filename"] == "a.md"
        assert result.sources[1]["filename"] == "b.md"
    
    def test_calculates_total_size(self):
        """Calculates total size bytes."""
        combiner = FileCombiner()
        files = [
            FileContent(path=Path("a.md"), content="A", format="md", size_bytes=100),
            FileContent(path=Path("b.md"), content="B", format="md", size_bytes=200),
        ]
        
        result = combiner.combine(files)
        
        assert result.total_size_bytes == 300
    
    def test_combine_from_paths(self):
        """Combines from file paths."""
        with TemporaryDirectory() as tmpdir:
            path1 = Path(tmpdir) / "a.md"
            path2 = Path(tmpdir) / "b.md"
            path1.write_text("Content A")
            path2.write_text("Content B")
            
            combiner = FileCombiner()
            result = combiner.combine_from_paths([path1, path2])
            
            assert result.source_count == 2
            assert "Content A" in result.content
    
    def test_combined_content_to_dict(self):
        """CombinedContent converts to dict."""
        content = CombinedContent(
            content="test",
            source_count=1,
            total_size_bytes=100,
        )
        
        data = content.to_dict()
        assert "source_count" in data
        assert "total_size_bytes" in data


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_combine_files(self):
        """combine_files convenience function works."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Content")
            
            result = combine_files([path])
            assert result.source_count == 1
