"""
Dynamic discovery module for vendors and models.

This module provides discovery of available vendors and models
through configuration scanning and API probing.
"""

from persona.core.discovery.checker import (
    ModelAvailability,
    ModelChecker,
    check_model,
    warn_if_deprecated,
)
from persona.core.discovery.checker import (
    ModelStatus as AvailabilityStatus,
)
from persona.core.discovery.model import (
    ModelDiscovery,
    ModelDiscoveryResult,
    ModelStatus,
)
from persona.core.discovery.vendor import (
    DiscoveryResult,
    VendorDiscovery,
    VendorStatus,
)
from persona.core.discovery.ollama_models import (
    ModelComparisonResult,
    ModelTestStatus,
    OllamaModelRegistry,
    OllamaTestedModel,
    compare_ollama_models,
    get_untested_models,
)

__all__ = [
    # Vendor discovery
    "VendorDiscovery",
    "VendorStatus",
    "DiscoveryResult",
    # Model discovery
    "ModelDiscovery",
    "ModelStatus",
    "ModelDiscoveryResult",
    # Model availability checking (F-056)
    "ModelChecker",
    "ModelAvailability",
    "AvailabilityStatus",
    "check_model",
    "warn_if_deprecated",
    # Ollama model comparison
    "OllamaModelRegistry",
    "ModelComparisonResult",
    "ModelTestStatus",
    "OllamaTestedModel",
    "compare_ollama_models",
    "get_untested_models",
]
