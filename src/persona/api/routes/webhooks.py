"""
Webhook endpoints.

This module provides webhook registration and management.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from persona.api.dependencies import ConfigDep, verify_token
from persona.api.models.requests import WebhookRegisterRequest
from persona.api.models.responses import SuccessResponse, WebhookResponse
from persona.api.services.webhook import WebhookManager

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


def get_webhook_manager(request: Request) -> WebhookManager:
    """Get webhook manager from app state."""
    return request.app.state.webhook_manager


@router.post("", response_model=WebhookResponse, dependencies=[Depends(verify_token)])
async def register_webhook(
    request: WebhookRegisterRequest,
    config: ConfigDep,
    manager: WebhookManager = Depends(get_webhook_manager),
) -> WebhookResponse:
    """
    Register a webhook for event notifications.

    Args:
        request: Webhook registration request.
        config: API configuration.
        manager: Webhook manager.

    Returns:
        WebhookResponse with webhook details.
    """
    webhook = manager.register(
        url=request.url,
        events=request.events,
        secret=request.secret,
    )

    return WebhookResponse(
        webhook_id=webhook.webhook_id,
        url=webhook.url,
        events=webhook.events,
        created_at=webhook.created_at,
    )


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    manager: WebhookManager = Depends(get_webhook_manager),
) -> WebhookResponse:
    """
    Get webhook details.

    Args:
        webhook_id: Webhook identifier.
        manager: Webhook manager.

    Returns:
        WebhookResponse with webhook details.

    Raises:
        HTTPException: If webhook not found.
    """
    webhook = manager.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook {webhook_id} not found",
        )

    return WebhookResponse(
        webhook_id=webhook.webhook_id,
        url=webhook.url,
        events=webhook.events,
        created_at=webhook.created_at,
    )


@router.delete("/{webhook_id}", response_model=SuccessResponse, dependencies=[Depends(verify_token)])
async def delete_webhook(
    webhook_id: str,
    manager: WebhookManager = Depends(get_webhook_manager),
) -> SuccessResponse:
    """
    Delete a webhook.

    Args:
        webhook_id: Webhook identifier.
        manager: Webhook manager.

    Returns:
        SuccessResponse confirming deletion.

    Raises:
        HTTPException: If webhook not found.
    """
    success = manager.unregister(webhook_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook {webhook_id} not found",
        )

    return SuccessResponse(
        success=True,
        message=f"Webhook {webhook_id} deleted successfully",
    )


@router.get("", response_model=list[WebhookResponse])
async def list_webhooks(
    manager: WebhookManager = Depends(get_webhook_manager),
) -> list[WebhookResponse]:
    """
    List all registered webhooks.

    Args:
        manager: Webhook manager.

    Returns:
        List of webhook details.
    """
    webhooks = manager.list_webhooks()
    return [
        WebhookResponse(
            webhook_id=webhook.webhook_id,
            url=webhook.url,
            events=webhook.events,
            created_at=webhook.created_at,
        )
        for webhook in webhooks
    ]
