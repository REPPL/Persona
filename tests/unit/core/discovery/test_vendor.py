"""Tests for vendor discovery."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from persona.core.discovery.vendor import (
    DiscoveryResult,
    VendorDiscovery,
    VendorStatus,
)


class TestVendorStatus:
    """Tests for VendorStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert VendorStatus.AVAILABLE.value == "available"
        assert VendorStatus.UNAVAILABLE.value == "unavailable"
        assert VendorStatus.NOT_CONFIGURED.value == "not_configured"
        assert VendorStatus.ERROR.value == "error"


class TestDiscoveryResult:
    """Tests for DiscoveryResult dataclass."""

    def test_minimal_result(self):
        """Test minimal discovery result."""
        result = DiscoveryResult(
            vendor_id="test",
            status=VendorStatus.AVAILABLE,
            source="builtin",
        )
        assert result.vendor_id == "test"
        assert result.status == VendorStatus.AVAILABLE
        assert result.models == []

    def test_full_result(self):
        """Test full discovery result."""
        result = DiscoveryResult(
            vendor_id="ollama",
            status=VendorStatus.AVAILABLE,
            source="ollama",
            name="Ollama (Local)",
            message="Found 5 models",
            base_url="http://localhost:11434",
            response_time_ms=123.5,
            models=["llama2", "codellama", "mistral"],
        )
        assert result.name == "Ollama (Local)"
        assert len(result.models) == 3


class TestVendorDiscovery:
    """Tests for VendorDiscovery class."""

    def test_builtin_vendors_defined(self):
        """Test built-in vendors are defined."""
        assert "anthropic" in VendorDiscovery.BUILTIN_VENDORS
        assert "openai" in VendorDiscovery.BUILTIN_VENDORS
        assert "gemini" in VendorDiscovery.BUILTIN_VENDORS

    def test_init_default_dirs(self):
        """Test initialization with default directories."""
        discovery = VendorDiscovery()
        assert discovery._user_dir == Path.home() / ".persona" / "vendors"
        assert discovery._project_dir == Path(".persona") / "vendors"

    def test_init_custom_dirs(self):
        """Test initialization with custom directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "user"
            project_dir = Path(tmpdir) / "project"

            discovery = VendorDiscovery(
                user_dir=user_dir,
                project_dir=project_dir,
            )
            assert discovery._user_dir == user_dir
            assert discovery._project_dir == project_dir

    def test_discover_builtin_not_configured(self):
        """Test discovering built-in vendor without API key."""
        with patch.dict(os.environ, {}, clear=True):
            discovery = VendorDiscovery(cache_enabled=False)
            result = discovery.discover("anthropic")

            assert result.vendor_id == "anthropic"
            assert result.status == VendorStatus.NOT_CONFIGURED
            assert "ANTHROPIC_API_KEY" in result.message

    def test_discover_builtin_configured(self):
        """Test discovering built-in vendor with API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 401  # Auth error but reachable
                mock_client.return_value.__enter__.return_value.request.return_value = (
                    mock_response
                )

                discovery = VendorDiscovery(cache_enabled=False)
                result = discovery.discover("anthropic")

                assert result.vendor_id == "anthropic"
                assert result.status == VendorStatus.AVAILABLE
                assert result.response_time_ms is not None

    def test_discover_ollama_not_running(self):
        """Test discovering Ollama when not running."""
        import httpx

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.side_effect = (
                httpx.ConnectError("Connection refused")
            )

            discovery = VendorDiscovery(cache_enabled=False)
            result = discovery.discover_ollama()

            assert result.vendor_id == "ollama"
            assert result.status == VendorStatus.UNAVAILABLE
            assert "Not running" in result.message

    def test_discover_ollama_running(self):
        """Test discovering Ollama when running."""
        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "llama2"},
                    {"name": "codellama"},
                ],
            }
            mock_client.return_value.__enter__.return_value.get.return_value = (
                mock_response
            )

            discovery = VendorDiscovery(cache_enabled=False)
            result = discovery.discover_ollama()

            assert result.vendor_id == "ollama"
            assert result.status == VendorStatus.AVAILABLE
            assert len(result.models) == 2

    def test_discover_all(self):
        """Test discovering all vendors."""
        with patch.dict(os.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as tmpdir:
                discovery = VendorDiscovery(
                    user_dir=Path(tmpdir) / "user",
                    project_dir=Path(tmpdir) / "project",
                    cache_enabled=False,
                )

                # Mock ollama as not running
                import httpx

                with patch("httpx.Client") as mock_client:
                    mock_client.return_value.__enter__.return_value.get.side_effect = (
                        httpx.ConnectError("refused")
                    )

                    results = discovery.discover_all()

                    # Should have at least built-in vendors + ollama
                    assert len(results) >= 4
                    vendor_ids = [r.vendor_id for r in results]
                    assert "anthropic" in vendor_ids
                    assert "openai" in vendor_ids
                    assert "gemini" in vendor_ids

    def test_check_availability(self):
        """Test check_availability method."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 401
                mock_client.return_value.__enter__.return_value.request.return_value = (
                    mock_response
                )

                discovery = VendorDiscovery(cache_enabled=False)
                assert discovery.check_availability("anthropic") is True

    def test_get_available_vendors(self):
        """Test get_available_vendors method."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 401
                mock_client.return_value.__enter__.return_value.request.return_value = (
                    mock_response
                )
                mock_client.return_value.__enter__.return_value.get.side_effect = (
                    Exception("Not running")
                )

                discovery = VendorDiscovery(cache_enabled=False)
                available = discovery.get_available_vendors()

                assert "anthropic" in available

    def test_caching(self):
        """Test that results are cached."""
        with patch.dict(os.environ, {}, clear=True):
            discovery = VendorDiscovery(cache_enabled=True)

            # First call
            result1 = discovery.discover("anthropic")

            # Second call should return cached result
            result2 = discovery.discover("anthropic")

            assert result1.vendor_id == result2.vendor_id
            assert result1.status == result2.status

    def test_cache_bypass_with_force_refresh(self):
        """Test force refresh bypasses cache."""
        with patch.dict(os.environ, {}, clear=True):
            discovery = VendorDiscovery(cache_enabled=True)

            # First call
            discovery.discover("anthropic")

            # Force refresh should make a new discovery
            result = discovery.discover("anthropic", force_refresh=True)
            assert result.status == VendorStatus.NOT_CONFIGURED

    def test_clear_cache(self):
        """Test clearing the cache."""
        discovery = VendorDiscovery(cache_enabled=True)
        discovery._cache["test"] = (MagicMock(), 0)

        discovery.clear_cache()
        assert len(discovery._cache) == 0
