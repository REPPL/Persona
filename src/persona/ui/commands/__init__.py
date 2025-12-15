"""
CLI command modules for Persona.

This package contains subcommand implementations.
"""

from persona.ui.commands.generate import generate_app
from persona.ui.commands.experiment import experiment_app
from persona.ui.commands.vendor import vendor_app
from persona.ui.commands.model import model_app
from persona.ui.commands.template import template_app
from persona.ui.commands.workflow import workflow_app
from persona.ui.commands.preview import preview_app
from persona.ui.commands.validate import validate_app
from persona.ui.commands.compare import compare_app
from persona.ui.commands.export import export_app
from persona.ui.commands.cluster import cluster_app
from persona.ui.commands.refine import refine_app
from persona.ui.commands.config import config_app
from persona.ui.commands.help import help_app
from persona.ui.commands.quality import quality_app
from persona.ui.commands.plugin import plugin_app
from persona.ui.commands.script import script_app
from persona.ui.commands.dashboard import dashboard_app

__all__ = [
    "generate_app",
    "experiment_app",
    "vendor_app",
    "model_app",
    "template_app",
    "workflow_app",
    "preview_app",
    "validate_app",
    "compare_app",
    "export_app",
    "cluster_app",
    "refine_app",
    "config_app",
    "help_app",
    "quality_app",
    "plugin_app",
    "script_app",
    "dashboard_app",
]
