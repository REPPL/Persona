"""
Tests for URL data fetching functionality (F-091).
"""

from datetime import datetime

import pytest

from persona.core.data import (
    Attribution,
    SourceType,
    TermsNotAcceptedError,
    URLFetcher,
    URLFetchResult,
    URLSource,
    URLValidationError,
)


class TestAttribution:
    """Tests for the Attribution dataclass."""

    def test_init_minimal(self):
        """Test Attribution with minimal fields."""
        attr = Attribution(title="Test Dataset")
        assert attr.title == "Test Dataset"
        assert attr.creators == []
        assert attr.source_url == ""

    def test_init_full(self):
        """Test Attribution with all fields."""
        attr = Attribution(
            title="Test Dataset",
            creators=["Org A", "Org B"],
            source_url="https://example.com/data",
            licence="CC-BY-4.0",
            access_date=datetime(2025, 3, 15),
            authors=["Alice", "Bob"],
            doi="10.1234/test",
            version="1.0",
            notify_email="data@example.com",
            requirements=["Credit creators", "Share alike"],
        )
        assert attr.title == "Test Dataset"
        assert len(attr.creators) == 2
        assert attr.notify_email == "data@example.com"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        attr = Attribution(
            title="Test",
            creators=["Org"],
            licence="CC-BY-4.0",
            access_date=datetime(2025, 3, 15),
        )
        d = attr.to_dict()

        assert d["title"] == "Test"
        assert d["creators"] == ["Org"]
        assert d["licence"] == "CC-BY-4.0"
        assert "access_date" in d

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "title": "Test Dataset",
            "creators": ["Org"],
            "source_url": "https://example.com",
            "licence": "CC-BY-4.0",
            "access_date": "2025-03-15T00:00:00",
        }
        attr = Attribution.from_dict(data)

        assert attr.title == "Test Dataset"
        assert attr.licence == "CC-BY-4.0"
        assert attr.access_date is not None
        assert attr.access_date.year == 2025

    def test_to_markdown(self):
        """Test markdown generation."""
        attr = Attribution(
            title="Test Dataset",
            creators=["Org A", "Org B"],
            source_url="https://example.com",
            licence="CC-BY-4.0",
            access_date=datetime(2025, 3, 15),
        )
        md = attr.to_markdown()

        assert "## Test Dataset" in md
        assert "Org A, Org B" in md
        assert "CC-BY-4.0" in md

    def test_get_citation(self):
        """Test citation generation."""
        attr = Attribution(
            title="Test Dataset",
            creators=["Org A"],
            access_date=datetime(2025, 3, 15),
            source_url="https://example.com",
        )
        citation = attr.get_citation()

        assert "Org A" in citation
        assert "Test Dataset" in citation
        assert "2025" in citation


class TestURLSource:
    """Tests for the URLSource dataclass."""

    def test_init(self):
        """Test URLSource initialisation."""
        source = URLSource(
            original_url="https://github.com/user/repo/blob/main/data.csv",
            resolved_url="https://raw.githubusercontent.com/user/repo/main/data.csv",
            content_type="text/csv",
            etag='"abc123"',
            fetched_at=datetime.now(),
            size_bytes=1024,
            sha256="e3b0c44298fc1c149afbf4c8996fb924",
            terms_accepted=True,
        )

        assert source.original_url.startswith("https://github.com")
        assert source.resolved_url.startswith("https://raw.githubusercontent.com")
        assert source.terms_accepted is True

    def test_to_dict(self):
        """Test conversion to dictionary."""
        source = URLSource(
            original_url="https://example.com/data.csv",
            resolved_url="https://example.com/data.csv",
            content_type="text/csv",
            etag='"abc"',
            size_bytes=100,
            sha256="abc123",
            terms_accepted=True,
        )
        d = source.to_dict()

        assert d["source_type"] == "remote_url"
        assert d["original_url"] == "https://example.com/data.csv"
        assert d["etag"] == '"abc"'

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "original_url": "https://example.com/data.csv",
            "resolved_url": "https://example.com/data.csv",
            "content_type": "text/csv",
            "fetched_at": "2025-03-15T10:00:00",
            "size_bytes": 100,
            "sha256": "abc123",
            "terms_accepted": True,
        }
        source = URLSource.from_dict(data)

        assert source.original_url == "https://example.com/data.csv"
        assert source.fetched_at.year == 2025

    def test_with_attribution(self):
        """Test URLSource with attribution."""
        attr = Attribution(title="Test", creators=["Org"])
        source = URLSource(
            original_url="https://example.com/data.csv",
            resolved_url="https://example.com/data.csv",
            terms_accepted=True,
            attribution=attr,
        )
        d = source.to_dict()

        assert "attribution" in d
        assert d["attribution"]["title"] == "Test"


class TestURLFetcher:
    """Tests for the URLFetcher class."""

    def test_init_default(self):
        """Test default initialisation."""
        fetcher = URLFetcher()
        assert fetcher.timeout == URLFetcher.DEFAULT_TIMEOUT
        assert fetcher.allow_http is False

    def test_init_custom(self):
        """Test custom initialisation."""
        fetcher = URLFetcher(timeout=60.0, allow_http=True)
        assert fetcher.timeout == 60.0
        assert fetcher.allow_http is True

    def test_is_url(self):
        """Test URL detection."""
        fetcher = URLFetcher()

        assert fetcher.is_url("https://example.com/data.csv") is True
        assert fetcher.is_url("http://example.com/data.csv") is True
        assert fetcher.is_url("/local/path/data.csv") is False
        assert fetcher.is_url("data.csv") is False
        assert fetcher.is_url("file:///data.csv") is False

    def test_validate_url_https(self):
        """Test HTTPS URL validation."""
        fetcher = URLFetcher()

        # Valid HTTPS should pass
        fetcher.validate_url("https://example.com/data.csv")

    def test_validate_url_http_blocked(self):
        """Test HTTP URL blocked by default."""
        fetcher = URLFetcher()

        with pytest.raises(URLValidationError, match="scheme.*not allowed"):
            fetcher.validate_url("http://example.com/data.csv")

    def test_validate_url_http_allowed(self):
        """Test HTTP allowed when enabled."""
        fetcher = URLFetcher(allow_http=True)

        # Should not raise
        fetcher.validate_url("http://example.com/data.csv")

    def test_validate_url_localhost_blocked(self):
        """Test localhost blocked."""
        fetcher = URLFetcher()

        with pytest.raises(URLValidationError, match="blocked"):
            fetcher.validate_url("https://localhost/data.csv")

    def test_validate_url_ip_blocked(self):
        """Test IP addresses blocked."""
        fetcher = URLFetcher()

        with pytest.raises(URLValidationError, match="IP addresses"):
            fetcher.validate_url("https://192.168.1.1/data.csv")

    def test_normalise_url_github_blob(self):
        """Test GitHub blob URL conversion."""
        fetcher = URLFetcher()

        url = "https://github.com/user/repo/blob/main/data/file.csv"
        normalised = fetcher.normalise_url(url)

        assert normalised == "https://raw.githubusercontent.com/user/repo/main/data/file.csv"

    def test_normalise_url_github_raw(self):
        """Test GitHub raw URL conversion."""
        fetcher = URLFetcher()

        url = "https://github.com/user/repo/raw/main/data/file.csv"
        normalised = fetcher.normalise_url(url)

        assert normalised == "https://raw.githubusercontent.com/user/repo/main/data/file.csv"

    def test_normalise_url_already_raw(self):
        """Test already raw URL unchanged."""
        fetcher = URLFetcher()

        url = "https://raw.githubusercontent.com/user/repo/main/file.csv"
        normalised = fetcher.normalise_url(url)

        assert normalised == url

    def test_normalise_url_non_github(self):
        """Test non-GitHub URL unchanged."""
        fetcher = URLFetcher()

        url = "https://example.com/data.csv"
        normalised = fetcher.normalise_url(url)

        assert normalised == url

    def test_fetch_requires_terms(self):
        """Test that fetch requires terms acceptance."""
        fetcher = URLFetcher()

        with pytest.raises(TermsNotAcceptedError, match="terms acceptance"):
            fetcher.fetch("https://example.com/data.csv", accept_terms=False)

    def test_infer_format_from_url(self):
        """Test format inference from URL extension."""
        fetcher = URLFetcher()

        assert fetcher.infer_format("https://example.com/data.csv") == "csv"
        assert fetcher.infer_format("https://example.com/data.json") == "json"
        assert fetcher.infer_format("https://example.com/data.yaml") == "yaml"
        assert fetcher.infer_format("https://example.com/data.yml") == "yaml"
        assert fetcher.infer_format("https://example.com/data.md") == "md"

    def test_infer_format_from_content_type(self):
        """Test format inference from content type."""
        fetcher = URLFetcher()

        assert fetcher.infer_format("https://example.com/data", "text/csv") == "csv"
        assert fetcher.infer_format("https://example.com/data", "application/json") == "json"
        assert fetcher.infer_format("https://example.com/data", "text/html") == "html"

    def test_infer_format_url_takes_precedence(self):
        """Test URL extension takes precedence over content type."""
        fetcher = URLFetcher()

        # URL says CSV, content-type says JSON - URL wins
        result = fetcher.infer_format("https://example.com/data.csv", "application/json")
        assert result == "csv"


class TestSourceType:
    """Tests for the SourceType enum."""

    def test_values(self):
        """Test enum values."""
        assert SourceType.LOCAL_FILE.value == "local_file"
        assert SourceType.REMOTE_URL.value == "remote_url"


class TestURLFetchResult:
    """Tests for the URLFetchResult dataclass."""

    def test_init(self):
        """Test URLFetchResult initialisation."""
        source = URLSource(
            original_url="https://example.com/data.csv",
            resolved_url="https://example.com/data.csv",
            terms_accepted=True,
        )
        result = URLFetchResult(
            content="col1,col2\n1,2",
            source=source,
            from_cache=False,
        )

        assert result.content == "col1,col2\n1,2"
        assert result.from_cache is False
        assert result.cache_path is None
