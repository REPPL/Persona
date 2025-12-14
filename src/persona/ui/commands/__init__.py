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

__all__ = [
    "generate_app",
    "experiment_app",
    "vendor_app",
    "model_app",
    "template_app",
    "workflow_app",
]
