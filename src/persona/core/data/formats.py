"""
Format-specific data loaders.

This module provides loaders for various file formats commonly used
in qualitative research data.
"""

import csv
import json
from pathlib import Path
from typing import Any

import yaml

from persona.core.data.loader import FormatLoader


class CSVLoader(FormatLoader):
    """Loader for CSV files."""

    @property
    def extensions(self) -> list[str]:
        return [".csv"]

    def load(self, path: Path) -> str:
        """
        Load CSV file and convert to readable text format.

        Each row is converted to a readable format with field names.
        """
        path = Path(path)

        with open(path, newline="", encoding="utf-8") as f:
            content = f.read()

        return self.load_content(content)

    def load_content(self, content: str) -> str:
        """
        Load CSV content from string and convert to readable text format.

        Args:
            content: Raw CSV content.

        Returns:
            Formatted readable text.
        """
        import io

        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)

        if not rows:
            return ""

        # Convert to readable text format
        output = []
        for i, row in enumerate(rows, 1):
            output.append(f"## Entry {i}")
            for key, value in row.items():
                if value:  # Skip empty values
                    output.append(f"**{key}**: {value}")
            output.append("")  # Blank line between entries

        return "\n".join(output)


class JSONLoader(FormatLoader):
    """Loader for JSON files."""

    @property
    def extensions(self) -> list[str]:
        return [".json"]

    def load(self, path: Path) -> str:
        """
        Load JSON file and convert to readable text format.

        Handles both array and object structures.
        """
        path = Path(path)

        with open(path, encoding="utf-8") as f:
            content = f.read()

        return self.load_content(content)

    def load_content(self, content: str) -> str:
        """
        Load JSON content from string and convert to readable text format.

        Args:
            content: Raw JSON content.

        Returns:
            Formatted readable text.
        """
        data = json.loads(content)
        return self._format_json(data)

    def _format_json(self, data: Any, depth: int = 0) -> str:
        """Recursively format JSON data as readable text."""
        indent = "  " * depth

        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{indent}**{key}**:")
                    lines.append(self._format_json(value, depth + 1))
                else:
                    lines.append(f"{indent}**{key}**: {value}")
            return "\n".join(lines)

        elif isinstance(data, list):
            lines = []
            for i, item in enumerate(data, 1):
                lines.append(f"{indent}### Item {i}")
                lines.append(self._format_json(item, depth + 1))
                lines.append("")
            return "\n".join(lines)

        else:
            return f"{indent}{data}"


class MarkdownLoader(FormatLoader):
    """Loader for Markdown files."""

    @property
    def extensions(self) -> list[str]:
        return [".md", ".markdown"]

    def load(self, path: Path) -> str:
        """Load Markdown file as-is (already in readable format)."""
        path = Path(path)
        return path.read_text(encoding="utf-8")


class TextLoader(FormatLoader):
    """Loader for plain text files."""

    @property
    def extensions(self) -> list[str]:
        return [".txt", ".text"]

    def load(self, path: Path) -> str:
        """Load plain text file."""
        path = Path(path)
        return path.read_text(encoding="utf-8")


class YAMLLoader(FormatLoader):
    """Loader for YAML files."""

    @property
    def extensions(self) -> list[str]:
        return [".yaml", ".yml"]

    def load(self, path: Path) -> str:
        """
        Load YAML file and convert to readable text format.

        Uses the same formatting approach as JSON.
        """
        path = Path(path)

        with open(path, encoding="utf-8") as f:
            content = f.read()

        return self.load_content(content)

    def load_content(self, content: str) -> str:
        """
        Load YAML content from string and convert to readable text format.

        Args:
            content: Raw YAML content.

        Returns:
            Formatted readable text.
        """
        data = yaml.safe_load(content)

        if data is None:
            return ""

        return self._format_yaml(data)

    def _format_yaml(self, data: Any, depth: int = 0) -> str:
        """Recursively format YAML data as readable text."""
        indent = "  " * depth

        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{indent}**{key}**:")
                    lines.append(self._format_yaml(value, depth + 1))
                else:
                    lines.append(f"{indent}**{key}**: {value}")
            return "\n".join(lines)

        elif isinstance(data, list):
            lines = []
            for i, item in enumerate(data, 1):
                lines.append(f"{indent}### Item {i}")
                lines.append(self._format_yaml(item, depth + 1))
                lines.append("")
            return "\n".join(lines)

        else:
            return f"{indent}{data}"


class OrgLoader(FormatLoader):
    """Loader for Org-mode files."""

    @property
    def extensions(self) -> list[str]:
        return [".org"]

    def load(self, path: Path) -> str:
        """
        Load Org-mode file and convert to readable format.

        Basic conversion: headers become markdown headers, lists preserved.
        """
        path = Path(path)
        content = path.read_text(encoding="utf-8")

        lines = []
        for line in content.split("\n"):
            # Convert Org headers to Markdown headers
            if line.startswith("*"):
                # Count asterisks for header level
                level = len(line) - len(line.lstrip("*"))
                text = line.lstrip("* ").strip()
                lines.append("#" * level + " " + text)
            else:
                lines.append(line)

        return "\n".join(lines)


class HTMLLoader(FormatLoader):
    """Loader for HTML files."""

    @property
    def extensions(self) -> list[str]:
        return [".html", ".htm"]

    def load(self, path: Path) -> str:
        """
        Load HTML file and extract text content.

        Strips HTML tags and returns plain text content.
        """
        path = Path(path)
        content = path.read_text(encoding="utf-8")
        return self.load_content(content)

    def load_content(self, content: str) -> str:
        """
        Load HTML content from string and extract text content.

        Args:
            content: Raw HTML content.

        Returns:
            Extracted plain text.
        """
        import re

        # Remove script and style elements
        content = re.sub(
            r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE
        )
        content = re.sub(
            r"<style[^>]*>.*?</style>", "", content, flags=re.DOTALL | re.IGNORECASE
        )

        # Convert common block elements to newlines
        content = re.sub(
            r"<(br|p|div|h[1-6]|li|tr)[^>]*>", "\n", content, flags=re.IGNORECASE
        )

        # Remove all remaining HTML tags
        content = re.sub(r"<[^>]+>", "", content)

        # Decode common HTML entities
        content = content.replace("&nbsp;", " ")
        content = content.replace("&amp;", "&")
        content = content.replace("&lt;", "<")
        content = content.replace("&gt;", ">")
        content = content.replace("&quot;", '"')
        content = content.replace("&#39;", "'")

        # Clean up whitespace
        lines = [line.strip() for line in content.split("\n")]
        lines = [line for line in lines if line]

        return "\n".join(lines)
