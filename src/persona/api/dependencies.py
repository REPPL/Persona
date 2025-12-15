"""
Dependency injection for FastAPI.

This module provides dependencies for routes including configuration,
authentication, and service instances.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from persona.api.config import APIConfig
from persona.sdk import PersonaClient

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


@lru_cache
def get_config() -> APIConfig:
    """
    Get API configuration (cached).

    Returns:
        APIConfig instance.
    """
    return APIConfig.from_env()


def get_client() -> PersonaClient:
    """
    Get PersonaClient instance.

    Returns:
        PersonaClient for generating personas.
    """
    return PersonaClient.from_environment()


async def verify_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(security)],
    config: Annotated[APIConfig, Depends(get_config)],
) -> None:
    """
    Verify API authentication token.

    Args:
        credentials: HTTP bearer token credentials.
        config: API configuration.

    Raises:
        HTTPException: If authentication fails.
    """
    if not config.is_auth_required():
        return

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not config.validate_token(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Type aliases for common dependencies
ConfigDep = Annotated[APIConfig, Depends(get_config)]
ClientDep = Annotated[PersonaClient, Depends(get_client)]
AuthDep = Annotated[None, Depends(verify_token)]
