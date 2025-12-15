"""
Tests for webhook manager.
"""

import pytest

from persona.api.config import APIConfig
from persona.api.services.webhook import Webhook, WebhookManager


@pytest.fixture
def webhook_manager():
    """Create webhook manager fixture."""
    config = APIConfig(
        webhook_timeout=10,
        webhook_max_retries=2,
        webhook_retry_delay=0.1,
    )
    return WebhookManager(config)


def test_register_webhook(webhook_manager):
    """Test webhook registration."""
    webhook = webhook_manager.register(
        url="https://example.com/webhook",
        events=["generation.completed"],
        secret="test-secret",
    )

    assert webhook.url == "https://example.com/webhook"
    assert webhook.events == ["generation.completed"]
    assert webhook.secret == "test-secret"
    assert webhook.webhook_id.startswith("webhook-")
    assert webhook.created_at is not None


def test_unregister_webhook(webhook_manager):
    """Test webhook unregistration."""
    webhook = webhook_manager.register(
        url="https://example.com/webhook",
        events=["generation.completed"],
    )

    # Successful unregister
    assert webhook_manager.unregister(webhook.webhook_id) is True

    # Webhook no longer exists
    assert webhook_manager.get_webhook(webhook.webhook_id) is None

    # Cannot unregister again
    assert webhook_manager.unregister(webhook.webhook_id) is False


def test_get_webhook(webhook_manager):
    """Test retrieving webhook by ID."""
    webhook = webhook_manager.register(
        url="https://example.com/webhook",
        events=["generation.completed"],
    )

    # Get existing webhook
    retrieved = webhook_manager.get_webhook(webhook.webhook_id)
    assert retrieved is not None
    assert retrieved.webhook_id == webhook.webhook_id

    # Get non-existent webhook
    assert webhook_manager.get_webhook("nonexistent") is None


def test_list_webhooks(webhook_manager):
    """Test listing all webhooks."""
    # Empty list initially
    assert len(webhook_manager.list_webhooks()) == 0

    # Register webhooks
    webhook1 = webhook_manager.register(
        url="https://example.com/webhook1",
        events=["generation.completed"],
    )
    webhook2 = webhook_manager.register(
        url="https://example.com/webhook2",
        events=["generation.failed"],
    )

    # List all webhooks
    webhooks = webhook_manager.list_webhooks()
    assert len(webhooks) == 2
    webhook_ids = [w.webhook_id for w in webhooks]
    assert webhook1.webhook_id in webhook_ids
    assert webhook2.webhook_id in webhook_ids


def test_webhook_matches_event():
    """Test event matching for webhooks."""
    webhook = Webhook(
        webhook_id="test",
        url="https://example.com/webhook",
        events=["generation.completed", "generation.failed"],
    )

    # Matching events
    assert webhook.matches_event("generation.completed") is True
    assert webhook.matches_event("generation.failed") is True

    # Non-matching event
    assert webhook.matches_event("generation.started") is False


def test_generate_signature(webhook_manager):
    """Test HMAC signature generation."""
    payload = b'{"event": "test"}'
    secret = "test-secret"

    signature1 = webhook_manager._generate_signature(payload, secret)
    signature2 = webhook_manager._generate_signature(payload, secret)

    # Same payload and secret should generate same signature
    assert signature1 == signature2

    # Different secret should generate different signature
    signature3 = webhook_manager._generate_signature(payload, "different-secret")
    assert signature1 != signature3


@pytest.mark.asyncio
async def test_deliver_to_registered_webhooks(webhook_manager, httpx_mock):
    """Test delivering events to registered webhooks."""
    # Register webhook
    webhook_manager.register(
        url="https://example.com/webhook",
        events=["generation.completed"],
    )

    # Mock HTTP response
    httpx_mock.add_response(
        url="https://example.com/webhook",
        method="POST",
        status_code=200,
    )

    # Deliver event
    await webhook_manager.deliver(
        event="generation.completed",
        data={"job_id": "test-job"},
    )

    # Verify request was made
    assert len(httpx_mock.get_requests()) == 1
    request = httpx_mock.get_requests()[0]
    assert request.url == "https://example.com/webhook"
