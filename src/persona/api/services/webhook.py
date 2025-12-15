"""
Webhook delivery service.

This module handles webhook delivery with retry logic and signature verification.
"""

import asyncio
import hashlib
import hmac
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

import httpx

from persona.api.config import APIConfig
from persona.core.async_utils import retry_async

logger = logging.getLogger(__name__)


class Webhook:
    """
    Webhook configuration and state.
    """

    def __init__(
        self,
        webhook_id: str,
        url: str,
        events: list[str],
        secret: Optional[str] = None,
    ):
        """
        Initialise webhook.

        Args:
            webhook_id: Unique webhook identifier.
            url: Webhook URL.
            events: Events to subscribe to.
            secret: Secret for HMAC signature.
        """
        self.webhook_id = webhook_id
        self.url = url
        self.events = events
        self.secret = secret
        self.created_at = datetime.now()

    def matches_event(self, event: str) -> bool:
        """Check if webhook is subscribed to event."""
        return event in self.events


class WebhookManager:
    """
    Manages webhook registration and delivery.

    Handles webhook lifecycle including registration, delivery,
    retries, and signature generation.
    """

    def __init__(self, config: APIConfig):
        """
        Initialise webhook manager.

        Args:
            config: API configuration.
        """
        self.config = config
        self.webhooks: dict[str, Webhook] = {}

    def register(
        self,
        url: str,
        events: list[str],
        secret: Optional[str] = None,
    ) -> Webhook:
        """
        Register a new webhook.

        Args:
            url: Webhook URL.
            events: Events to subscribe to.
            secret: Optional secret for HMAC signature.

        Returns:
            Registered webhook.
        """
        webhook_id = f"webhook-{uuid.uuid4().hex[:12]}"
        webhook = Webhook(webhook_id, url, events, secret)
        self.webhooks[webhook_id] = webhook

        logger.info(f"Registered webhook {webhook_id} for {url}")
        return webhook

    def unregister(self, webhook_id: str) -> bool:
        """
        Unregister a webhook.

        Args:
            webhook_id: Webhook identifier.

        Returns:
            True if webhook was removed.
        """
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            logger.info(f"Unregistered webhook {webhook_id}")
            return True
        return False

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID."""
        return self.webhooks.get(webhook_id)

    def list_webhooks(self) -> list[Webhook]:
        """List all registered webhooks."""
        return list(self.webhooks.values())

    def _generate_signature(self, payload: bytes, secret: str) -> str:
        """
        Generate HMAC-SHA256 signature for payload.

        Args:
            payload: Payload bytes.
            secret: Secret key.

        Returns:
            Signature as hex string.
        """
        return hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

    async def deliver(
        self,
        event: str,
        data: dict[str, Any],
        webhook_url: Optional[str] = None,
    ) -> None:
        """
        Deliver webhook event to all matching webhooks.

        Args:
            event: Event name (e.g., "generation.completed").
            data: Event data.
            webhook_url: Optional specific webhook URL (overrides registered webhooks).
        """
        # Prepare payload
        payload = {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        # Determine target webhooks
        if webhook_url:
            # Specific webhook URL provided
            await self._deliver_to_url(webhook_url, payload, secret=None)
        else:
            # Deliver to all matching registered webhooks
            matching_webhooks = [
                webhook
                for webhook in self.webhooks.values()
                if webhook.matches_event(event)
            ]

            if not matching_webhooks:
                logger.debug(f"No webhooks registered for event: {event}")
                return

            # Deliver to all matching webhooks concurrently
            tasks = [
                self._deliver_to_url(webhook.url, payload, webhook.secret)
                for webhook in matching_webhooks
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _deliver_to_url(
        self,
        url: str,
        payload: dict[str, Any],
        secret: Optional[str],
    ) -> None:
        """
        Deliver webhook to specific URL with retry.

        Args:
            url: Webhook URL.
            payload: Event payload.
            secret: Optional secret for signature.
        """
        # Serialise payload
        import json

        payload_json = json.dumps(payload)
        payload_bytes = payload_json.encode("utf-8")

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Persona-Webhook/1.0",
        }

        # Add signature if secret provided
        if secret:
            signature = self._generate_signature(payload_bytes, secret)
            headers["X-Persona-Signature"] = f"sha256={signature}"

        # Delivery function with retry
        async def deliver_with_retry() -> None:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    content=payload_bytes,
                    headers=headers,
                    timeout=self.config.webhook_timeout,
                )
                response.raise_for_status()

        # Attempt delivery with retry
        try:
            await retry_async(
                deliver_with_retry,
                max_retries=self.config.webhook_max_retries,
                base_delay=self.config.webhook_retry_delay,
                exponential=True,
                exceptions=(httpx.HTTPError,),
            )
            logger.info(f"Successfully delivered webhook to {url}")
        except Exception as e:
            logger.error(f"Failed to deliver webhook to {url} after retries: {e}")

    async def notify_generation_started(
        self,
        job_id: str,
        webhook_url: Optional[str] = None,
    ) -> None:
        """
        Notify generation started.

        Args:
            job_id: Generation job ID.
            webhook_url: Optional specific webhook URL.
        """
        await self.deliver(
            "generation.started",
            {"job_id": job_id},
            webhook_url=webhook_url,
        )

    async def notify_generation_progress(
        self,
        job_id: str,
        progress: int,
        webhook_url: Optional[str] = None,
    ) -> None:
        """
        Notify generation progress.

        Args:
            job_id: Generation job ID.
            progress: Progress percentage.
            webhook_url: Optional specific webhook URL.
        """
        await self.deliver(
            "generation.progress",
            {"job_id": job_id, "progress": progress},
            webhook_url=webhook_url,
        )

    async def notify_generation_completed(
        self,
        job_id: str,
        result: dict[str, Any],
        webhook_url: Optional[str] = None,
    ) -> None:
        """
        Notify generation completed.

        Args:
            job_id: Generation job ID.
            result: Generation result.
            webhook_url: Optional specific webhook URL.
        """
        await self.deliver(
            "generation.completed",
            {"job_id": job_id, "result": result},
            webhook_url=webhook_url,
        )

    async def notify_generation_failed(
        self,
        job_id: str,
        error: str,
        webhook_url: Optional[str] = None,
    ) -> None:
        """
        Notify generation failed.

        Args:
            job_id: Generation job ID.
            error: Error message.
            webhook_url: Optional specific webhook URL.
        """
        await self.deliver(
            "generation.failed",
            {"job_id": job_id, "error": error},
            webhook_url=webhook_url,
        )
