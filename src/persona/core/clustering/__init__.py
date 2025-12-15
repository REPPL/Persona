"""
Persona clustering module.

This module provides functionality for clustering personas
to identify similar groups and suggest consolidation.
"""

from persona.core.clustering.cluster import (
    PersonaClusterer,
    Cluster,
    ClusterMethod,
    ClusterResult,
    ConsolidationSuggestion,
)

__all__ = [
    "PersonaClusterer",
    "Cluster",
    "ClusterMethod",
    "ClusterResult",
    "ConsolidationSuggestion",
]
