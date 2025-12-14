"""
Persona export functionality.

This module provides the PersonaExporter class for exporting
personas to various design tool formats.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import json


class ExportFormat(Enum):
    """Supported export formats."""

    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    FIGMA = "figma"
    MIRO = "miro"
    UXPRESSIA = "uxpressia"
    CSV = "csv"


@dataclass
class ExportResult:
    """
    Result of an export operation.

    Attributes:
        success: Whether export succeeded.
        format: Export format used.
        output_path: Path to exported file(s).
        persona_count: Number of personas exported.
        error: Error message if failed.
    """

    success: bool
    format: ExportFormat
    output_path: Path | None = None
    persona_count: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "format": self.format.value,
            "output_path": str(self.output_path) if self.output_path else None,
            "persona_count": self.persona_count,
            "error": self.error,
        }


class PersonaExporter:
    """
    Exports personas to various formats.

    Supports JSON, Markdown, HTML, and design tool formats
    like Figma and Miro.

    Example:
        exporter = PersonaExporter()
        result = exporter.export(personas, ExportFormat.FIGMA, Path("./output"))
        print(f"Exported {result.persona_count} personas")
    """

    def __init__(self) -> None:
        """Initialise the exporter."""
        self._exporters = {
            ExportFormat.JSON: self._export_json,
            ExportFormat.MARKDOWN: self._export_markdown,
            ExportFormat.HTML: self._export_html,
            ExportFormat.FIGMA: self._export_figma,
            ExportFormat.MIRO: self._export_miro,
            ExportFormat.UXPRESSIA: self._export_uxpressia,
            ExportFormat.CSV: self._export_csv,
        }

    def export(
        self,
        personas: list[Any],
        format: ExportFormat,
        output_path: Path,
        **options: Any,
    ) -> ExportResult:
        """
        Export personas to specified format.

        Args:
            personas: List of personas to export.
            format: Export format.
            output_path: Output file or directory path.
            **options: Format-specific options.

        Returns:
            ExportResult with outcome.
        """
        try:
            exporter = self._exporters.get(format)
            if exporter is None:
                return ExportResult(
                    success=False,
                    format=format,
                    error=f"Unsupported format: {format.value}",
                )

            # Ensure output directory exists
            if output_path.suffix:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_path.mkdir(parents=True, exist_ok=True)

            result = exporter(personas, output_path, **options)
            result.persona_count = len(personas)
            return result

        except Exception as e:
            return ExportResult(
                success=False,
                format=format,
                error=str(e),
            )

    def export_single(
        self,
        persona: Any,
        format: ExportFormat,
        output_path: Path,
        **options: Any,
    ) -> ExportResult:
        """
        Export a single persona.

        Args:
            persona: Persona to export.
            format: Export format.
            output_path: Output file path.
            **options: Format-specific options.

        Returns:
            ExportResult with outcome.
        """
        return self.export([persona], format, output_path, **options)

    def preview(
        self,
        personas: list[Any],
        format: ExportFormat,
        **options: Any,
    ) -> str:
        """
        Preview export without writing to file.

        Args:
            personas: Personas to preview.
            format: Export format.
            **options: Format-specific options.

        Returns:
            String preview of export content.
        """
        if format == ExportFormat.JSON:
            return self._to_json(personas, **options)
        elif format == ExportFormat.MARKDOWN:
            return self._to_markdown(personas, **options)
        elif format == ExportFormat.HTML:
            return self._to_html(personas, **options)
        elif format == ExportFormat.FIGMA:
            return self._to_figma_json(personas, **options)
        elif format == ExportFormat.MIRO:
            return self._to_miro_json(personas, **options)
        elif format == ExportFormat.UXPRESSIA:
            return self._to_uxpressia_json(personas, **options)
        elif format == ExportFormat.CSV:
            return self._to_csv(personas, **options)
        else:
            return f"Preview not available for {format.value}"

    def list_formats(self) -> list[dict[str, str]]:
        """
        List available export formats.

        Returns:
            List of format information.
        """
        return [
            {"id": "json", "name": "JSON", "extension": ".json"},
            {"id": "markdown", "name": "Markdown", "extension": ".md"},
            {"id": "html", "name": "HTML", "extension": ".html"},
            {"id": "figma", "name": "Figma", "extension": ".json"},
            {"id": "miro", "name": "Miro", "extension": ".json"},
            {"id": "uxpressia", "name": "UXPressia", "extension": ".json"},
            {"id": "csv", "name": "CSV", "extension": ".csv"},
        ]

    def _export_json(
        self,
        personas: list[Any],
        output_path: Path,
        **options: Any,
    ) -> ExportResult:
        """Export to JSON format."""
        content = self._to_json(personas, **options)

        if output_path.is_dir():
            output_path = output_path / "personas.json"

        with open(output_path, "w") as f:
            f.write(content)

        return ExportResult(
            success=True,
            format=ExportFormat.JSON,
            output_path=output_path,
        )

    def _export_markdown(
        self,
        personas: list[Any],
        output_path: Path,
        **options: Any,
    ) -> ExportResult:
        """Export to Markdown format."""
        content = self._to_markdown(personas, **options)

        if output_path.is_dir():
            output_path = output_path / "personas.md"

        with open(output_path, "w") as f:
            f.write(content)

        return ExportResult(
            success=True,
            format=ExportFormat.MARKDOWN,
            output_path=output_path,
        )

    def _export_html(
        self,
        personas: list[Any],
        output_path: Path,
        **options: Any,
    ) -> ExportResult:
        """Export to HTML format."""
        content = self._to_html(personas, **options)

        if output_path.is_dir():
            output_path = output_path / "personas.html"

        with open(output_path, "w") as f:
            f.write(content)

        return ExportResult(
            success=True,
            format=ExportFormat.HTML,
            output_path=output_path,
        )

    def _export_figma(
        self,
        personas: list[Any],
        output_path: Path,
        **options: Any,
    ) -> ExportResult:
        """Export to Figma-compatible format."""
        content = self._to_figma_json(personas, **options)

        if output_path.is_dir():
            output_path = output_path / "personas-figma.json"

        with open(output_path, "w") as f:
            f.write(content)

        return ExportResult(
            success=True,
            format=ExportFormat.FIGMA,
            output_path=output_path,
        )

    def _export_miro(
        self,
        personas: list[Any],
        output_path: Path,
        **options: Any,
    ) -> ExportResult:
        """Export to Miro-compatible format."""
        content = self._to_miro_json(personas, **options)

        if output_path.is_dir():
            output_path = output_path / "personas-miro.json"

        with open(output_path, "w") as f:
            f.write(content)

        return ExportResult(
            success=True,
            format=ExportFormat.MIRO,
            output_path=output_path,
        )

    def _export_uxpressia(
        self,
        personas: list[Any],
        output_path: Path,
        **options: Any,
    ) -> ExportResult:
        """Export to UXPressia-compatible format."""
        content = self._to_uxpressia_json(personas, **options)

        if output_path.is_dir():
            output_path = output_path / "personas-uxpressia.json"

        with open(output_path, "w") as f:
            f.write(content)

        return ExportResult(
            success=True,
            format=ExportFormat.UXPRESSIA,
            output_path=output_path,
        )

    def _export_csv(
        self,
        personas: list[Any],
        output_path: Path,
        **options: Any,
    ) -> ExportResult:
        """Export to CSV format."""
        content = self._to_csv(personas, **options)

        if output_path.is_dir():
            output_path = output_path / "personas.csv"

        with open(output_path, "w") as f:
            f.write(content)

        return ExportResult(
            success=True,
            format=ExportFormat.CSV,
            output_path=output_path,
        )

    def _to_json(self, personas: list[Any], **options: Any) -> str:
        """Convert personas to JSON string."""
        data = []
        for persona in personas:
            if hasattr(persona, "to_dict"):
                data.append(persona.to_dict())
            else:
                data.append({
                    "id": getattr(persona, "id", "unknown"),
                    "name": getattr(persona, "name", "Unknown"),
                    "goals": list(getattr(persona, "goals", []) or []),
                    "pain_points": list(getattr(persona, "pain_points", []) or []),
                    "behaviours": list(getattr(persona, "behaviours", []) or []),
                    "demographics": dict(getattr(persona, "demographics", {}) or {}),
                })

        return json.dumps({"personas": data}, indent=2)

    def _to_markdown(self, personas: list[Any], **options: Any) -> str:
        """Convert personas to Markdown string."""
        lines = ["# Personas", ""]

        for persona in personas:
            name = getattr(persona, "name", "Unknown")
            persona_id = getattr(persona, "id", "unknown")

            lines.extend([
                f"## {name}",
                f"**ID:** {persona_id}",
                "",
            ])

            # Demographics
            demographics = getattr(persona, "demographics", {}) or {}
            if demographics:
                lines.append("### Demographics")
                for key, value in demographics.items():
                    lines.append(f"- **{key}:** {value}")
                lines.append("")

            # Goals
            goals = getattr(persona, "goals", []) or []
            if goals:
                lines.append("### Goals")
                for goal in goals:
                    lines.append(f"- {goal}")
                lines.append("")

            # Pain points
            pain_points = getattr(persona, "pain_points", []) or []
            if pain_points:
                lines.append("### Pain Points")
                for pain in pain_points:
                    lines.append(f"- {pain}")
                lines.append("")

            # Behaviours
            behaviours = getattr(persona, "behaviours", []) or []
            if behaviours:
                lines.append("### Behaviours")
                for behaviour in behaviours:
                    lines.append(f"- {behaviour}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _to_html(self, personas: list[Any], **options: Any) -> str:
        """Convert personas to HTML string."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '<meta charset="UTF-8">',
            "<title>Personas</title>",
            "<style>",
            "body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
            ".persona { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }",
            ".persona h2 { margin-top: 0; }",
            ".section { margin: 15px 0; }",
            ".section h3 { margin-bottom: 10px; color: #666; }",
            "ul { margin: 0; padding-left: 20px; }",
            ".demographics { background: #f5f5f5; padding: 10px; border-radius: 4px; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Personas</h1>",
        ]

        for persona in personas:
            name = getattr(persona, "name", "Unknown")
            persona_id = getattr(persona, "id", "unknown")

            html_parts.append('<div class="persona">')
            html_parts.append(f'<h2>{name}</h2>')
            html_parts.append(f'<p><small>ID: {persona_id}</small></p>')

            # Demographics
            demographics = getattr(persona, "demographics", {}) or {}
            if demographics:
                html_parts.append('<div class="section demographics">')
                html_parts.append("<h3>Demographics</h3>")
                for key, value in demographics.items():
                    html_parts.append(f"<p><strong>{key}:</strong> {value}</p>")
                html_parts.append("</div>")

            # Goals
            goals = getattr(persona, "goals", []) or []
            if goals:
                html_parts.append('<div class="section">')
                html_parts.append("<h3>Goals</h3>")
                html_parts.append("<ul>")
                for goal in goals:
                    html_parts.append(f"<li>{goal}</li>")
                html_parts.append("</ul>")
                html_parts.append("</div>")

            # Pain points
            pain_points = getattr(persona, "pain_points", []) or []
            if pain_points:
                html_parts.append('<div class="section">')
                html_parts.append("<h3>Pain Points</h3>")
                html_parts.append("<ul>")
                for pain in pain_points:
                    html_parts.append(f"<li>{pain}</li>")
                html_parts.append("</ul>")
                html_parts.append("</div>")

            html_parts.append("</div>")

        html_parts.extend([
            "</body>",
            "</html>",
        ])

        return "\n".join(html_parts)

    def _to_figma_json(self, personas: list[Any], **options: Any) -> str:
        """Convert personas to Figma-compatible JSON."""
        figma_data = {
            "type": "FRAME",
            "name": "Personas",
            "children": [],
        }

        for persona in personas:
            name = getattr(persona, "name", "Unknown")
            goals = getattr(persona, "goals", []) or []
            pain_points = getattr(persona, "pain_points", []) or []

            persona_frame = {
                "type": "FRAME",
                "name": f"Persona: {name}",
                "children": [
                    {
                        "type": "TEXT",
                        "name": "Name",
                        "characters": name,
                    },
                    {
                        "type": "TEXT",
                        "name": "Goals",
                        "characters": "\n".join(f"• {g}" for g in goals),
                    },
                    {
                        "type": "TEXT",
                        "name": "Pain Points",
                        "characters": "\n".join(f"• {p}" for p in pain_points),
                    },
                ],
            }
            figma_data["children"].append(persona_frame)

        return json.dumps(figma_data, indent=2)

    def _to_miro_json(self, personas: list[Any], **options: Any) -> str:
        """Convert personas to Miro-compatible JSON."""
        miro_data = {
            "type": "board_content",
            "items": [],
        }

        x_offset = 0
        for persona in personas:
            name = getattr(persona, "name", "Unknown")
            goals = getattr(persona, "goals", []) or []
            pain_points = getattr(persona, "pain_points", []) or []

            card = {
                "type": "card",
                "title": name,
                "description": (
                    "**Goals:**\n" +
                    "\n".join(f"- {g}" for g in goals) +
                    "\n\n**Pain Points:**\n" +
                    "\n".join(f"- {p}" for p in pain_points)
                ),
                "position": {"x": x_offset, "y": 0},
            }
            miro_data["items"].append(card)
            x_offset += 300

        return json.dumps(miro_data, indent=2)

    def _to_uxpressia_json(self, personas: list[Any], **options: Any) -> str:
        """Convert personas to UXPressia-compatible JSON."""
        uxpressia_data = {
            "version": "1.0",
            "personas": [],
        }

        for persona in personas:
            persona_id = getattr(persona, "id", "unknown")
            name = getattr(persona, "name", "Unknown")
            demographics = getattr(persona, "demographics", {}) or {}
            goals = getattr(persona, "goals", []) or []
            pain_points = getattr(persona, "pain_points", []) or []
            behaviours = getattr(persona, "behaviours", []) or []

            uxpressia_persona = {
                "id": persona_id,
                "name": name,
                "demographic": {
                    "age": demographics.get("age", ""),
                    "occupation": demographics.get("occupation", ""),
                    "location": demographics.get("location", ""),
                },
                "goals": [{"text": g} for g in goals],
                "painPoints": [{"text": p} for p in pain_points],
                "behaviors": [{"text": b} for b in behaviours],
            }
            uxpressia_data["personas"].append(uxpressia_persona)

        return json.dumps(uxpressia_data, indent=2)

    def _to_csv(self, personas: list[Any], **options: Any) -> str:
        """Convert personas to CSV string."""
        lines = ["id,name,goals,pain_points,behaviours,demographics"]

        for persona in personas:
            persona_id = getattr(persona, "id", "unknown")
            name = getattr(persona, "name", "Unknown")
            goals = "; ".join(getattr(persona, "goals", []) or [])
            pain_points = "; ".join(getattr(persona, "pain_points", []) or [])
            behaviours = "; ".join(getattr(persona, "behaviours", []) or [])
            demographics = str(getattr(persona, "demographics", {}) or {})

            # Escape CSV fields
            def escape(s: str) -> str:
                if "," in s or '"' in s or "\n" in s:
                    return f'"{s.replace('"', '""')}"'
                return s

            lines.append(
                f"{escape(persona_id)},{escape(name)},{escape(goals)},"
                f"{escape(pain_points)},{escape(behaviours)},{escape(demographics)}"
            )

        return "\n".join(lines)
