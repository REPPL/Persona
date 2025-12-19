"""
Output management for generation results.

This module provides the OutputManager class for creating structured
output directories and saving generation results.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from persona.core.generation.parser import Persona
from persona.core.generation.pipeline import GenerationResult
from persona.core.output.formatters import (
    JSONFormatter,
    MarkdownFormatter,
    TextFormatter,
)


class OutputManager:
    """
    Manages output directory structure and file saving.

    Creates timestamped output folders with consistent structure:

    ```
    outputs/YYYYMMDD_HHMMSS/
    ├── metadata.json       # Generation parameters and stats
    ├── prompt.txt          # The rendered prompt
    ├── full_response.txt   # Complete LLM response
    └── personas/
        ├── 01/
        │   ├── persona.json
        │   └── persona.md
        └── 02/
            ├── persona.json
            └── persona.md
    ```

    Example:
        manager = OutputManager("./outputs")
        output_dir = manager.save(result)
    """

    def __init__(
        self,
        base_dir: str | Path = "./outputs",
        timestamp_folders: bool = True,
    ) -> None:
        """
        Initialise the output manager.

        Args:
            base_dir: Base directory for outputs.
            timestamp_folders: Whether to use timestamped folder names.
        """
        self._base_dir = Path(base_dir)
        self._timestamp_folders = timestamp_folders

    def save(self, result: GenerationResult, name: str | None = None) -> Path:
        """
        Save generation results to output directory.

        Args:
            result: The generation result to save.
            name: Optional custom folder name (defaults to timestamp).

        Returns:
            Path to the created output directory.
        """
        # Create output directory
        output_dir = self._create_output_dir(name)

        # Save metadata
        self._save_metadata(output_dir, result)

        # Save prompt
        if result.prompt:
            self._save_prompt(output_dir, result.prompt)

        # Save full response
        if result.raw_response:
            self._save_full_response(output_dir, result.raw_response)

        # Save reasoning if present
        if result.reasoning:
            self._save_reasoning(output_dir, result.reasoning)

        # Save personas
        self._save_personas(output_dir, result.personas)

        # Save attribution for URL sources
        if result.url_sources:
            self._save_attribution(output_dir, result.url_sources)

        return output_dir

    def _create_output_dir(self, name: str | None = None) -> Path:
        """Create the output directory."""
        if name:
            dir_name = name
        elif self._timestamp_folders:
            dir_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            dir_name = "latest"

        output_dir = self._base_dir / dir_name
        output_dir.mkdir(parents=True, exist_ok=True)

        return output_dir

    def _save_metadata(self, output_dir: Path, result: GenerationResult) -> None:
        """Save generation metadata."""
        metadata: dict[str, Any] = {
            "generated_at": datetime.now().isoformat(),
            "provider": result.provider,
            "model": result.model,
            "persona_count": len(result.personas),
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "total_tokens": result.input_tokens + result.output_tokens,
            "source_files": [str(f) for f in result.source_files],
        }

        # Include URL sources if present
        if result.url_sources:
            url_source_data = []
            for source in result.url_sources:
                if hasattr(source, 'to_dict'):
                    url_source_data.append(source.to_dict())
            if url_source_data:
                metadata["url_sources"] = url_source_data

        metadata_path = output_dir / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _save_prompt(self, output_dir: Path, prompt: str) -> None:
        """Save the rendered prompt."""
        prompt_path = output_dir / "prompt.txt"
        prompt_path.write_text(prompt, encoding="utf-8")

    def _save_full_response(self, output_dir: Path, response: str) -> None:
        """Save the full LLM response."""
        response_path = output_dir / "full_response.txt"
        response_path.write_text(response, encoding="utf-8")

    def _save_reasoning(self, output_dir: Path, reasoning: str) -> None:
        """Save the LLM reasoning."""
        reasoning_path = output_dir / "reasoning.txt"
        reasoning_path.write_text(reasoning, encoding="utf-8")

    def _save_personas(self, output_dir: Path, personas: list[Persona]) -> None:
        """Save personas to individual directories."""
        personas_dir = output_dir / "personas"
        personas_dir.mkdir(exist_ok=True)

        json_formatter = JSONFormatter()
        md_formatter = MarkdownFormatter()
        txt_formatter = TextFormatter()

        for i, persona in enumerate(personas, 1):
            # Create numbered directory
            persona_dir = personas_dir / f"{i:02d}"
            persona_dir.mkdir(exist_ok=True)

            # Save in multiple formats
            (persona_dir / "persona.json").write_text(
                json_formatter.format(persona),
                encoding="utf-8",
            )
            (persona_dir / "persona.md").write_text(
                md_formatter.format(persona),
                encoding="utf-8",
            )
            (persona_dir / "persona.txt").write_text(
                txt_formatter.format(persona),
                encoding="utf-8",
            )

    def list_outputs(self) -> list[Path]:
        """
        List all output directories.

        Returns:
            List of output directory paths, sorted by name.
        """
        if not self._base_dir.exists():
            return []

        return sorted(
            [
                d
                for d in self._base_dir.iterdir()
                if d.is_dir() and (d / "metadata.json").exists()
            ]
        )

    def get_latest_output(self) -> Path | None:
        """
        Get the most recent output directory.

        Returns:
            Path to latest output, or None if no outputs exist.
        """
        outputs = self.list_outputs()
        return outputs[-1] if outputs else None

    def load_metadata(self, output_dir: Path) -> dict[str, Any]:
        """
        Load metadata from an output directory.

        Args:
            output_dir: Path to output directory.

        Returns:
            Metadata dictionary.
        """
        metadata_path = output_dir / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")

        with open(metadata_path, encoding="utf-8") as f:
            return json.load(f)

    def _save_attribution(self, output_dir: Path, url_sources: list) -> None:
        """
        Save attribution file for URL sources.

        Generates an attribution.md file documenting the external data sources
        used in persona generation, including licence and usage requirements.

        Args:
            output_dir: Output directory.
            url_sources: List of URLSource objects.
        """
        lines = [
            "# Data Attribution",
            "",
            "This persona generation used data from external sources.",
            "",
        ]

        for source in url_sources:
            # Get attribution if available
            if hasattr(source, 'attribution') and source.attribution:
                attribution = source.attribution
                lines.append(attribution.to_markdown())
                lines.append("")
            else:
                # Basic attribution from URL source metadata
                lines.append(f"## {source.original_url}")
                lines.append("")
                if hasattr(source, 'resolved_url') and source.resolved_url != source.original_url:
                    lines.append(f"- **Resolved URL:** {source.resolved_url}")
                if hasattr(source, 'fetched_at'):
                    lines.append(f"- **Fetched:** {source.fetched_at.isoformat()}")
                if hasattr(source, 'content_type') and source.content_type:
                    lines.append(f"- **Content Type:** {source.content_type}")
                if hasattr(source, 'size_bytes'):
                    lines.append(f"- **Size:** {source.size_bytes} bytes")
                lines.append("")

        lines.extend([
            "---",
            "",
            "*Users must credit the original data sources when using generated personas.*",
        ])

        attribution_path = output_dir / "attribution.md"
        attribution_path.write_text("\n".join(lines), encoding="utf-8")
