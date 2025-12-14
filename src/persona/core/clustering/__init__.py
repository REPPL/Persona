"""
Persona clustering module.

This module provides functionality for clustering personas
to identify similar groups and suggest consolidation.
"""

from persona.core.clustering.cluster import (
    PersonaClusterer,
    Cluster,
    ClusterResult,
    ConsolidationSuggestion,
)

__all__ = [
    "PersonaClusterer",
    "Cluster",
    "ClusterResult",
    "ConsolidationSuggestion",
]
