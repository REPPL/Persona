"""
Dynamic discovery module for vendors and models.

This module provides discovery of available vendors and models
through configuration scanning and API probing.
"""

from persona.core.discovery.vendor import (
    VendorDiscovery,
    VendorStatus,
    DiscoveryResult,
)
from persona.core.discovery.model import (
    ModelDiscovery,
    ModelStatus,
    ModelDiscoveryResult,
)
from persona.core.discovery.checker import (
    ModelChecker,
    ModelAvailability,
    ModelStatus as AvailabilityStatus,
    check_model,
    warn_if_deprecated,
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
]
