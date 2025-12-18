"""
Attribution metadata for data sources (F-091).

Provides structured attribution information for external data sources,
ensuring proper credit and licence compliance.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Attribution:
    """Attribution metadata for a data source.

    Attributes:
        title: Title of the data source.
        creators: List of creator names or organisations.
        source_url: URL where the data was obtained.
        licence: Licence identifier or description.
        access_date: Date when the data was accessed.
        authors: Optional list of individual authors.
        doi: Optional DOI for the data source.
        version: Optional version identifier.
        notify_email: Optional email for notification requirements.
        requirements: Optional list of usage requirements.
    """

    title: str
    creators: list[str] = field(default_factory=list)
    source_url: str = ""
    licence: str = ""
    access_date: datetime | None = None
    authors: list[str] = field(default_factory=list)
    doi: str | None = None
    version: str | None = None
    notify_email: str | None = None
    requirements: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation.

        Returns:
            Dictionary representation of attribution.
        """
        result: dict[str, Any] = {
            "title": self.title,
            "creators": self.creators,
            "source_url": self.source_url,
            "licence": self.licence,
        }

        if self.access_date:
            result["access_date"] = self.access_date.isoformat()
        if self.authors:
            result["authors"] = self.authors
        if self.doi:
            result["doi"] = self.doi
        if self.version:
            result["version"] = self.version
        if self.notify_email:
            result["notify_email"] = self.notify_email
        if self.requirements:
            result["requirements"] = self.requirements

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Attribution":
        """Create from dictionary.

        Args:
            data: Dictionary with attribution data.

        Returns:
            Attribution instance.
        """
        access_date = None
        if "access_date" in data and data["access_date"]:
            if isinstance(data["access_date"], str):
                access_date = datetime.fromisoformat(data["access_date"])
            elif isinstance(data["access_date"], datetime):
                access_date = data["access_date"]

        return cls(
            title=data.get("title", ""),
            creators=data.get("creators", []),
            source_url=data.get("source_url", ""),
            licence=data.get("licence", ""),
            access_date=access_date,
            authors=data.get("authors", []),
            doi=data.get("doi"),
            version=data.get("version"),
            notify_email=data.get("notify_email"),
            requirements=data.get("requirements", []),
        )

    def to_markdown(self) -> str:
        """Generate markdown attribution text.

        Returns:
            Markdown-formatted attribution.
        """
        lines = [f"## {self.title}", ""]

        if self.creators:
            lines.append(f"- **Source:** {', '.join(self.creators)}")
        if self.source_url:
            lines.append(f"- **URL:** {self.source_url}")
        if self.access_date:
            lines.append(f"- **Accessed:** {self.access_date.strftime('%Y-%m-%d')}")
        if self.licence:
            lines.append(f"- **Licence:** {self.licence}")
        if self.doi:
            lines.append(f"- **DOI:** {self.doi}")

        if self.requirements:
            lines.append("")
            lines.append("**Usage Requirements:**")
            for req in self.requirements:
                lines.append(f"- {req}")

        return "\n".join(lines)

    def get_citation(self) -> str:
        """Generate a citation string.

        Returns:
            Plain text citation.
        """
        parts = []

        if self.creators:
            parts.append(", ".join(self.creators))
        if self.title:
            parts.append(f'"{self.title}"')
        if self.access_date:
            parts.append(f"({self.access_date.year})")
        if self.source_url:
            parts.append(f"Available at: {self.source_url}")
        if self.doi:
            parts.append(f"DOI: {self.doi}")

        return ". ".join(parts) + "." if parts else ""
