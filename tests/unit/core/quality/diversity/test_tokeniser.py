"""Unit tests for tokeniser module."""


from persona.core.generation.parser import Persona
from persona.core.quality.diversity.tokeniser import extract_persona_text, tokenise


class TestExtractPersonaText:
    """Tests for extract_persona_text function."""

    def test_extract_empty_persona(self):
        """Test extraction from empty persona."""
        persona = Persona(id="1", name="")
        text = extract_persona_text(persona)
        assert text == ""

    def test_extract_name_only(self):
        """Test extraction with only name populated."""
        persona = Persona(id="1", name="Alice Johnson")
        text = extract_persona_text(persona)
        assert "Alice Johnson" in text

    def test_extract_demographics(self):
        """Test extraction of demographics."""
        persona = Persona(
            id="1",
            name="Bob Smith",
            demographics={
                "age": 35,
                "occupation": "Software Engineer",
                "location": "San Francisco",
            },
        )
        text = extract_persona_text(persona)
        assert "Bob Smith" in text
        assert "35" in text
        assert "Software Engineer" in text
        assert "San Francisco" in text

    def test_extract_goals(self):
        """Test extraction of goals."""
        persona = Persona(
            id="1",
            name="Charlie",
            goals=[
                "Learn new programming languages",
                "Build a successful startup",
            ],
        )
        text = extract_persona_text(persona)
        assert "Learn new programming languages" in text
        assert "Build a successful startup" in text

    def test_extract_pain_points(self):
        """Test extraction of pain points."""
        persona = Persona(
            id="1",
            name="Diana",
            pain_points=[
                "Limited time for learning",
                "Difficulty finding resources",
            ],
        )
        text = extract_persona_text(persona)
        assert "Limited time for learning" in text
        assert "Difficulty finding resources" in text

    def test_extract_behaviours(self):
        """Test extraction of behaviours."""
        persona = Persona(
            id="1",
            name="Eve",
            behaviours=[
                "Reads tech blogs daily",
                "Attends conferences regularly",
            ],
        )
        text = extract_persona_text(persona)
        assert "Reads tech blogs daily" in text
        assert "Attends conferences regularly" in text

    def test_extract_quotes(self):
        """Test extraction of quotes."""
        persona = Persona(
            id="1",
            name="Frank",
            quotes=[
                "I love learning new things",
                "Technology is my passion",
            ],
        )
        text = extract_persona_text(persona)
        assert "I love learning new things" in text
        assert "Technology is my passion" in text

    def test_extract_all_fields(self):
        """Test extraction with all fields populated."""
        persona = Persona(
            id="1",
            name="Grace Hopper",
            demographics={"age": 40, "occupation": "Computer Scientist"},
            goals=["Advance computing"],
            pain_points=["Limited resources"],
            behaviours=["Works late nights"],
            quotes=["It's easier to ask forgiveness than permission"],
        )
        text = extract_persona_text(persona)
        assert "Grace Hopper" in text
        assert "40" in text
        assert "Computer Scientist" in text
        assert "Advance computing" in text
        assert "Limited resources" in text
        assert "Works late nights" in text
        assert "It's easier to ask forgiveness than permission" in text

    def test_extract_additional_fields(self):
        """Test extraction of additional fields."""
        persona = Persona(
            id="1",
            name="Henry",
            additional={
                "hobbies": "Reading, hiking",
                "skills": ["Python", "Java", "Go"],
                "bio": "Passionate developer",
            },
        )
        text = extract_persona_text(persona)
        assert "Henry" in text
        assert "Reading, hiking" in text
        assert "Python" in text
        assert "Passionate developer" in text


class TestTokenise:
    """Tests for tokenise function."""

    def test_tokenise_empty_string(self):
        """Test tokenising empty string."""
        tokens = tokenise("")
        assert tokens == []

    def test_tokenise_simple_text(self):
        """Test tokenising simple text."""
        text = "Hello world"
        tokens = tokenise(text)
        assert tokens == ["hello", "world"]

    def test_tokenise_with_punctuation(self):
        """Test tokenising text with punctuation."""
        text = "Hello, world! How are you?"
        tokens = tokenise(text)
        assert "hello" in tokens
        assert "world" in tokens
        assert "how" in tokens
        assert "are" in tokens
        assert "you" in tokens
        assert "," not in tokens
        assert "!" not in tokens
        assert "?" not in tokens

    def test_tokenise_case_normalisation(self):
        """Test case normalisation."""
        text = "Hello WORLD HeLLo"
        tokens = tokenise(text)
        assert tokens.count("hello") == 2
        assert tokens.count("world") == 1

    def test_tokenise_contractions(self):
        """Test contraction expansion."""
        text = "I'm happy, you're great, it's wonderful"
        tokens = tokenise(text)
        # Contractions expanded
        assert "am" in tokens
        assert "are" in tokens
        assert "is" in tokens

    def test_tokenise_filters_short_tokens(self):
        """Test filtering of short tokens."""
        text = "a I am going to the store"
        tokens = tokenise(text)
        # Single-letter tokens should be filtered
        assert "a" not in tokens
        # Two or more letters are kept
        assert "am" in tokens
        assert "to" in tokens

    def test_tokenise_filters_numbers(self):
        """Test filtering of pure numeric tokens."""
        text = "I have 123 apples and 456 oranges"
        tokens = tokenise(text)
        assert "123" not in tokens
        assert "456" not in tokens
        assert "have" in tokens
        assert "apples" in tokens

    def test_tokenise_alphanumeric_preserved(self):
        """Test that alphanumeric tokens are preserved."""
        text = "Python3 and Node16 are popular"
        tokens = tokenise(text)
        assert "python3" in tokens
        assert "node16" in tokens

    def test_tokenise_complex_text(self):
        """Test tokenising complex realistic text."""
        text = """
        I'm a software engineer who loves building innovative solutions.
        I've worked with Python, JavaScript, and Go. My goal is to create
        products that make people's lives easier. I don't like when
        technology is overcomplicated.
        """
        tokens = tokenise(text)
        assert len(tokens) > 20
        assert "software" in tokens
        assert "engineer" in tokens
        assert "python" in tokens
        assert "javascript" in tokens
        assert "goal" in tokens
        assert "overcomplicated" in tokens

    def test_tokenise_special_characters(self):
        """Test handling of special characters."""
        text = "hello@world #hashtag $money email@example.com"
        tokens = tokenise(text)
        # Special characters should be removed
        assert "hello" in tokens
        assert "world" in tokens
        assert "hashtag" in tokens
        assert "money" in tokens
        assert "email" in tokens
        assert "example" in tokens
        assert "com" in tokens
