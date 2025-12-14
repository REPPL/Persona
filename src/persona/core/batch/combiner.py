"""
Multi-file handling with separators (F-060).

Provides file combination with clear separators and metadata
for multi-source persona generation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from jinja2 import Template


class SeparatorStyle(Enum):
    """Separator style options."""
    
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"


@dataclass
class FileContent:
    """Content from a single file with metadata."""
    
    path: Path
    content: str
    format: str
    size_bytes: int
    modified: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CombinedContent:
    """Combined content from multiple files."""
    
    content: str
    source_count: int
    total_size_bytes: int
    sources: list[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "content_length": len(self.content),
            "source_count": self.source_count,
            "total_size_bytes": self.total_size_bytes,
            "sources": self.sources,
        }


class FileCombiner:
    """
    Combines multiple files with clear separators.
    
    Inserts metadata-rich separators between files to help
    LLMs understand source boundaries.
    
    Example:
        >>> combiner = FileCombiner()
        >>> result = combiner.combine([
        ...     FileContent(path=Path("a.md"), content="...", format="markdown", size_bytes=100),
        ...     FileContent(path=Path("b.md"), content="...", format="markdown", size_bytes=150),
        ... ])
        >>> print(result.content)
    """
    
    # Default separator templates
    TEMPLATES = {
        SeparatorStyle.MINIMAL: """
---
SOURCE: {{ filename }}
---
{{ content }}
""",
        SeparatorStyle.STANDARD: """
---
SOURCE: {{ filename }}
TYPE: {{ format }}
INDEX: {{ index }} of {{ total }}
---

{{ content }}

---
END SOURCE: {{ filename }}
---
""",
        SeparatorStyle.DETAILED: """
---
SOURCE: {{ filename }}
PATH: {{ path }}
TYPE: {{ format }}
SIZE: {{ size_bytes }} bytes
{% if modified %}MODIFIED: {{ modified }}{% endif %}
INDEX: {{ index }} of {{ total }}
{% for key, value in metadata.items() %}{{ key }}: {{ value }}
{% endfor %}---

{{ content }}

---
END SOURCE: {{ filename }}
---
""",
    }
    
    def __init__(
        self,
        style: SeparatorStyle = SeparatorStyle.STANDARD,
        include_metadata: bool = True,
        custom_template: str | None = None,
    ):
        """
        Initialise the combiner.
        
        Args:
            style: Separator style.
            include_metadata: Whether to include metadata in separators.
            custom_template: Optional custom Jinja2 template.
        """
        self._style = style
        self._include_metadata = include_metadata
        self._custom_template = custom_template
    
    def combine(self, files: list[FileContent]) -> CombinedContent:
        """
        Combine multiple files with separators.
        
        Args:
            files: List of file contents to combine.
        
        Returns:
            CombinedContent with combined text and metadata.
        """
        if not files:
            return CombinedContent(
                content="",
                source_count=0,
                total_size_bytes=0,
            )
        
        template = self._get_template()
        combined_parts = []
        sources = []
        total = len(files)
        
        for index, file_content in enumerate(files, 1):
            # Render separator with content
            rendered = template.render(
                filename=file_content.path.name,
                path=str(file_content.path),
                format=file_content.format,
                size_bytes=file_content.size_bytes,
                modified=file_content.modified.isoformat() if file_content.modified else None,
                index=index,
                total=total,
                content=file_content.content,
                metadata=file_content.metadata if self._include_metadata else {},
            )
            combined_parts.append(rendered.strip())
            
            # Track source
            sources.append({
                "filename": file_content.path.name,
                "path": str(file_content.path),
                "format": file_content.format,
                "size_bytes": file_content.size_bytes,
                "index": index,
            })
        
        return CombinedContent(
            content="\n\n".join(combined_parts),
            source_count=len(files),
            total_size_bytes=sum(f.size_bytes for f in files),
            sources=sources,
        )
    
    def combine_from_paths(
        self,
        paths: list[Path],
        base_path: Path | None = None,
    ) -> CombinedContent:
        """
        Combine files from paths.
        
        Args:
            paths: File paths to combine.
            base_path: Base path for relative paths.
        
        Returns:
            CombinedContent with combined text.
        """
        files = []
        for path in paths:
            if path.exists() and path.is_file():
                content = path.read_text(encoding="utf-8")
                stat = path.stat()
                
                files.append(FileContent(
                    path=path if base_path is None else path.relative_to(base_path),
                    content=content,
                    format=self._detect_format(path),
                    size_bytes=stat.st_size,
                    modified=datetime.fromtimestamp(stat.st_mtime),
                ))
        
        return self.combine(files)
    
    def set_style(self, style: SeparatorStyle) -> None:
        """Set separator style."""
        self._style = style
    
    def set_custom_template(self, template: str) -> None:
        """Set a custom separator template."""
        self._custom_template = template
    
    def _get_template(self) -> Template:
        """Get the appropriate template."""
        if self._custom_template:
            return Template(self._custom_template)
        return Template(self.TEMPLATES[self._style])
    
    def _detect_format(self, path: Path) -> str:
        """Detect file format from extension."""
        ext = path.suffix.lower()
        format_map = {
            ".csv": "CSV",
            ".json": "JSON",
            ".md": "Markdown",
            ".markdown": "Markdown",
            ".txt": "Text",
            ".yaml": "YAML",
            ".yml": "YAML",
        }
        return format_map.get(ext, "Unknown")


def combine_files(
    paths: list[Path],
    style: SeparatorStyle = SeparatorStyle.STANDARD,
) -> CombinedContent:
    """
    Convenience function to combine files.
    
    Args:
        paths: File paths to combine.
        style: Separator style.
    
    Returns:
        CombinedContent with combined text.
    """
    combiner = FileCombiner(style=style)
    return combiner.combine_from_paths(paths)
