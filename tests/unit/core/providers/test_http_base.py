"""
Tests for HTTP base provider with connection pooling (F-129).
"""

import pytest

from persona.core.providers.http_base import HTTPProvider


class ConcreteHTTPProvider(HTTPProvider):
    """Concrete implementation for testing."""

    @property
    def name(self) -> str:
        return "test"

    @property
    def default_model(self) -> str:
        return "test-model"

    @property
    def available_models(self) -> list[str]:
        return ["test-model"]

    def generate(self, prompt, **kwargs):
        pass

    def is_configured(self) -> bool:
        return True


class TestHTTPProviderInit:
    """Tests for HTTPProvider initialisation."""

    def test_default_timeout(self):
        """Test default timeout value."""
        provider = ConcreteHTTPProvider()
        assert provider._timeout == HTTPProvider.DEFAULT_TIMEOUT

    def test_custom_timeout(self):
        """Test custom timeout value."""
        provider = ConcreteHTTPProvider(timeout=60.0)
        assert provider._timeout == 60.0

    def test_default_max_connections(self):
        """Test default max connections."""
        provider = ConcreteHTTPProvider()
        assert provider._max_connections == HTTPProvider.DEFAULT_MAX_CONNECTIONS

    def test_custom_max_connections(self):
        """Test custom max connections."""
        provider = ConcreteHTTPProvider(max_connections=20)
        assert provider._max_connections == 20

    def test_default_max_keepalive(self):
        """Test default max keepalive connections."""
        provider = ConcreteHTTPProvider()
        assert provider._max_keepalive == HTTPProvider.DEFAULT_MAX_KEEPALIVE

    def test_custom_max_keepalive(self):
        """Test custom max keepalive connections."""
        provider = ConcreteHTTPProvider(max_keepalive_connections=10)
        assert provider._max_keepalive == 10


class TestHTTPProviderSyncClient:
    """Tests for synchronous client management."""

    def setup_method(self):
        """Reset class-level clients before each test."""
        HTTPProvider.cleanup_sync()
        HTTPProvider._sync_client = None

    def teardown_method(self):
        """Cleanup after each test."""
        HTTPProvider.cleanup_sync()

    def test_get_sync_client_creates_client(self):
        """Test that get_sync_client creates a client."""
        provider = ConcreteHTTPProvider()
        client = provider.get_sync_client()

        assert client is not None
        assert not client.is_closed

    def test_get_sync_client_reuses_client(self):
        """Test that get_sync_client reuses existing client."""
        provider1 = ConcreteHTTPProvider()
        provider2 = ConcreteHTTPProvider()

        client1 = provider1.get_sync_client()
        client2 = provider2.get_sync_client()

        assert client1 is client2

    def test_cleanup_sync_closes_client(self):
        """Test that cleanup_sync closes the client."""
        provider = ConcreteHTTPProvider()
        client = provider.get_sync_client()

        HTTPProvider.cleanup_sync()

        assert HTTPProvider._sync_client is None


class TestHTTPProviderAsyncClient:
    """Tests for asynchronous client management."""

    def setup_method(self):
        """Reset class-level clients before each test."""
        HTTPProvider._async_client = None
        HTTPProvider._lock = None

    @pytest.mark.asyncio
    async def test_get_async_client_creates_client(self):
        """Test that get_async_client creates a client."""
        provider = ConcreteHTTPProvider()
        client = await provider.get_async_client()

        assert client is not None
        assert not client.is_closed

        await HTTPProvider.cleanup_async()

    @pytest.mark.asyncio
    async def test_get_async_client_reuses_client(self):
        """Test that get_async_client reuses existing client."""
        provider1 = ConcreteHTTPProvider()
        provider2 = ConcreteHTTPProvider()

        client1 = await provider1.get_async_client()
        client2 = await provider2.get_async_client()

        assert client1 is client2

        await HTTPProvider.cleanup_async()

    @pytest.mark.asyncio
    async def test_cleanup_async_closes_client(self):
        """Test that cleanup_async closes the client."""
        provider = ConcreteHTTPProvider()
        await provider.get_async_client()

        await HTTPProvider.cleanup_async()

        assert HTTPProvider._async_client is None


class TestHTTPProviderTimeout:
    """Tests for timeout configuration."""

    def test_get_timeout_default(self):
        """Test default timeout configuration."""
        timeout = HTTPProvider._get_timeout()

        assert timeout.read == HTTPProvider.DEFAULT_TIMEOUT
        assert timeout.connect == 10.0

    def test_get_timeout_custom(self):
        """Test custom timeout configuration."""
        timeout = HTTPProvider._get_timeout(60.0)

        assert timeout.read == 60.0


class TestHTTPProviderLimits:
    """Tests for connection limits configuration."""

    def test_get_limits_default(self):
        """Test default limits configuration."""
        limits = HTTPProvider._get_limits()

        assert limits.max_connections == HTTPProvider.DEFAULT_MAX_CONNECTIONS
        assert limits.max_keepalive_connections == HTTPProvider.DEFAULT_MAX_KEEPALIVE

    def test_get_limits_custom(self):
        """Test custom limits configuration."""
        limits = HTTPProvider._get_limits(max_connections=20, max_keepalive=10)

        assert limits.max_connections == 20
        assert limits.max_keepalive_connections == 10


class TestHTTPProviderCleanup:
    """Tests for cleanup methods."""

    def setup_method(self):
        """Reset clients before each test."""
        HTTPProvider._sync_client = None
        HTTPProvider._async_client = None
        HTTPProvider._lock = None

    @pytest.mark.asyncio
    async def test_cleanup_closes_all_clients(self):
        """Test that cleanup closes both sync and async clients."""
        provider = ConcreteHTTPProvider()

        # Create both clients
        provider.get_sync_client()
        await provider.get_async_client()

        # Cleanup both
        await HTTPProvider.cleanup()

        assert HTTPProvider._sync_client is None
        assert HTTPProvider._async_client is None
