"""
URL caching for remote data sources (F-091).

Provides disk-based caching with ETag support for efficient re-fetching
of remote data sources.
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from persona.core.data.url import URLSource
from persona.core.platform import ensure_dir, get_cache_dir


@dataclass
class CacheEntry:
    """A cached URL entry.

    Attributes:
        url: The original URL.
        resolved_url: The URL after normalisation.
        content_path: Path to the cached content file.
        metadata_path: Path to the metadata JSON file.
        etag: ETag for conditional requests.
        last_modified: Last-Modified header value.
        fetched_at: When the content was fetched.
        expires_at: When the cache entry expires.
        size_bytes: Size of the cached content.
    """

    url: str
    resolved_url: str
    content_path: Path
    metadata_path: Path
    etag: str | None = None
    last_modified: str | None = None
    fetched_at: datetime | None = None
    expires_at: datetime | None = None
    size_bytes: int = 0

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.expires_at is None:
            return True
        return datetime.now() > self.expires_at

    def get_content(self) -> str:
        """Read the cached content.

        Returns:
            Cached content as string.

        Raises:
            FileNotFoundError: If cache file doesn't exist.
        """
        return self.content_path.read_text(encoding="utf-8")


class URLCache:
    """Disk-based cache for URL content with ETag support.

    Cache structure:
        <cache_dir>/url_data/
            <hash>/
                content.<ext>    # The actual data
                metadata.json    # URLSource as JSON

    Example:
        >>> cache = URLCache()
        >>> cache.put("https://example.com/data.csv", "col1,col2\\n1,2", source)
        >>> entry = cache.get("https://example.com/data.csv")
        >>> if entry and not entry.is_expired:
        ...     content = entry.get_content()
    """

    DEFAULT_TTL_HOURS = 24
    CACHE_SUBDIR = "url_data"

    def __init__(
        self,
        cache_dir: Path | None = None,
        ttl_hours: int = DEFAULT_TTL_HOURS,
    ) -> None:
        """Initialise the URL cache.

        Args:
            cache_dir: Base cache directory. Uses platform default if None.
            ttl_hours: Time-to-live for cache entries in hours.
        """
        if cache_dir is None:
            cache_dir = get_cache_dir()

        self.cache_dir = cache_dir / self.CACHE_SUBDIR
        self.ttl = timedelta(hours=ttl_hours)

    def _get_cache_key(self, url: str) -> str:
        """Generate a cache key for a URL.

        Args:
            url: URL to hash.

        Returns:
            SHA256 hash of the URL.
        """
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]

    def _get_cache_path(self, url: str) -> Path:
        """Get the cache directory for a URL.

        Args:
            url: URL to cache.

        Returns:
            Path to the cache directory.
        """
        return self.cache_dir / self._get_cache_key(url)

    def _infer_extension(self, url: str, content_type: str = "") -> str:
        """Infer file extension from URL or content type.

        Args:
            url: The URL.
            content_type: MIME type.

        Returns:
            File extension (default: "txt").
        """
        # Check URL extension
        url_lower = url.lower()
        for ext in [".csv", ".json", ".yaml", ".yml", ".md", ".html", ".txt", ".org"]:
            if ext in url_lower:
                return ext.lstrip(".")

        # Check content type
        type_map = {
            "text/csv": "csv",
            "application/json": "json",
            "text/yaml": "yaml",
            "text/markdown": "md",
            "text/html": "html",
        }
        base_type = content_type.split(";")[0].strip().lower()
        return type_map.get(base_type, "txt")

    def get(self, url: str) -> CacheEntry | None:
        """Get a cached entry for a URL.

        Args:
            url: URL to look up.

        Returns:
            CacheEntry if found and valid, None otherwise.
        """
        cache_path = self._get_cache_path(url)
        metadata_path = cache_path / "metadata.json"

        if not metadata_path.exists():
            return None

        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

        # Find content file
        content_files = list(cache_path.glob("content.*"))
        if not content_files:
            return None

        content_path = content_files[0]

        # Parse timestamps
        fetched_at = None
        expires_at = None
        if "fetched_at" in metadata:
            fetched_at = datetime.fromisoformat(metadata["fetched_at"])
            expires_at = fetched_at + self.ttl

        return CacheEntry(
            url=url,
            resolved_url=metadata.get("resolved_url", url),
            content_path=content_path,
            metadata_path=metadata_path,
            etag=metadata.get("etag"),
            last_modified=metadata.get("last_modified"),
            fetched_at=fetched_at,
            expires_at=expires_at,
            size_bytes=metadata.get("size_bytes", 0),
        )

    def put(
        self,
        url: str,
        content: str,
        source: URLSource,
    ) -> CacheEntry:
        """Store content in the cache.

        Args:
            url: URL being cached.
            content: Content to cache.
            source: URLSource metadata.

        Returns:
            CacheEntry for the stored content.
        """
        cache_path = self._get_cache_path(url)
        ensure_dir(cache_path)

        # Determine extension
        ext = self._infer_extension(url, source.content_type)
        content_path = cache_path / f"content.{ext}"
        metadata_path = cache_path / "metadata.json"

        # Remove any existing content files
        for existing in cache_path.glob("content.*"):
            existing.unlink()

        # Write content
        content_path.write_text(content, encoding="utf-8")

        # Write metadata
        metadata: dict[str, Any] = {
            "url": url,
            "resolved_url": source.resolved_url,
            "content_type": source.content_type,
            "fetched_at": source.fetched_at.isoformat(),
            "size_bytes": source.size_bytes,
            "sha256": source.sha256,
        }

        if source.etag:
            metadata["etag"] = source.etag
        if source.last_modified:
            metadata["last_modified"] = source.last_modified
        if source.attribution:
            metadata["attribution"] = source.attribution.to_dict()

        metadata_path.write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )

        return CacheEntry(
            url=url,
            resolved_url=source.resolved_url,
            content_path=content_path,
            metadata_path=metadata_path,
            etag=source.etag,
            last_modified=source.last_modified,
            fetched_at=source.fetched_at,
            expires_at=source.fetched_at + self.ttl,
            size_bytes=source.size_bytes,
        )

    def get_etag(self, url: str) -> str | None:
        """Get the ETag for a cached URL.

        Args:
            url: URL to look up.

        Returns:
            ETag if available, None otherwise.
        """
        entry = self.get(url)
        return entry.etag if entry else None

    def invalidate(self, url: str) -> bool:
        """Remove a URL from the cache.

        Args:
            url: URL to remove.

        Returns:
            True if entry was removed, False if not found.
        """
        cache_path = self._get_cache_path(url)

        if not cache_path.exists():
            return False

        # Remove all files in cache directory
        for file in cache_path.iterdir():
            file.unlink()
        cache_path.rmdir()

        return True

    def clear_expired(self) -> int:
        """Remove all expired cache entries.

        Returns:
            Number of entries removed.
        """
        if not self.cache_dir.exists():
            return 0

        count = 0
        for entry_dir in self.cache_dir.iterdir():
            if not entry_dir.is_dir():
                continue

            metadata_path = entry_dir / "metadata.json"
            if not metadata_path.exists():
                # Invalid entry, remove it
                self._remove_dir(entry_dir)
                count += 1
                continue

            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                fetched_at = datetime.fromisoformat(metadata["fetched_at"])
                expires_at = fetched_at + self.ttl

                if datetime.now() > expires_at:
                    self._remove_dir(entry_dir)
                    count += 1
            except (json.JSONDecodeError, KeyError, OSError):
                # Invalid entry, remove it
                self._remove_dir(entry_dir)
                count += 1

        return count

    def clear_all(self) -> int:
        """Remove all cache entries.

        Returns:
            Number of entries removed.
        """
        if not self.cache_dir.exists():
            return 0

        count = 0
        for entry_dir in self.cache_dir.iterdir():
            if entry_dir.is_dir():
                self._remove_dir(entry_dir)
                count += 1

        return count

    def _remove_dir(self, path: Path) -> None:
        """Remove a directory and its contents.

        Args:
            path: Directory to remove.
        """
        for file in path.iterdir():
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                self._remove_dir(file)
        path.rmdir()

    def list_entries(self) -> list[CacheEntry]:
        """List all cache entries.

        Returns:
            List of CacheEntry objects.
        """
        if not self.cache_dir.exists():
            return []

        entries = []
        for entry_dir in self.cache_dir.iterdir():
            if not entry_dir.is_dir():
                continue

            metadata_path = entry_dir / "metadata.json"
            if not metadata_path.exists():
                continue

            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                url = metadata.get("url", "")

                entry = self.get(url)
                if entry:
                    entries.append(entry)
            except (json.JSONDecodeError, OSError):
                continue

        return entries

    def get_total_size(self) -> int:
        """Get total size of cached content in bytes.

        Returns:
            Total size in bytes.
        """
        return sum(entry.size_bytes for entry in self.list_entries())
