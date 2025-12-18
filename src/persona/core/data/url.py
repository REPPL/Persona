"""
URL-based data fetching (F-091).

Provides functionality for fetching data from remote URLs with caching,
rate limiting, and attribution tracking.
"""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from persona.core.data.attribution import Attribution


class URLValidationError(Exception):
    """Raised when URL validation fails."""

    pass


class TermsNotAcceptedError(Exception):
    """Raised when terms have not been accepted for a URL source."""

    pass


class SourceType(Enum):
    """Type of data source."""

    LOCAL_FILE = "local_file"
    REMOTE_URL = "remote_url"


@dataclass
class URLSource:
    """Metadata about a fetched URL source.

    Attributes:
        original_url: The URL as provided by the user.
        resolved_url: The URL after normalisation (e.g., GitHub conversion).
        content_type: MIME type from response headers.
        etag: ETag header for cache validation.
        last_modified: Last-Modified header for cache validation.
        fetched_at: Timestamp when the data was fetched.
        size_bytes: Size of the fetched content.
        sha256: SHA256 hash of the content.
        terms_accepted: Whether the user accepted the terms.
        attribution: Attribution metadata for the source.
    """

    original_url: str
    resolved_url: str
    content_type: str = ""
    etag: str | None = None
    last_modified: str | None = None
    fetched_at: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0
    sha256: str = ""
    terms_accepted: bool = False
    attribution: Attribution | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation.

        Returns:
            Dictionary representation of URL source.
        """
        result: dict[str, Any] = {
            "source_type": "remote_url",
            "original_url": self.original_url,
            "resolved_url": self.resolved_url,
            "content_type": self.content_type,
            "fetched_at": self.fetched_at.isoformat(),
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "terms_accepted": self.terms_accepted,
        }

        if self.etag:
            result["etag"] = self.etag
        if self.last_modified:
            result["last_modified"] = self.last_modified
        if self.attribution:
            result["attribution"] = self.attribution.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "URLSource":
        """Create from dictionary.

        Args:
            data: Dictionary with URL source data.

        Returns:
            URLSource instance.
        """
        fetched_at = datetime.now()
        if "fetched_at" in data:
            if isinstance(data["fetched_at"], str):
                fetched_at = datetime.fromisoformat(data["fetched_at"])
            elif isinstance(data["fetched_at"], datetime):
                fetched_at = data["fetched_at"]

        attribution = None
        if "attribution" in data and data["attribution"]:
            attribution = Attribution.from_dict(data["attribution"])

        return cls(
            original_url=data.get("original_url", ""),
            resolved_url=data.get("resolved_url", ""),
            content_type=data.get("content_type", ""),
            etag=data.get("etag"),
            last_modified=data.get("last_modified"),
            fetched_at=fetched_at,
            size_bytes=data.get("size_bytes", 0),
            sha256=data.get("sha256", ""),
            terms_accepted=data.get("terms_accepted", False),
            attribution=attribution,
        )


@dataclass
class URLFetchResult:
    """Result of fetching a URL.

    Attributes:
        content: The fetched content as a string.
        source: Metadata about the source.
        from_cache: Whether the content was served from cache.
        cache_path: Path to the cached content file, if any.
    """

    content: str
    source: URLSource
    from_cache: bool = False
    cache_path: Path | None = None


class URLFetcher:
    """Fetches data from URLs with caching, rate limiting, and attribution.

    Features:
    - HTTPS-only by default (configurable)
    - GitHub URL auto-conversion to raw.githubusercontent.com
    - ETag-based conditional requests
    - Attribution metadata capture
    - User-Agent identification

    Example:
        >>> fetcher = URLFetcher()
        >>> result = fetcher.fetch(
        ...     "https://github.com/user/repo/blob/main/data.csv",
        ...     accept_terms=True
        ... )
        >>> print(result.content[:100])
    """

    # Default configuration
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_USER_AGENT = "Persona/1.0 (+https://github.com/REPPL/Persona)"

    # Security configuration
    ALLOWED_SCHEMES = {"https"}
    BLOCKED_HOSTS = {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "[::1]",
    }

    # Patterns for URL conversion
    GITHUB_BLOB_PATTERN = re.compile(
        r"^https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$"
    )
    GITHUB_RAW_PATTERN = re.compile(
        r"^https://github\.com/([^/]+)/([^/]+)/raw/([^/]+)/(.+)$"
    )
    GIST_PATTERN = re.compile(
        r"^https://gist\.github\.com/([^/]+)/([^/]+)/raw/(.+)$"
    )

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: str = DEFAULT_USER_AGENT,
        allow_http: bool = False,
    ) -> None:
        """Initialise the URL fetcher.

        Args:
            timeout: Request timeout in seconds.
            user_agent: User-Agent header for requests.
            allow_http: If True, allow HTTP URLs (insecure).
        """
        self.timeout = timeout
        self.user_agent = user_agent
        self.allow_http = allow_http

        if allow_http:
            self._allowed_schemes = {"http", "https"}
        else:
            self._allowed_schemes = self.ALLOWED_SCHEMES.copy()

    def is_url(self, path: str) -> bool:
        """Check if a path is a URL.

        Args:
            path: Path or URL string.

        Returns:
            True if the path is a URL.
        """
        return path.startswith(("http://", "https://"))

    def validate_url(self, url: str) -> None:
        """Validate a URL for security.

        Args:
            url: URL to validate.

        Raises:
            URLValidationError: If the URL fails validation.
        """
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in self._allowed_schemes:
            allowed = ", ".join(sorted(self._allowed_schemes))
            raise URLValidationError(
                f"URL scheme '{parsed.scheme}' not allowed. "
                f"Allowed schemes: {allowed}"
            )

        # Check host
        host = parsed.hostname or ""
        if host.lower() in self.BLOCKED_HOSTS:
            raise URLValidationError(
                f"Host '{host}' is blocked for security reasons."
            )

        # Check for IP addresses (potential SSRF)
        if self._is_ip_address(host):
            raise URLValidationError(
                f"IP addresses are not allowed: {host}. "
                "Please use a domain name."
            )

    def _is_ip_address(self, host: str) -> bool:
        """Check if a host is an IP address.

        Args:
            host: Hostname to check.

        Returns:
            True if the host appears to be an IP address.
        """
        # IPv4 pattern
        ipv4_pattern = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
        if ipv4_pattern.match(host):
            return True

        # IPv6 pattern (simplified)
        if ":" in host:
            return True

        return False

    def normalise_url(self, url: str) -> str:
        """Normalise a URL, converting GitHub URLs to raw format.

        Args:
            url: URL to normalise.

        Returns:
            Normalised URL.
        """
        # GitHub blob URLs
        match = self.GITHUB_BLOB_PATTERN.match(url)
        if match:
            user, repo, branch, path = match.groups()
            return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"

        # GitHub raw URLs (alternative format)
        match = self.GITHUB_RAW_PATTERN.match(url)
        if match:
            user, repo, branch, path = match.groups()
            return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"

        # Gist URLs
        match = self.GIST_PATTERN.match(url)
        if match:
            user, gist_id, path = match.groups()
            return f"https://gist.githubusercontent.com/{user}/{gist_id}/raw/{path}"

        return url

    def fetch(
        self,
        url: str,
        accept_terms: bool = False,
        etag: str | None = None,
        attribution: Attribution | None = None,
    ) -> URLFetchResult:
        """Fetch content from a URL.

        Args:
            url: URL to fetch.
            accept_terms: Whether the user accepts the source terms.
            etag: Optional ETag for conditional request.
            attribution: Optional attribution metadata.

        Returns:
            URLFetchResult with content and metadata.

        Raises:
            TermsNotAcceptedError: If terms not accepted.
            URLValidationError: If URL validation fails.
            httpx.HTTPError: If the request fails.
        """
        if not accept_terms:
            raise TermsNotAcceptedError(
                "Remote data sources require explicit terms acceptance. "
                "Use --accept-terms flag to acknowledge that you accept "
                "the source's terms of use."
            )

        # Validate and normalise URL
        self.validate_url(url)
        resolved_url = self.normalise_url(url)

        # Build headers
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "*/*",
        }
        if etag:
            headers["If-None-Match"] = etag

        # Make request
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(resolved_url, headers=headers, follow_redirects=True)

            # Handle 304 Not Modified
            if response.status_code == 304:
                # Content unchanged, caller should use cached version
                source = URLSource(
                    original_url=url,
                    resolved_url=resolved_url,
                    etag=etag,
                    fetched_at=datetime.now(),
                    terms_accepted=True,
                    attribution=attribution,
                )
                return URLFetchResult(
                    content="",
                    source=source,
                    from_cache=True,
                )

            response.raise_for_status()

            # Extract content
            content = response.text

            # Calculate hash
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            # Build source metadata
            source = URLSource(
                original_url=url,
                resolved_url=resolved_url,
                content_type=response.headers.get("content-type", ""),
                etag=response.headers.get("etag"),
                last_modified=response.headers.get("last-modified"),
                fetched_at=datetime.now(),
                size_bytes=len(content.encode("utf-8")),
                sha256=content_hash,
                terms_accepted=True,
                attribution=attribution,
            )

            return URLFetchResult(
                content=content,
                source=source,
                from_cache=False,
            )

    async def fetch_async(
        self,
        url: str,
        accept_terms: bool = False,
        etag: str | None = None,
        attribution: Attribution | None = None,
    ) -> URLFetchResult:
        """Fetch content from a URL asynchronously.

        Args:
            url: URL to fetch.
            accept_terms: Whether the user accepts the source terms.
            etag: Optional ETag for conditional request.
            attribution: Optional attribution metadata.

        Returns:
            URLFetchResult with content and metadata.

        Raises:
            TermsNotAcceptedError: If terms not accepted.
            URLValidationError: If URL validation fails.
            httpx.HTTPError: If the request fails.
        """
        if not accept_terms:
            raise TermsNotAcceptedError(
                "Remote data sources require explicit terms acceptance. "
                "Use --accept-terms flag to acknowledge that you accept "
                "the source's terms of use."
            )

        # Validate and normalise URL
        self.validate_url(url)
        resolved_url = self.normalise_url(url)

        # Build headers
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "*/*",
        }
        if etag:
            headers["If-None-Match"] = etag

        # Make request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                resolved_url, headers=headers, follow_redirects=True
            )

            # Handle 304 Not Modified
            if response.status_code == 304:
                source = URLSource(
                    original_url=url,
                    resolved_url=resolved_url,
                    etag=etag,
                    fetched_at=datetime.now(),
                    terms_accepted=True,
                    attribution=attribution,
                )
                return URLFetchResult(
                    content="",
                    source=source,
                    from_cache=True,
                )

            response.raise_for_status()

            # Extract content
            content = response.text

            # Calculate hash
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            # Build source metadata
            source = URLSource(
                original_url=url,
                resolved_url=resolved_url,
                content_type=response.headers.get("content-type", ""),
                etag=response.headers.get("etag"),
                last_modified=response.headers.get("last-modified"),
                fetched_at=datetime.now(),
                size_bytes=len(content.encode("utf-8")),
                sha256=content_hash,
                terms_accepted=True,
                attribution=attribution,
            )

            return URLFetchResult(
                content=content,
                source=source,
                from_cache=False,
            )

    def infer_format(self, url: str, content_type: str = "") -> str | None:
        """Infer the data format from URL or content type.

        Args:
            url: The URL.
            content_type: MIME type from response.

        Returns:
            File extension (without dot) or None if unknown.
        """
        # Try URL extension first
        parsed = urlparse(url)
        path = parsed.path.lower()

        extension_map = {
            ".csv": "csv",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "md",
            ".markdown": "md",
            ".txt": "txt",
            ".text": "txt",
            ".html": "html",
            ".htm": "html",
            ".org": "org",
        }

        for ext, fmt in extension_map.items():
            if path.endswith(ext):
                return fmt

        # Try content type
        content_type_map = {
            "text/csv": "csv",
            "application/json": "json",
            "text/json": "json",
            "text/yaml": "yaml",
            "application/x-yaml": "yaml",
            "text/markdown": "md",
            "text/plain": "txt",
            "text/html": "html",
        }

        # Extract base content type (ignore charset etc.)
        base_type = content_type.split(";")[0].strip().lower()
        return content_type_map.get(base_type)
