"""
Metric registry for extensible quality metrics.

This module provides a plugin architecture for quality metrics,
enabling registration of custom metrics and discovery via entry points.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from persona.core.quality.base import MetricCategory, QualityMetric
from persona.core.quality.config import QualityConfig


@dataclass
class MetricInfo:
    """Metadata about a registered quality metric."""

    name: str
    description: str
    metric_class: type[QualityMetric]
    category: str = MetricCategory.STRUCTURAL
    requires_source_data: bool = False
    requires_other_personas: bool = False
    requires_evidence_report: bool = False
    is_builtin: bool = True


class MetricRegistry:
    """
    Registry for quality metrics.

    Provides plugin architecture for discovering and instantiating metrics.

    Example:
        registry = MetricRegistry()
        registry.register(
            name="custom",
            metric_class=CustomMetric,
            description="Custom quality metric",
            category=MetricCategory.SEMANTIC,
        )

        metric = registry.get("custom")
        score = metric.evaluate(persona)
    """

    def __init__(self, register_builtins: bool = True) -> None:
        """
        Initialise the metric registry.

        Args:
            register_builtins: Whether to register built-in metrics.
        """
        self._metrics: dict[str, MetricInfo] = {}
        if register_builtins:
            self._register_builtins()

    def _register_builtins(self) -> None:
        """Register built-in quality metrics."""
        # Defer imports to avoid circular dependency
        from persona.core.quality.metrics.completeness import CompletenessMetric
        from persona.core.quality.metrics.consistency import ConsistencyMetric
        from persona.core.quality.metrics.distinctiveness import DistinctivenessMetric
        from persona.core.quality.metrics.evidence import EvidenceStrengthMetric
        from persona.core.quality.metrics.realism import RealismMetric

        self.register(
            name="completeness",
            metric_class=CompletenessMetric,
            description="Evaluate field population and content depth",
            category=MetricCategory.STRUCTURAL,
            requires_source_data=False,
            requires_other_personas=False,
            requires_evidence_report=False,
        )
        self.register(
            name="consistency",
            metric_class=ConsistencyMetric,
            description="Evaluate internal logical coherence",
            category=MetricCategory.STRUCTURAL,
            requires_source_data=False,
            requires_other_personas=False,
            requires_evidence_report=False,
        )
        self.register(
            name="evidence_strength",
            metric_class=EvidenceStrengthMetric,
            description="Evaluate link to source data",
            category=MetricCategory.EVIDENTIAL,
            requires_source_data=False,
            requires_other_personas=False,
            requires_evidence_report=True,
        )
        self.register(
            name="distinctiveness",
            metric_class=DistinctivenessMetric,
            description="Evaluate uniqueness compared to other personas",
            category=MetricCategory.COMPARATIVE,
            requires_source_data=False,
            requires_other_personas=True,
            requires_evidence_report=False,
        )
        self.register(
            name="realism",
            metric_class=RealismMetric,
            description="Evaluate plausibility as a real person",
            category=MetricCategory.SEMANTIC,
            requires_source_data=False,
            requires_other_personas=False,
            requires_evidence_report=False,
        )

    def register(
        self,
        name: str,
        metric_class: type[QualityMetric],
        description: str,
        category: str = MetricCategory.STRUCTURAL,
        requires_source_data: bool = False,
        requires_other_personas: bool = False,
        requires_evidence_report: bool = False,
        is_builtin: bool = False,
    ) -> None:
        """
        Register a quality metric.

        Args:
            name: Unique name for the metric.
            metric_class: The metric class (must inherit from QualityMetric).
            description: Human-readable description.
            category: Metric category for organisation.
            requires_source_data: Whether metric needs source data.
            requires_other_personas: Whether metric needs other personas.
            requires_evidence_report: Whether metric needs evidence report.
            is_builtin: Whether this is a built-in metric.

        Raises:
            ValueError: If name is already registered.
            TypeError: If metric_class doesn't inherit from QualityMetric.
        """
        if name in self._metrics:
            raise ValueError(f"Metric '{name}' is already registered")

        if not issubclass(metric_class, QualityMetric):
            raise TypeError(
                f"Metric class must inherit from QualityMetric, "
                f"got {metric_class.__name__}"
            )

        self._metrics[name] = MetricInfo(
            name=name,
            description=description,
            metric_class=metric_class,
            category=category,
            requires_source_data=requires_source_data,
            requires_other_personas=requires_other_personas,
            requires_evidence_report=requires_evidence_report,
            is_builtin=is_builtin,
        )

    def unregister(self, name: str) -> None:
        """
        Unregister a quality metric.

        Args:
            name: Name of the metric to remove.

        Raises:
            KeyError: If metric not found.
        """
        if name not in self._metrics:
            raise KeyError(f"Metric '{name}' not found")
        del self._metrics[name]

    def get(
        self,
        name: str,
        config: QualityConfig | None = None,
        **kwargs: Any,
    ) -> QualityMetric:
        """
        Get an instance of a metric.

        Args:
            name: Name of the metric.
            config: Optional quality configuration.
            **kwargs: Additional arguments passed to metric constructor.

        Returns:
            QualityMetric instance.

        Raises:
            KeyError: If metric not found.
        """
        if name not in self._metrics:
            raise KeyError(f"Metric '{name}' not found. Available: {self.list_names()}")

        info = self._metrics[name]
        return info.metric_class(config=config, **kwargs)

    def get_info(self, name: str) -> MetricInfo:
        """
        Get metadata about a metric.

        Args:
            name: Name of the metric.

        Returns:
            MetricInfo with metric metadata.

        Raises:
            KeyError: If metric not found.
        """
        if name not in self._metrics:
            raise KeyError(f"Metric '{name}' not found")
        return self._metrics[name]

    def list_names(self) -> list[str]:
        """
        List all registered metric names.

        Returns:
            List of metric names.
        """
        return sorted(self._metrics.keys())

    def list_all(self) -> list[MetricInfo]:
        """
        List all registered metrics with metadata.

        Returns:
            List of MetricInfo objects.
        """
        return [self._metrics[name] for name in self.list_names()]

    def list_by_category(self, category: str) -> list[MetricInfo]:
        """
        List metrics in a specific category.

        Args:
            category: Category to filter by.

        Returns:
            List of MetricInfo objects in that category.
        """
        return [info for info in self._metrics.values() if info.category == category]

    def has(self, name: str) -> bool:
        """
        Check if a metric is registered.

        Args:
            name: Name to check.

        Returns:
            True if registered.
        """
        return name in self._metrics

    def get_all_metrics(
        self,
        config: QualityConfig | None = None,
        **kwargs: Any,
    ) -> dict[str, QualityMetric]:
        """
        Get instances of all registered metrics.

        Args:
            config: Optional quality configuration for all metrics.
            **kwargs: Additional arguments passed to metric constructors.

        Returns:
            Dictionary mapping metric names to instances.

        Example:
            registry = MetricRegistry()
            metrics = registry.get_all_metrics(config)

            for name, metric in metrics.items():
                score = metric.evaluate(persona)
        """
        return {name: self.get(name, config, **kwargs) for name in self.list_names()}

    def get_builtin_metrics(
        self,
        config: QualityConfig | None = None,
        **kwargs: Any,
    ) -> dict[str, QualityMetric]:
        """
        Get instances of all built-in metrics.

        Args:
            config: Optional quality configuration for all metrics.
            **kwargs: Additional arguments passed to metric constructors.

        Returns:
            Dictionary mapping metric names to instances.
        """
        return {
            name: self.get(name, config, **kwargs)
            for name in self.get_builtin_names()
        }

    def get_builtin_names(self) -> list[str]:
        """
        Get names of built-in metrics.

        Returns:
            List of built-in metric names.
        """
        return [name for name, info in self._metrics.items() if info.is_builtin]

    def get_academic_names(self) -> list[str]:
        """
        Get names of academic metrics.

        Returns:
            List of academic metric names.
        """
        return [
            name
            for name, info in self._metrics.items()
            if info.category == MetricCategory.ACADEMIC
        ]

    def get_compliance_names(self) -> list[str]:
        """
        Get names of compliance metrics.

        Returns:
            List of compliance metric names.
        """
        return [
            name
            for name, info in self._metrics.items()
            if info.category == MetricCategory.COMPLIANCE
        ]


# Global registry instance
_global_registry: MetricRegistry | None = None


def get_registry() -> MetricRegistry:
    """
    Get the global metric registry.

    Returns:
        The global MetricRegistry instance.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = MetricRegistry()
    return _global_registry


def register_metric(
    name: str,
    description: str = "",
    category: str = MetricCategory.STRUCTURAL,
    requires_source_data: bool = False,
    requires_other_personas: bool = False,
    requires_evidence_report: bool = False,
) -> Callable[[type[QualityMetric]], type[QualityMetric]]:
    """
    Decorator to register a metric class.

    Example:
        @register_metric(
            name="custom",
            description="Custom quality metric",
            category=MetricCategory.SEMANTIC,
        )
        class CustomMetric(QualityMetric):
            ...

    Args:
        name: Unique name for the metric.
        description: Human-readable description.
        category: Metric category for organisation.
        requires_source_data: Whether metric needs source data.
        requires_other_personas: Whether metric needs other personas.
        requires_evidence_report: Whether metric needs evidence report.

    Returns:
        Decorator function.
    """

    def decorator(cls: type[QualityMetric]) -> type[QualityMetric]:
        registry = get_registry()
        registry.register(
            name=name,
            metric_class=cls,
            description=description or f"{cls.__name__} metric",
            category=category,
            requires_source_data=requires_source_data,
            requires_other_personas=requires_other_personas,
            requires_evidence_report=requires_evidence_report,
            is_builtin=False,
        )
        return cls

    return decorator
