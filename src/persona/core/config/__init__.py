"""
Configuration management module.

This module provides configuration loading, validation, and management
for custom vendors, models, workflows, and prompts.
"""

from persona.core.config.vendor import (
    VendorConfig,
    VendorLoader,
    AuthType,
)
from persona.core.config.model import (
    ModelConfig,
    ModelLoader,
    ModelPricing,
    ModelCapabilities,
    get_builtin_models,
    get_all_models,
)
from persona.core.config.template import (
    TemplateLoader,
    TemplateInfo,
    TemplateMetadata,
    get_builtin_templates,
)
from persona.core.config.workflow import (
    WorkflowConfig,
    WorkflowStep,
    WorkflowInfo,
    CustomWorkflowLoader,
    get_builtin_workflows,
)
from persona.core.config.validator import (
    ConfigValidator,
    ValidationResult,
    ValidationIssue,
    ValidationLevel,
    validate_config,
)
from persona.core.config.global_config import (
    GlobalConfig,
    ConfigManager,
    DefaultsConfig,
    BudgetConfig,
    OutputConfig,
    LoggingConfig,
    get_config,
    get_config_manager,
    get_global_config_path,
    get_project_config_path,
)

__all__ = [
    # Vendor configuration
    "VendorConfig",
    "VendorLoader",
    "AuthType",
    # Model configuration
    "ModelConfig",
    "ModelLoader",
    "ModelPricing",
    "ModelCapabilities",
    "get_builtin_models",
    "get_all_models",
    # Template configuration
    "TemplateLoader",
    "TemplateInfo",
    "TemplateMetadata",
    "get_builtin_templates",
    # Workflow configuration
    "WorkflowConfig",
    "WorkflowStep",
    "WorkflowInfo",
    "CustomWorkflowLoader",
    "get_builtin_workflows",
    # Configuration validation (F-055)
    "ConfigValidator",
    "ValidationResult",
    "ValidationIssue",
    "ValidationLevel",
    "validate_config",
    # Global configuration (F-085)
    "GlobalConfig",
    "ConfigManager",
    "DefaultsConfig",
    "BudgetConfig",
    "OutputConfig",
    "LoggingConfig",
    "get_config",
    "get_config_manager",
    "get_global_config_path",
    "get_project_config_path",
]
