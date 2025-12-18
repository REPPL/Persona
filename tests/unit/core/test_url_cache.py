"""
Tests for URL caching functionality (F-091).
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from persona.core.data import Attribution, CacheEntry, URLCache, URLSource


class TestCacheEntry:
    """Tests for the CacheEntry dataclass."""

    def test_is_expired_no_expiry(self):
        """Test expired check when no expiry set."""
        entry = CacheEntry(
            url="https://example.com/data.csv",
            resolved_url="https://example.com/data.csv",
            content_path=Path("/tmp/content.csv"),
            metadata_path=Path("/tmp/metadata.json"),
        )
        assert entry.is_expired is True

    def test_is_expired_future(self, tmp_path: Path):
        """Test not expired when expiry is in future."""
        content_path = tmp_path / "content.csv"
        content_path.write_text("data")

        entry = CacheEntry(
            url="https://example.com/data.csv",
            resolved_url="https://example.com/data.csv",
            content_path=content_path,
            metadata_path=tmp_path / "metadata.json",
            expires_at=datetime.now() + timedelta(hours=1),
        )
        assert entry.is_expired is False

    def test_is_expired_past(self, tmp_path: Path):
        """Test expired when expiry is in past."""
        entry = CacheEntry(
            url="https://example.com/data.csv",
            resolved_url="https://example.com/data.csv",
            content_path=tmp_path / "content.csv",
            metadata_path=tmp_path / "metadata.json",
            expires_at=datetime.now() - timedelta(hours=1),
        )
        assert entry.is_expired is True

    def test_get_content(self, tmp_path: Path):
        """Test reading cached content."""
        content_path = tmp_path / "content.csv"
        content_path.write_text("col1,col2\n1,2")

        entry = CacheEntry(
            url="https://example.com/data.csv",
            resolved_url="https://example.com/data.csv",
            content_path=content_path,
            metadata_path=tmp_path / "metadata.json",
        )
        content = entry.get_content()

        assert content == "col1,col2\n1,2"


class TestURLCache:
    """Tests for the URLCache class."""

    def test_init_default(self, tmp_path: Path):
        """Test default initialisation."""
        cache = URLCache(cache_dir=tmp_path)
        assert cache.ttl == timedelta(hours=URLCache.DEFAULT_TTL_HOURS)

    def test_init_custom_ttl(self, tmp_path: Path):
        """Test custom TTL."""
        cache = URLCache(cache_dir=tmp_path, ttl_hours=48)
        assert cache.ttl == timedelta(hours=48)

    def test_put_get(self, tmp_path: Path):
        """Test storing and retrieving content."""
        cache = URLCache(cache_dir=tmp_path)
        url = "https://example.com/data.csv"

        source = URLSource(
            original_url=url,
            resolved_url=url,
            content_type="text/csv",
            etag='"abc123"',
            fetched_at=datetime.now(),
            size_bytes=14,
            sha256="e3b0c442",
            terms_accepted=True,
        )

        # Store content
        entry = cache.put(url, "col1,col2\n1,2", source)

        assert entry.url == url
        assert entry.etag == '"abc123"'
        assert entry.content_path.exists()

        # Retrieve content
        retrieved = cache.get(url)
        assert retrieved is not None
        assert retrieved.url == url
        assert retrieved.etag == '"abc123"'
        assert retrieved.get_content() == "col1,col2\n1,2"

    def test_get_missing(self, tmp_path: Path):
        """Test retrieving non-existent entry."""
        cache = URLCache(cache_dir=tmp_path)
        entry = cache.get("https://example.com/nonexistent.csv")
        assert entry is None

    def test_get_etag(self, tmp_path: Path):
        """Test retrieving ETag for cached URL."""
        cache = URLCache(cache_dir=tmp_path)
        url = "https://example.com/data.csv"

        source = URLSource(
            original_url=url,
            resolved_url=url,
            content_type="text/csv",
            etag='"abc123"',
            fetched_at=datetime.now(),
            size_bytes=14,
            sha256="e3b0c442",
            terms_accepted=True,
        )

        cache.put(url, "col1,col2\n1,2", source)

        etag = cache.get_etag(url)
        assert etag == '"abc123"'

    def test_get_etag_missing(self, tmp_path: Path):
        """Test ETag for non-existent entry."""
        cache = URLCache(cache_dir=tmp_path)
        etag = cache.get_etag("https://example.com/nonexistent.csv")
        assert etag is None

    def test_invalidate(self, tmp_path: Path):
        """Test invalidating a cache entry."""
        cache = URLCache(cache_dir=tmp_path)
        url = "https://example.com/data.csv"

        source = URLSource(
            original_url=url,
            resolved_url=url,
            content_type="text/csv",
            fetched_at=datetime.now(),
            size_bytes=14,
            sha256="e3b0c442",
            terms_accepted=True,
        )

        cache.put(url, "col1,col2\n1,2", source)

        # Verify it exists
        assert cache.get(url) is not None

        # Invalidate
        result = cache.invalidate(url)
        assert result is True

        # Verify it's gone
        assert cache.get(url) is None

    def test_invalidate_missing(self, tmp_path: Path):
        """Test invalidating non-existent entry."""
        cache = URLCache(cache_dir=tmp_path)
        result = cache.invalidate("https://example.com/nonexistent.csv")
        assert result is False

    def test_clear_expired(self, tmp_path: Path):
        """Test clearing expired entries."""
        cache = URLCache(cache_dir=tmp_path, ttl_hours=0)  # Immediate expiry

        url = "https://example.com/data.csv"
        source = URLSource(
            original_url=url,
            resolved_url=url,
            content_type="text/csv",
            fetched_at=datetime.now() - timedelta(hours=1),  # Old fetch
            size_bytes=14,
            sha256="e3b0c442",
            terms_accepted=True,
        )

        cache.put(url, "col1,col2\n1,2", source)

        # Entry should exist but be expired
        entry = cache.get(url)
        assert entry is not None

        # Clear expired
        count = cache.clear_expired()
        assert count == 1

        # Entry should be gone
        assert cache.get(url) is None

    def test_clear_all(self, tmp_path: Path):
        """Test clearing all entries."""
        cache = URLCache(cache_dir=tmp_path)

        # Add multiple entries
        for i in range(3):
            url = f"https://example.com/data{i}.csv"
            source = URLSource(
                original_url=url,
                resolved_url=url,
                content_type="text/csv",
                fetched_at=datetime.now(),
                size_bytes=14,
                sha256="e3b0c442",
                terms_accepted=True,
            )
            cache.put(url, f"data{i}", source)

        # Clear all
        count = cache.clear_all()
        assert count == 3

        # All should be gone
        for i in range(3):
            assert cache.get(f"https://example.com/data{i}.csv") is None

    def test_list_entries(self, tmp_path: Path):
        """Test listing all cache entries."""
        cache = URLCache(cache_dir=tmp_path)

        # Add multiple entries
        urls = []
        for i in range(3):
            url = f"https://example.com/data{i}.csv"
            urls.append(url)
            source = URLSource(
                original_url=url,
                resolved_url=url,
                content_type="text/csv",
                fetched_at=datetime.now(),
                size_bytes=14,
                sha256="e3b0c442",
                terms_accepted=True,
            )
            cache.put(url, f"data{i}", source)

        entries = cache.list_entries()
        assert len(entries) == 3

        entry_urls = {e.url for e in entries}
        for url in urls:
            assert url in entry_urls

    def test_get_total_size(self, tmp_path: Path):
        """Test calculating total cache size."""
        cache = URLCache(cache_dir=tmp_path)

        # Add entries with known sizes
        for i in range(3):
            url = f"https://example.com/data{i}.csv"
            content = "x" * (100 * (i + 1))  # 100, 200, 300 bytes
            source = URLSource(
                original_url=url,
                resolved_url=url,
                content_type="text/csv",
                fetched_at=datetime.now(),
                size_bytes=len(content),
                sha256="e3b0c442",
                terms_accepted=True,
            )
            cache.put(url, content, source)

        total = cache.get_total_size()
        assert total == 600  # 100 + 200 + 300

    def test_infer_extension_csv(self, tmp_path: Path):
        """Test extension inference for CSV."""
        cache = URLCache(cache_dir=tmp_path)
        ext = cache._infer_extension("https://example.com/data.csv", "")
        assert ext == "csv"

    def test_infer_extension_json(self, tmp_path: Path):
        """Test extension inference for JSON."""
        cache = URLCache(cache_dir=tmp_path)
        ext = cache._infer_extension("https://example.com/data.json", "")
        assert ext == "json"

    def test_infer_extension_from_content_type(self, tmp_path: Path):
        """Test extension inference from content type."""
        cache = URLCache(cache_dir=tmp_path)
        ext = cache._infer_extension("https://example.com/data", "text/csv")
        assert ext == "csv"

    def test_put_with_attribution(self, tmp_path: Path):
        """Test storing content with attribution."""
        cache = URLCache(cache_dir=tmp_path)
        url = "https://example.com/data.csv"

        attr = Attribution(
            title="Test Dataset",
            creators=["Test Org"],
            licence="CC-BY-4.0",
        )

        source = URLSource(
            original_url=url,
            resolved_url=url,
            content_type="text/csv",
            fetched_at=datetime.now(),
            size_bytes=14,
            sha256="e3b0c442",
            terms_accepted=True,
            attribution=attr,
        )

        cache.put(url, "col1,col2\n1,2", source)

        # Check metadata file contains attribution
        import json

        entry = cache.get(url)
        assert entry is not None

        metadata = json.loads(entry.metadata_path.read_text())
        assert "attribution" in metadata
        assert metadata["attribution"]["title"] == "Test Dataset"

    def test_different_urls_different_cache_keys(self, tmp_path: Path):
        """Test that different URLs get different cache keys."""
        cache = URLCache(cache_dir=tmp_path)

        url1 = "https://example.com/data1.csv"
        url2 = "https://example.com/data2.csv"

        key1 = cache._get_cache_key(url1)
        key2 = cache._get_cache_key(url2)

        assert key1 != key2

    def test_same_url_same_cache_key(self, tmp_path: Path):
        """Test that same URL always gets same cache key."""
        cache = URLCache(cache_dir=tmp_path)

        url = "https://example.com/data.csv"
        key1 = cache._get_cache_key(url)
        key2 = cache._get_cache_key(url)

        assert key1 == key2
