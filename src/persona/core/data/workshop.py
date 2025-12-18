"""
Workshop data import functionality.

This module provides tools for importing co-creation workshop data
from photos of post-it notes on boards, using vision LLMs to extract
text and map it to empathy map categories.
"""

import base64
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

import yaml


class WorkshopCategory(Enum):
    """Categories for workshop post-it notes (Boag empathy map dimensions)."""

    TASKS = "tasks"
    FEELINGS = "feelings"
    INFLUENCES = "influences"
    PAIN_POINTS = "pain_points"
    GOALS = "goals"
    UNCATEGORISED = "uncategorised"


@dataclass
class PostItNote:
    """
    A single post-it note extracted from a workshop image.

    Attributes:
        text: The extracted text content.
        confidence: Extraction confidence (0.0 to 1.0).
        category: Assigned empathy map category.
        position: Optional spatial position (x, y) in image.
        colour: Optional detected colour.
    """

    text: str
    confidence: float = 1.0
    category: WorkshopCategory = WorkshopCategory.UNCATEGORISED
    position: tuple[float, float] | None = None
    colour: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "category": self.category.value,
            "position": self.position,
            "colour": self.colour,
        }


@dataclass
class WorkshopExtractionResult:
    """
    Result of extracting data from a workshop image.

    Attributes:
        source_image: Path to the source image.
        post_its: List of extracted post-it notes.
        clusters: Detected clusters of post-its.
        raw_response: Raw LLM response for debugging.
        overall_confidence: Overall extraction confidence.
    """

    source_image: Path
    post_its: list[PostItNote] = field(default_factory=list)
    clusters: list[list[int]] = field(default_factory=list)  # Indices into post_its
    raw_response: str = ""
    overall_confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_image": str(self.source_image),
            "post_its": [p.to_dict() for p in self.post_its],
            "clusters": self.clusters,
            "overall_confidence": self.overall_confidence,
        }


@dataclass
class WorkshopImportConfig:
    """
    Configuration for workshop import.

    Attributes:
        confidence_threshold: Minimum confidence for inclusion.
        auto_categorise: Whether to auto-assign categories.
        detect_clusters: Whether to detect spatial clusters.
        supported_formats: Supported image formats.
    """

    confidence_threshold: float = 0.5
    auto_categorise: bool = True
    detect_clusters: bool = True
    supported_formats: list[str] = field(
        default_factory=lambda: [".jpg", ".jpeg", ".png", ".webp"]
    )


class VisionExtractor(Protocol):
    """Protocol for vision-based text extraction."""

    def extract_from_image(self, image_path: Path) -> WorkshopExtractionResult:
        """Extract text and structure from an image."""
        ...


class MockVisionExtractor:
    """
    Mock vision extractor for testing without LLM access.

    Generates deterministic mock extractions based on image filename.
    """

    # Mock responses based on common workshop scenarios
    MOCK_EXTRACTIONS = {
        "tasks": [
            "Collecting new items",
            "Sharing discoveries",
            "Organizing collection",
            "Researching background",
        ],
        "feelings": [
            "Excited about finds",
            "Frustrated by gaps",
            "Proud of collection",
            "Connected to community",
        ],
        "influences": [
            "Online communities",
            "Expert recommendations",
            "Social media",
            "Friends and family",
        ],
        "pain_points": [
            "Limited budget",
            "Time constraints",
            "Missing information",
            "Storage space",
        ],
        "goals": [
            "Complete the collection",
            "Share knowledge",
            "Connect with others",
            "Preserve items",
        ],
    }

    def extract_from_image(self, image_path: Path) -> WorkshopExtractionResult:
        """Generate mock extraction based on filename."""
        filename = image_path.stem.lower()

        # Determine which mock data to use based on filename hints
        post_its = []

        # Generate post-its based on filename
        for category_name, items in self.MOCK_EXTRACTIONS.items():
            if category_name in filename or "all" in filename:
                category = WorkshopCategory(category_name)
                for i, text in enumerate(items[:3]):
                    post_its.append(
                        PostItNote(
                            text=text,
                            confidence=0.85 + (i * 0.03),
                            category=category,
                            position=(100 + i * 50, 100 + i * 30),
                        )
                    )

        # Default extraction if no specific category matched
        if not post_its:
            for category_name, items in self.MOCK_EXTRACTIONS.items():
                category = WorkshopCategory(category_name)
                post_its.append(
                    PostItNote(
                        text=items[0],
                        confidence=0.8,
                        category=category,
                    )
                )

        return WorkshopExtractionResult(
            source_image=image_path,
            post_its=post_its,
            clusters=[[i] for i in range(len(post_its))],
            raw_response="[Mock extraction]",
            overall_confidence=0.85,
        )


class LLMVisionExtractor:
    """
    Vision extractor using LLM APIs.

    Uses vision-capable LLMs to extract text and structure
    from workshop images.
    """

    # Prompt for extracting post-it content
    EXTRACTION_PROMPT = """Analyse this image of a workshop board with post-it notes.

Extract all visible text from the post-it notes and identify their likely category
based on empathy mapping (Boag method):
- tasks: What the participant is trying to accomplish
- feelings: Emotional responses and reactions
- influences: External factors affecting decisions
- pain_points: Frustrations and challenges
- goals: Desired outcomes and objectives

Return a JSON object with this structure:
{
    "post_its": [
        {
            "text": "extracted text",
            "confidence": 0.0-1.0,
            "category": "tasks|feelings|influences|pain_points|goals|uncategorised",
            "position": [x, y] or null,
            "colour": "colour name" or null
        }
    ],
    "clusters": [[indices of related post-its]],
    "overall_confidence": 0.0-1.0
}

Be thorough but only extract clearly visible text. Mark uncertain extractions
with lower confidence scores."""

    def __init__(self, provider: Any) -> None:
        """
        Initialise with an LLM provider.

        Args:
            provider: An LLM provider with vision capabilities.
        """
        self.provider = provider

    def extract_from_image(self, image_path: Path) -> WorkshopExtractionResult:
        """
        Extract post-it content using vision LLM.

        Args:
            image_path: Path to the workshop image.

        Returns:
            Extraction result with post-its and clusters.
        """
        # Read and encode image
        image_data = self._encode_image(image_path)

        # Call vision LLM
        response = self._call_vision_llm(image_data)

        # Parse response
        return self._parse_response(image_path, response)

    def _encode_image(self, path: Path) -> str:
        """Encode image as base64."""
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _call_vision_llm(self, image_data: str) -> str:
        """Call the vision LLM with the image."""
        # This would use the provider's vision API
        # For now, return empty to allow structure testing
        if hasattr(self.provider, "generate_with_image"):
            return self.provider.generate_with_image(
                self.EXTRACTION_PROMPT,
                image_data,
            )
        return "{}"

    def _parse_response(
        self,
        image_path: Path,
        response: str,
    ) -> WorkshopExtractionResult:
        """Parse LLM response into extraction result."""
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            return WorkshopExtractionResult(
                source_image=image_path,
                raw_response=response,
                overall_confidence=0.0,
            )

        post_its = []
        for item in data.get("post_its", []):
            category = WorkshopCategory.UNCATEGORISED
            cat_str = item.get("category", "uncategorised")
            try:
                category = WorkshopCategory(cat_str)
            except ValueError:
                pass

            position = item.get("position")
            if position and len(position) == 2:
                position = tuple(position)
            else:
                position = None

            post_its.append(
                PostItNote(
                    text=item.get("text", ""),
                    confidence=item.get("confidence", 0.5),
                    category=category,
                    position=position,
                    colour=item.get("colour"),
                )
            )

        return WorkshopExtractionResult(
            source_image=image_path,
            post_its=post_its,
            clusters=data.get("clusters", []),
            raw_response=response,
            overall_confidence=data.get("overall_confidence", 0.5),
        )


class WorkshopImporter:
    """
    Imports workshop data from images.

    Processes workshop photos, extracts post-it content,
    and generates editable empathy map YAML.

    Example:
        importer = WorkshopImporter()
        result = importer.import_images([Path("workshop1.jpg")])
        yaml_content = importer.to_editable_yaml(result)
    """

    def __init__(
        self,
        config: WorkshopImportConfig | None = None,
        extractor: VisionExtractor | None = None,
    ) -> None:
        """
        Initialise the importer.

        Args:
            config: Import configuration.
            extractor: Vision extractor to use (defaults to mock).
        """
        self.config = config or WorkshopImportConfig()
        self.extractor = extractor or MockVisionExtractor()

    def import_images(
        self,
        image_paths: list[Path],
    ) -> list[WorkshopExtractionResult]:
        """
        Import multiple workshop images.

        Args:
            image_paths: List of image paths to process.

        Returns:
            List of extraction results.
        """
        results = []

        for path in image_paths:
            path = Path(path)

            if not path.exists():
                continue

            if path.suffix.lower() not in self.config.supported_formats:
                continue

            result = self.extractor.extract_from_image(path)
            results.append(result)

        return results

    def import_directory(
        self,
        directory: Path,
        recursive: bool = False,
    ) -> list[WorkshopExtractionResult]:
        """
        Import all images from a directory.

        Args:
            directory: Directory to scan for images.
            recursive: Whether to search subdirectories.

        Returns:
            List of extraction results.
        """
        directory = Path(directory)

        if not directory.is_dir():
            return []

        image_paths = []
        pattern = "**/*" if recursive else "*"

        for fmt in self.config.supported_formats:
            image_paths.extend(directory.glob(f"{pattern}{fmt}"))

        return self.import_images(sorted(image_paths))

    def to_editable_yaml(
        self,
        results: list[WorkshopExtractionResult],
        participant_type: str = "workshop_participant",
    ) -> str:
        """
        Convert extraction results to editable YAML.

        Args:
            results: Extraction results to convert.
            participant_type: Name for the participant type.

        Returns:
            YAML string for manual editing.
        """
        # Aggregate post-its by category
        categories: dict[str, list[str]] = {
            "tasks": [],
            "feelings": [],
            "influences": [],
            "pain_points": [],
            "goals": [],
        }

        total_confidence = 0.0
        count = 0

        for result in results:
            for post_it in result.post_its:
                if post_it.confidence < self.config.confidence_threshold:
                    continue

                category = post_it.category.value
                if category in categories:
                    categories[category].append(post_it.text)
                    total_confidence += post_it.confidence
                    count += 1

        avg_confidence = total_confidence / count if count else 0.0

        # Build YAML structure
        data = {
            "# Workshop Import": None,
            "# Review and edit the extracted content below": None,
            "# Delete any incorrectly extracted items": None,
            "# Add missing items manually": None,
            "participants": len(results),
            "method": "co-creation workshop (auto-extracted)",
            "extraction_confidence": round(avg_confidence, 2),
            "data": [
                {
                    "participant_type": participant_type,
                    **{k: v for k, v in categories.items() if v},
                }
            ],
        }

        # Remove comment keys (they'll appear as comments)
        yaml_content = yaml.dump(
            {k: v for k, v in data.items() if not k.startswith("#")},
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

        # Add header comments
        header = """# Workshop Import Results
# Review and edit the extracted content below
# Delete any incorrectly extracted items
# Add missing items manually

"""
        return header + yaml_content

    def to_json(self, results: list[WorkshopExtractionResult]) -> str:
        """
        Convert extraction results to JSON.

        Args:
            results: Extraction results to convert.

        Returns:
            JSON string.
        """
        data = {
            "workshop_results": [r.to_dict() for r in results],
            "total_images": len(results),
            "total_post_its": sum(len(r.post_its) for r in results),
        }
        return json.dumps(data, indent=2)

    def filter_by_confidence(
        self,
        results: list[WorkshopExtractionResult],
        threshold: float | None = None,
    ) -> list[WorkshopExtractionResult]:
        """
        Filter post-its by confidence threshold.

        Args:
            results: Results to filter.
            threshold: Confidence threshold (uses config if not provided).

        Returns:
            Filtered results.
        """
        threshold = threshold or self.config.confidence_threshold

        filtered = []
        for result in results:
            filtered_post_its = [
                p for p in result.post_its if p.confidence >= threshold
            ]
            filtered.append(
                WorkshopExtractionResult(
                    source_image=result.source_image,
                    post_its=filtered_post_its,
                    clusters=result.clusters,
                    raw_response=result.raw_response,
                    overall_confidence=result.overall_confidence,
                )
            )

        return filtered
