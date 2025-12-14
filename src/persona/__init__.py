"""
Persona - Generate realistic user personas from your data using AI.

This package provides tools for generating user personas from qualitative
research data such as interviews, surveys, and user feedback.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("persona")
except PackageNotFoundError:
    # Package not installed (e.g., running from source without pip install -e)
    __version__ = "0.0.0-dev"
