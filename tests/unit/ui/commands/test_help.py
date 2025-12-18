"""
Tests for the help system (F-082).
"""

import pytest
from persona.ui.cli import app
from persona.ui.commands.help import (
    HELP_TOPICS,
    get_topic_content,
    get_topic_list,
    get_topic_title,
)
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


class TestHelpTopics:
    """Tests for help topic data."""

    def test_topics_exist(self):
        """Test that help topics are defined."""
        assert len(HELP_TOPICS) > 0

    def test_required_topics(self):
        """Test that all required topics exist."""
        required = [
            "quickstart",
            "configuration",
            "providers",
            "experiments",
            "generation",
            "output",
            "costs",
            "troubleshoot",
        ]
        for topic in required:
            assert topic in HELP_TOPICS, f"Missing required topic: {topic}"

    def test_topic_structure(self):
        """Test that each topic has title and content."""
        for name, topic in HELP_TOPICS.items():
            assert "title" in topic, f"Topic {name} missing title"
            assert "content" in topic, f"Topic {name} missing content"
            assert len(topic["title"]) > 0, f"Topic {name} has empty title"
            assert len(topic["content"]) > 0, f"Topic {name} has empty content"

    def test_get_topic_list(self):
        """Test getting list of topics."""
        topics = get_topic_list()
        assert len(topics) == len(HELP_TOPICS)
        for name, title in topics:
            assert name in HELP_TOPICS
            assert title == HELP_TOPICS[name]["title"]

    def test_get_topic_content(self):
        """Test getting topic content."""
        content = get_topic_content("quickstart")
        assert content is not None
        assert "Quickstart" in content

    def test_get_topic_content_not_found(self):
        """Test getting content for nonexistent topic."""
        content = get_topic_content("nonexistent")
        assert content is None

    def test_get_topic_title(self):
        """Test getting topic title."""
        title = get_topic_title("quickstart")
        assert title == "Getting Started with Persona"

    def test_get_topic_title_not_found(self):
        """Test getting title for nonexistent topic."""
        title = get_topic_title("nonexistent")
        assert title is None


class TestHelpCommand:
    """Tests for the help CLI command."""

    def test_help_no_args(self, runner):
        """Test help with no arguments shows overview."""
        result = runner.invoke(app, ["help"])
        assert result.exit_code == 0
        assert "Persona Help System" in result.output
        assert "Quick Commands" in result.output

    def test_help_topics_list(self, runner):
        """Test 'help topics' lists all topics."""
        result = runner.invoke(app, ["help", "topics"])
        assert result.exit_code == 0
        assert "Available Help Topics" in result.output
        assert "quickstart" in result.output
        assert "configuration" in result.output
        assert "providers" in result.output

    def test_help_specific_topic(self, runner):
        """Test help for specific topic."""
        result = runner.invoke(app, ["help", "quickstart"])
        assert result.exit_code == 0
        assert "Quickstart" in result.output
        assert "Installation" in result.output

    def test_help_providers(self, runner):
        """Test providers help topic."""
        result = runner.invoke(app, ["help", "providers"])
        assert result.exit_code == 0
        assert "Provider Setup" in result.output
        assert "Anthropic" in result.output
        assert "OpenAI" in result.output

    def test_help_configuration(self, runner):
        """Test configuration help topic."""
        result = runner.invoke(app, ["help", "configuration"])
        assert result.exit_code == 0
        assert "Configuration Guide" in result.output
        assert "Environment variables" in result.output

    def test_help_generation(self, runner):
        """Test generation help topic."""
        result = runner.invoke(app, ["help", "generation"])
        assert result.exit_code == 0
        assert "Generating Personas" in result.output
        assert "Complexity Levels" in result.output

    def test_help_costs(self, runner):
        """Test costs help topic."""
        result = runner.invoke(app, ["help", "costs"])
        assert result.exit_code == 0
        assert "Understanding Costs" in result.output
        assert "Budget Limits" in result.output

    def test_help_troubleshoot(self, runner):
        """Test troubleshoot help topic."""
        result = runner.invoke(app, ["help", "troubleshoot"])
        assert result.exit_code == 0
        assert "Troubleshooting" in result.output
        assert "No providers configured" in result.output

    def test_help_unknown_topic(self, runner):
        """Test help for unknown topic shows error."""
        result = runner.invoke(app, ["help", "nonexistent"])
        assert result.exit_code == 1
        assert "Unknown help topic" in result.output
        assert "Available topics" in result.output

    def test_help_case_insensitive(self, runner):
        """Test topic names are case insensitive."""
        result = runner.invoke(app, ["help", "QUICKSTART"])
        assert result.exit_code == 0
        assert "Quickstart" in result.output

    def test_help_experiments(self, runner):
        """Test experiments help topic."""
        result = runner.invoke(app, ["help", "experiments"])
        assert result.exit_code == 0
        assert "Experiment Management" in result.output

    def test_help_output(self, runner):
        """Test output help topic."""
        result = runner.invoke(app, ["help", "output"])
        assert result.exit_code == 0
        assert "Output Formats" in result.output
        assert "Verbosity Levels" in result.output


class TestMainHelpFlag:
    """Tests for --help flags on commands."""

    def test_main_help(self, runner):
        """Test persona --help shows commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "generate" in result.output
        assert "check" in result.output

    def test_generate_help(self, runner):
        """Test persona generate --help."""
        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert (
            "Generate personas" in result.output or "generate" in result.output.lower()
        )

    def test_check_help(self, runner):
        """Test persona check --help."""
        result = runner.invoke(app, ["check", "--help"])
        assert result.exit_code == 0
        assert "Check" in result.output or "check" in result.output.lower()

    def test_cost_help(self, runner):
        """Test persona cost --help."""
        result = runner.invoke(app, ["cost", "--help"])
        assert result.exit_code == 0
        assert "cost" in result.output.lower()

    def test_models_help(self, runner):
        """Test persona models --help."""
        result = runner.invoke(app, ["models", "--help"])
        assert result.exit_code == 0
        assert "models" in result.output.lower()

    def test_config_help(self, runner):
        """Test persona config --help."""
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "config" in result.output.lower()
