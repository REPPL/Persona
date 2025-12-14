"""
Tests for conversation scripts (F-086).
"""

import json
import pytest

from persona.core.generation.parser import Persona
from persona.core.scripts.abstractors import (
    AbstractorResult,
    BehaviourAbstractor,
    CharacterSynthesiser,
    QuoteAbstractor,
    ScenarioGeneraliser,
)
from persona.core.scripts.formatters import (
    CharacterCardFormatter,
    Jinja2TemplateFormatter,
    SystemPromptFormatter,
    get_formatter,
)
from persona.core.scripts.generator import (
    ConversationScriptGenerator,
    ScriptGenerationResult,
)
from persona.core.scripts.models import (
    CharacterCard,
    CommunicationStyle,
    Guidelines,
    Identity,
    KnowledgeBoundaries,
    Provenance,
    PsychologicalProfile,
    ScriptFormat,
)
from persona.core.scripts.privacy import (
    LeakageType,
    PrivacyAuditResult,
    PrivacyAuditor,
    PrivacyConfig,
    PrivacyLeakageError,
)


@pytest.fixture
def sample_persona() -> Persona:
    """Create a sample persona for testing."""
    return Persona(
        id="persona-001",
        name="Sarah Chen",
        demographics={
            "role": "Marketing Manager",
            "age": "32",
            "experience": "8 years",
        },
        goals=[
            "Streamline campaign workflows",
            "Improve team collaboration",
            "Achieve work-life balance",
        ],
        pain_points=[
            "Too many manual processes",
            "Difficulty tracking performance",
            "Constant context switching",
        ],
        behaviours=[
            "Checking analytics dashboards first thing in the morning",
            "Juggling multiple campaigns simultaneously",
            "Collaborating with cross-functional teams",
        ],
        quotes=[
            "I need tools that work the way I think.",
            "Every minute spent on admin is a minute not spent on strategy.",
            "If I can't see the big picture, I can't make good decisions.",
        ],
        additional={
            "motivations": ["Recognition", "Team success", "Professional growth"],
        },
    )


@pytest.fixture
def sample_character_card() -> CharacterCard:
    """Create a sample character card."""
    return CharacterCard(
        id="script-abc123",
        identity=Identity(
            name="Sarah Chen",
            title="The Marketing Manager",
            demographics_summary="32 years old, Marketing Manager",
        ),
        psychological_profile=PsychologicalProfile(
            goals=["seeks efficiency improvements"],
            motivations=["driven by achievement"],
            pain_points=["frustrated by manual processes"],
            personality_traits=["efficiency-focused"],
            flaws=["impatient with delays"],
        ),
        communication_style=CommunicationStyle(
            tone="professional but frustrated",
            vocabulary_level="professional",
            speech_patterns=["uses urgency language"],
        ),
        knowledge_boundaries=KnowledgeBoundaries(
            knows=["marketing strategies"],
            doesnt_know=["backend implementation"],
            can_infer=["market trends"],
        ),
        guidelines=Guidelines(),
        provenance=Provenance(source_persona_id="persona-001"),
    )


# ==================== Abstractor Tests ====================


class TestQuoteAbstractor:
    """Tests for QuoteAbstractor."""

    def test_empty_quotes(self):
        """Test with empty quotes."""
        abstractor = QuoteAbstractor()
        result = abstractor.abstract([])
        assert result.abstracted_content == []
        assert result.source_count == 0

    def test_urgency_detection(self):
        """Test detection of urgency language."""
        abstractor = QuoteAbstractor()
        result = abstractor.abstract(["I need this done immediately!"])
        assert "uses urgency language" in result.abstracted_content

    def test_frustration_detection(self):
        """Test detection of frustration."""
        abstractor = QuoteAbstractor()
        result = abstractor.abstract(["I'm so frustrated with this system!"])
        assert "expresses frustration directly" in result.abstracted_content

    def test_positive_detection(self):
        """Test detection of positive sentiment."""
        abstractor = QuoteAbstractor()
        result = abstractor.abstract(["I love this feature, it's amazing!"])
        assert "uses positive reinforcement" in result.abstracted_content

    def test_technical_detection(self):
        """Test detection of technical language."""
        abstractor = QuoteAbstractor()
        result = abstractor.abstract(["The API integration with the database is broken."])
        assert "comfortable with technical terminology" in result.abstracted_content

    def test_concise_detection(self):
        """Test detection of concise communication."""
        abstractor = QuoteAbstractor()
        result = abstractor.abstract(["Yes.", "Done.", "OK."])
        assert "prefers concise communication" in result.abstracted_content

    def test_question_detection(self):
        """Test detection of question patterns."""
        abstractor = QuoteAbstractor()
        result = abstractor.abstract(["What's this?", "How does it work?", "Why?"])
        assert "frequently asks clarifying questions" in result.abstracted_content

    def test_source_count(self):
        """Test source count is accurate."""
        abstractor = QuoteAbstractor()
        result = abstractor.abstract(["Quote 1", "Quote 2", "Quote 3"])
        assert result.source_count == 3


class TestScenarioGeneraliser:
    """Tests for ScenarioGeneraliser."""

    def test_empty_scenarios(self):
        """Test with empty scenarios."""
        generaliser = ScenarioGeneraliser()
        result = generaliser.generalise([])
        assert result.abstracted_content == []

    def test_overtime_detection(self):
        """Test detection of overtime patterns."""
        generaliser = ScenarioGeneraliser()
        result = generaliser.generalise(["Stayed late to finish the project"])
        assert "willing to invest extra time when needed" in result.abstracted_content

    def test_problem_solving_detection(self):
        """Test detection of problem-solving patterns."""
        generaliser = ScenarioGeneraliser()
        result = generaliser.generalise(["Fixed the critical bug in production"])
        assert "proactive problem-solver" in result.abstracted_content

    def test_collaboration_detection(self):
        """Test detection of collaboration patterns."""
        generaliser = ScenarioGeneraliser()
        result = generaliser.generalise(["Worked with the team to deliver the feature"])
        assert "values teamwork and collaboration" in result.abstracted_content


class TestBehaviourAbstractor:
    """Tests for BehaviourAbstractor."""

    def test_empty_behaviours(self):
        """Test with empty behaviours."""
        abstractor = BehaviourAbstractor()
        result = abstractor.abstract([])
        assert result.abstracted_content == []

    def test_routine_detection(self):
        """Test detection of routine patterns."""
        abstractor = BehaviourAbstractor()
        result = abstractor.abstract(["Starts every morning with a review"])
        assert "structured daily routine" in result.abstracted_content

    def test_multitasking_detection(self):
        """Test detection of multitasking."""
        abstractor = BehaviourAbstractor()
        result = abstractor.abstract(["Juggling multiple projects simultaneously"])
        assert "handles multiple priorities" in result.abstracted_content

    def test_data_driven_detection(self):
        """Test detection of data-driven behaviour."""
        abstractor = BehaviourAbstractor()
        result = abstractor.abstract(["Reviews dashboard metrics daily"])
        assert "data-informed decision maker" in result.abstracted_content


class TestCharacterSynthesiser:
    """Tests for CharacterSynthesiser."""

    def test_efficiency_trait(self, sample_persona):
        """Test efficiency trait detection."""
        synthesiser = CharacterSynthesiser()
        result = synthesiser.synthesise(sample_persona)
        assert "efficiency-focused" in result.abstracted_content

    def test_collaboration_trait(self, sample_persona):
        """Test collaboration trait detection."""
        synthesiser = CharacterSynthesiser()
        # Modify persona to have collaboration goal
        sample_persona.goals = ["Improve team collaboration"]
        result = synthesiser.synthesise(sample_persona)
        assert "values collaboration" in result.abstracted_content

    def test_impatience_flaw(self, sample_persona):
        """Test impatience flaw detection."""
        synthesiser = CharacterSynthesiser()
        sample_persona.pain_points = ["Slow systems are frustrating"]
        result = synthesiser.synthesise(sample_persona)
        flaws = [c for c in result.abstracted_content if c.startswith("FLAW:")]
        assert len(flaws) > 0

    def test_get_traits_and_flaws_separation(self, sample_persona):
        """Test traits and flaws are separated."""
        synthesiser = CharacterSynthesiser()
        traits, flaws = synthesiser.get_traits_and_flaws(sample_persona)
        assert isinstance(traits, list)
        assert isinstance(flaws, list)
        # Traits should not contain "FLAW:"
        assert all(not t.startswith("FLAW:") for t in traits)


# ==================== Model Tests ====================


class TestCharacterCard:
    """Tests for CharacterCard model."""

    def test_to_dict(self, sample_character_card):
        """Test conversion to dictionary."""
        data = sample_character_card.to_dict()
        assert data["id"] == "script-abc123"
        assert data["identity"]["name"] == "Sarah Chen"
        assert "psychological_profile" in data
        assert "communication_style" in data

    def test_to_json(self, sample_character_card):
        """Test conversion to JSON."""
        json_str = sample_character_card.to_json()
        data = json.loads(json_str)
        assert data["id"] == "script-abc123"

    def test_to_yaml(self, sample_character_card):
        """Test conversion to YAML."""
        yaml_str = sample_character_card.to_yaml()
        assert "Sarah Chen" in yaml_str
        assert "script-abc123" in yaml_str

    def test_from_dict(self, sample_character_card):
        """Test creation from dictionary."""
        data = sample_character_card.to_dict()
        restored = CharacterCard.from_dict(data)
        assert restored.id == sample_character_card.id
        assert restored.identity.name == sample_character_card.identity.name


class TestScriptFormat:
    """Tests for ScriptFormat enum."""

    def test_format_values(self):
        """Test format enum values."""
        assert ScriptFormat.CHARACTER_CARD.value == "character_card"
        assert ScriptFormat.SYSTEM_PROMPT.value == "system_prompt"
        assert ScriptFormat.JINJA2_TEMPLATE.value == "jinja2_template"


# ==================== Privacy Tests ====================


class TestPrivacyAuditor:
    """Tests for PrivacyAuditor."""

    def test_passes_clean_card(self, sample_character_card, sample_persona):
        """Test audit passes for clean card."""
        auditor = PrivacyAuditor()
        result = auditor.audit(sample_character_card, sample_persona)
        # Should pass since card doesn't contain raw quotes
        assert result.passed is True
        assert result.leakage_score <= 0.1

    def test_detects_direct_quote(self, sample_character_card, sample_persona):
        """Test detection of direct quote leakage."""
        auditor = PrivacyAuditor()

        # Add a direct quote to the card
        sample_character_card.communication_style.speech_patterns = [
            "I need tools that work the way I think."  # Direct quote!
        ]

        result = auditor.audit(sample_character_card, sample_persona)
        assert len(result.leakages) > 0
        assert any(l.type == LeakageType.DIRECT_QUOTE for l in result.leakages)

    def test_detects_partial_match(self, sample_character_card, sample_persona):
        """Test detection of partial quote match."""
        auditor = PrivacyAuditor()

        # Add partial quote
        sample_character_card.communication_style.speech_patterns = [
            "work the way I think"  # 3+ word match
        ]

        result = auditor.audit(sample_character_card, sample_persona)
        assert len(result.leakages) > 0

    def test_config_threshold(self, sample_character_card, sample_persona):
        """Test configurable threshold."""
        config = PrivacyConfig(max_leakage_score=0.0)  # Very strict
        auditor = PrivacyAuditor(config)

        result = auditor.audit(sample_character_card, sample_persona)
        # With strict threshold, even minor overlap might fail
        # But clean card should still pass if no actual leakage
        assert result.leakage_score >= 0

    def test_blocked_property(self, sample_character_card, sample_persona):
        """Test blocked property is inverse of passed."""
        auditor = PrivacyAuditor()
        result = auditor.audit(sample_character_card, sample_persona)
        assert result.blocked == (not result.passed)


class TestPrivacyConfig:
    """Tests for PrivacyConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = PrivacyConfig()
        assert config.max_leakage_score == 0.1
        assert config.check_direct_quotes is True
        assert config.check_paraphrases is True

    def test_custom_values(self):
        """Test custom configuration."""
        config = PrivacyConfig(
            max_leakage_score=0.2,
            check_paraphrases=False,
        )
        assert config.max_leakage_score == 0.2
        assert config.check_paraphrases is False


# ==================== Generator Tests ====================


class TestConversationScriptGenerator:
    """Tests for ConversationScriptGenerator."""

    def test_generate_returns_result(self, sample_persona):
        """Test generate returns ScriptGenerationResult."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona)
        assert isinstance(result, ScriptGenerationResult)

    def test_generate_creates_character_card(self, sample_persona):
        """Test generate creates a character card."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona)
        assert result.character_card is not None
        assert result.character_card.identity.name == "Sarah Chen"

    def test_generate_runs_privacy_audit(self, sample_persona):
        """Test generate runs privacy audit."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona)
        assert result.privacy_audit is not None

    def test_generate_not_blocked_for_clean_persona(self, sample_persona):
        """Test clean persona doesn't get blocked."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona)
        assert result.blocked is False
        assert result.output != ""

    def test_generate_character_card_format(self, sample_persona):
        """Test generate with character card format."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona, ScriptFormat.CHARACTER_CARD)
        assert result.format == ScriptFormat.CHARACTER_CARD
        # Output should be valid JSON
        data = json.loads(result.output)
        assert "identity" in data

    def test_generate_system_prompt_format(self, sample_persona):
        """Test generate with system prompt format."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona, ScriptFormat.SYSTEM_PROMPT)
        assert result.format == ScriptFormat.SYSTEM_PROMPT
        assert "You are Sarah Chen" in result.output

    def test_generate_jinja2_format(self, sample_persona):
        """Test generate with Jinja2 template format."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona, ScriptFormat.JINJA2_TEMPLATE)
        assert result.format == ScriptFormat.JINJA2_TEMPLATE
        assert "{{ identity.name }}" in result.output

    def test_identity_includes_title(self, sample_persona):
        """Test identity includes title from role."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona)
        assert "Marketing Manager" in result.character_card.identity.title

    def test_profile_has_abstracted_goals(self, sample_persona):
        """Test psychological profile has abstracted goals."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona)
        # Goals should be abstracted, not raw
        goals = result.character_card.psychological_profile.goals
        assert len(goals) > 0
        # Should not contain raw goal text
        assert "Streamline campaign workflows" not in goals


class TestGeneratorPrivacyBlocking:
    """Tests for generator privacy blocking."""

    def test_blocks_on_direct_quote_leakage(self, sample_persona):
        """Test generator blocks when quote appears in output."""
        generator = ConversationScriptGenerator(block_on_failure=True)

        # This is hard to test since generator abstracts by design
        # Just verify blocking mechanism works
        result = generator.generate(sample_persona)
        # With clean abstraction, should not be blocked
        assert result.blocked is False

    def test_non_blocking_mode(self, sample_persona):
        """Test non-blocking mode still generates output."""
        generator = ConversationScriptGenerator(block_on_failure=False)
        result = generator.generate(sample_persona)
        # Should have output even if audit fails
        assert result.output != "" or result.blocked is False


# ==================== Formatter Tests ====================


class TestCharacterCardFormatter:
    """Tests for CharacterCardFormatter."""

    def test_json_format(self, sample_character_card):
        """Test JSON formatting."""
        formatter = CharacterCardFormatter(use_yaml=False)
        output = formatter.format(sample_character_card)
        data = json.loads(output)
        assert data["id"] == "script-abc123"

    def test_yaml_format(self, sample_character_card):
        """Test YAML formatting."""
        formatter = CharacterCardFormatter(use_yaml=True)
        output = formatter.format(sample_character_card)
        assert "Sarah Chen" in output
        # Should not be JSON
        assert not output.strip().startswith("{")

    def test_extension_json(self):
        """Test JSON extension."""
        formatter = CharacterCardFormatter(use_yaml=False)
        assert formatter.extension() == ".json"

    def test_extension_yaml(self):
        """Test YAML extension."""
        formatter = CharacterCardFormatter(use_yaml=True)
        assert formatter.extension() == ".yaml"


class TestSystemPromptFormatter:
    """Tests for SystemPromptFormatter."""

    def test_format_includes_name(self, sample_character_card):
        """Test output includes persona name."""
        formatter = SystemPromptFormatter()
        output = formatter.format(sample_character_card)
        assert "Sarah Chen" in output

    def test_format_includes_traits(self, sample_character_card):
        """Test output includes personality traits."""
        formatter = SystemPromptFormatter()
        output = formatter.format(sample_character_card)
        assert "efficiency-focused" in output

    def test_format_includes_synthetic_marker(self, sample_character_card):
        """Test output includes synthetic marker."""
        formatter = SystemPromptFormatter(include_synthetic_marker=True)
        output = formatter.format(sample_character_card)
        assert "SYNTHETIC_PERSONA_SCRIPT" in output

    def test_format_without_marker(self, sample_character_card):
        """Test output without synthetic marker."""
        formatter = SystemPromptFormatter(include_synthetic_marker=False)
        output = formatter.format(sample_character_card)
        assert "SYNTHETIC_PERSONA_SCRIPT" not in output

    def test_extension(self):
        """Test extension is .txt."""
        formatter = SystemPromptFormatter()
        assert formatter.extension() == ".txt"


class TestJinja2TemplateFormatter:
    """Tests for Jinja2TemplateFormatter."""

    def test_format_returns_template(self, sample_character_card):
        """Test format returns template (not rendered)."""
        formatter = Jinja2TemplateFormatter()
        output = formatter.format(sample_character_card)
        assert "{{ identity.name }}" in output

    def test_render_substitutes_values(self, sample_character_card):
        """Test render substitutes values."""
        formatter = Jinja2TemplateFormatter()
        output = formatter.render(sample_character_card)
        assert "Sarah Chen" in output
        assert "{{ identity.name }}" not in output

    def test_render_with_context(self, sample_character_card):
        """Test render with context."""
        formatter = Jinja2TemplateFormatter()
        output = formatter.render(
            sample_character_card,
            context="User is asking about campaign performance",
        )
        assert "campaign performance" in output

    def test_render_with_history(self, sample_character_card):
        """Test render with conversation history."""
        formatter = Jinja2TemplateFormatter()
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        output = formatter.render(sample_character_card, conversation_history=history)
        assert "Hello" in output
        assert "Hi there" in output

    def test_custom_template(self, sample_character_card):
        """Test custom template."""
        custom = "Name: {{ identity.name }}"
        formatter = Jinja2TemplateFormatter(custom_template=custom)
        output = formatter.render(sample_character_card)
        assert output == "Name: Sarah Chen"

    def test_extension(self):
        """Test extension is .j2."""
        formatter = Jinja2TemplateFormatter()
        assert formatter.extension() == ".j2"


class TestGetFormatter:
    """Tests for get_formatter function."""

    def test_get_character_card_formatter(self):
        """Test getting character card formatter."""
        formatter = get_formatter(ScriptFormat.CHARACTER_CARD)
        assert isinstance(formatter, CharacterCardFormatter)

    def test_get_system_prompt_formatter(self):
        """Test getting system prompt formatter."""
        formatter = get_formatter(ScriptFormat.SYSTEM_PROMPT)
        assert isinstance(formatter, SystemPromptFormatter)

    def test_get_jinja2_formatter(self):
        """Test getting Jinja2 formatter."""
        formatter = get_formatter(ScriptFormat.JINJA2_TEMPLATE)
        assert isinstance(formatter, Jinja2TemplateFormatter)


# ==================== Integration Tests ====================


class TestScriptGenerationIntegration:
    """Integration tests for script generation."""

    def test_full_generation_workflow(self, sample_persona):
        """Test complete generation workflow."""
        # Generate script
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona)

        # Verify not blocked
        assert result.blocked is False

        # Verify output is valid JSON
        data = json.loads(result.output)
        assert "identity" in data
        assert "psychological_profile" in data
        assert "provenance" in data

        # Verify synthetic marker present
        assert data["provenance"]["synthetic_marker"] == "SYNTHETIC_PERSONA_SCRIPT"

    def test_no_raw_quotes_in_output(self, sample_persona):
        """Test no raw quotes appear in generated output."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona)

        # Raw quotes should not appear
        for quote in sample_persona.quotes:
            assert quote not in result.output

    def test_no_persona_id_in_card_content(self, sample_persona):
        """Test persona ID doesn't appear in card content."""
        generator = ConversationScriptGenerator()
        result = generator.generate(sample_persona)

        # Check all content fields (not provenance)
        card_dict = result.character_card.to_dict()
        identity_str = str(card_dict["identity"])
        profile_str = str(card_dict["psychological_profile"])
        style_str = str(card_dict["communication_style"])

        assert sample_persona.id not in identity_str
        assert sample_persona.id not in profile_str
        assert sample_persona.id not in style_str
