"""Tests for claim extractor."""

from unittest.mock import Mock

from persona.core.generation.parser import Persona
from persona.core.providers.base import LLMProvider, LLMResponse
from persona.core.quality.faithfulness.extractor import ClaimExtractor
from persona.core.quality.faithfulness.models import ClaimType


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self, response_content: str = "[]"):
        self.response_content = response_content

    @property
    def name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return "mock-model"

    @property
    def available_models(self) -> list[str]:
        return ["mock-model"]

    def generate(self, prompt: str, model: str | None = None, **kwargs) -> LLMResponse:
        return LLMResponse(
            content=self.response_content,
            model=model or self.default_model,
            input_tokens=10,
            output_tokens=10,
        )

    def is_configured(self) -> bool:
        return True


class TestClaimExtractor:
    """Tests for ClaimExtractor."""

    def test_extract_simple_claims_demographics(self):
        """Test simple extraction of demographic claims."""
        persona = Persona(
            id="test-1",
            name="Test Person",
            demographics={"age": "25", "occupation": "Teacher"},
            goals=[],
            pain_points=[],
        )

        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        claims = extractor._extract_simple_claims(persona)

        assert len(claims) >= 2
        # Check demographic claims extracted
        demo_claims = [c for c in claims if c.claim_type == ClaimType.DEMOGRAPHIC]
        assert len(demo_claims) == 2

    def test_extract_simple_claims_goals(self):
        """Test simple extraction of goal claims."""
        persona = Persona(
            id="test-1",
            name="Test Person",
            goals=["Learn Python", "Build portfolio"],
            pain_points=[],
        )

        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        claims = extractor._extract_simple_claims(persona)

        goal_claims = [c for c in claims if c.claim_type == ClaimType.GOAL]
        assert len(goal_claims) == 2
        assert goal_claims[0].text == "Learn Python"
        assert goal_claims[1].text == "Build portfolio"

    def test_extract_simple_claims_pain_points(self):
        """Test simple extraction of pain point claims."""
        persona = Persona(
            id="test-1",
            name="Test Person",
            pain_points=["Lack of time", "High costs"],
            goals=[],
        )

        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        claims = extractor._extract_simple_claims(persona)

        pain_claims = [c for c in claims if c.claim_type == ClaimType.PAIN_POINT]
        assert len(pain_claims) == 2
        assert pain_claims[0].text == "Lack of time"

    def test_extract_simple_claims_behaviours(self):
        """Test simple extraction of behaviour claims."""
        persona = Persona(
            id="test-1",
            name="Test Person",
            behaviours=["Checks email daily", "Uses mobile apps"],
            goals=[],
            pain_points=[],
        )

        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        claims = extractor._extract_simple_claims(persona)

        behaviour_claims = [c for c in claims if c.claim_type == ClaimType.BEHAVIOUR]
        assert len(behaviour_claims) == 2

    def test_extract_simple_claims_quotes(self):
        """Test simple extraction of quote claims."""
        persona = Persona(
            id="test-1",
            name="Test Person",
            quotes=["I love this product", "It's really helpful"],
            goals=[],
            pain_points=[],
        )

        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        claims = extractor._extract_simple_claims(persona)

        quote_claims = [c for c in claims if c.claim_type == ClaimType.QUOTE]
        assert len(quote_claims) == 2

    def test_parse_llm_response_json_array(self):
        """Test parsing LLM response with JSON array."""
        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        response = """
        [
            {
                "text": "User is 25 years old",
                "source_field": "demographics.age",
                "claim_type": "demographic"
            }
        ]
        """

        claims_data = extractor._parse_llm_response(response)

        assert len(claims_data) == 1
        assert claims_data[0]["text"] == "User is 25 years old"

    def test_parse_llm_response_with_code_block(self):
        """Test parsing LLM response with markdown code block."""
        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        response = """
        Here are the claims:

        ```json
        [
            {
                "text": "User is 25 years old",
                "source_field": "demographics.age",
                "claim_type": "demographic"
            }
        ]
        ```
        """

        claims_data = extractor._parse_llm_response(response)

        assert len(claims_data) == 1
        assert claims_data[0]["text"] == "User is 25 years old"

    def test_parse_claim_type(self):
        """Test claim type parsing."""
        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        assert extractor._parse_claim_type("factual") == ClaimType.FACTUAL
        assert extractor._parse_claim_type("opinion") == ClaimType.OPINION
        assert extractor._parse_claim_type("preference") == ClaimType.PREFERENCE
        assert extractor._parse_claim_type("behaviour") == ClaimType.BEHAVIOUR
        assert extractor._parse_claim_type("behavior") == ClaimType.BEHAVIOUR  # US
        assert extractor._parse_claim_type("quote") == ClaimType.QUOTE
        assert extractor._parse_claim_type("demographic") == ClaimType.DEMOGRAPHIC
        assert extractor._parse_claim_type("goal") == ClaimType.GOAL
        assert extractor._parse_claim_type("pain_point") == ClaimType.PAIN_POINT
        assert extractor._parse_claim_type("pain point") == ClaimType.PAIN_POINT

    def test_parse_claim_type_default(self):
        """Test claim type parsing with unknown type."""
        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        # Unknown types default to FACTUAL
        assert extractor._parse_claim_type("unknown") == ClaimType.FACTUAL

    def test_deduplicate_claims(self):
        """Test claim deduplication."""
        from persona.core.quality.faithfulness.models import Claim

        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        claim1 = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )
        claim2 = Claim(
            text="User is 25 years old",  # Duplicate
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )
        claim3 = Claim(
            text="User likes hiking",
            source_field="preferences",
            claim_type=ClaimType.PREFERENCE,
        )

        claims = [claim1, claim2, claim3]
        unique = extractor._deduplicate_claims(claims)

        assert len(unique) == 2
        # Should keep first occurrence
        assert unique[0].text == "User is 25 years old"
        assert unique[1].text == "User likes hiking"

    def test_deduplicate_claims_case_insensitive(self):
        """Test deduplication is case insensitive."""
        from persona.core.quality.faithfulness.models import Claim

        llm = MockLLMProvider()
        extractor = ClaimExtractor(llm)

        claim1 = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )
        claim2 = Claim(
            text="USER IS 25 YEARS OLD",  # Different case
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        claims = [claim1, claim2]
        unique = extractor._deduplicate_claims(claims)

        assert len(unique) == 1

    def test_extract_claims_fallback_on_llm_failure(self):
        """Test extraction falls back to simple extraction on LLM failure."""
        # Mock LLM that raises error
        llm = Mock(spec=LLMProvider)
        llm.generate.side_effect = RuntimeError("API error")

        extractor = ClaimExtractor(llm)

        persona = Persona(
            id="test-1",
            name="Test Person",
            demographics={"age": "25"},
            goals=["Learn Python"],
            pain_points=[],
        )

        # Should still return claims from simple extraction
        claims = extractor.extract_claims(persona)

        assert len(claims) >= 2  # At least demographics and goals

    def test_extract_with_llm_valid_response(self):
        """Test LLM-based extraction with valid response."""
        llm_response = """
        [
            {
                "text": "User is 25 years old",
                "source_field": "demographics.age",
                "claim_type": "demographic",
                "context": "Age: 25"
            }
        ]
        """
        llm = MockLLMProvider(response_content=llm_response)
        extractor = ClaimExtractor(llm)

        persona = Persona(
            id="test-1",
            name="Test Person",
            demographics={"age": "25"},
            goals=[],
            pain_points=[],
        )

        claims = extractor._extract_with_llm(persona)

        assert len(claims) >= 1
        # Check LLM-extracted claim
        llm_claim = next((c for c in claims if c.context == "Age: 25"), None)
        assert llm_claim is not None
        assert llm_claim.text == "User is 25 years old"
