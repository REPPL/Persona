"""
Persona REST API.

This module provides a FastAPI-based REST API for programmatic access
to Persona's functionality via HTTP.
"""

from persona.api.app import create_app

__all__ = ["create_app"]
