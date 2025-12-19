"""
Tests for JSON extraction utility (F-128).
"""

import pytest

from persona.core.utils import JSONExtractor


class TestStripMarkdownCodeBlocks:
    """Tests for strip_markdown_code_blocks method."""

    def test_strip_json_code_block(self):
        """Test stripping ```json code block."""
        text = '```json\n{"name": "Alice"}\n```'
        result = JSONExtractor.strip_markdown_code_blocks(text)
        assert result == '{"name": "Alice"}'

    def test_strip_plain_code_block(self):
        """Test stripping ``` code block without language."""
        text = '```\n{"data": 123}\n```'
        result = JSONExtractor.strip_markdown_code_blocks(text)
        assert result == '{"data": 123}'

    def test_no_code_block(self):
        """Test text without code blocks passes through."""
        text = '{"already": "plain"}'
        result = JSONExtractor.strip_markdown_code_blocks(text)
        assert result == '{"already": "plain"}'

    def test_strip_with_trailing_content(self):
        """Test stripping ignores content after closing block."""
        text = '```json\n{"key": "value"}\n```\nSome text after'
        result = JSONExtractor.strip_markdown_code_blocks(text)
        assert result == '{"key": "value"}'

    def test_empty_code_block(self):
        """Test empty code block returns empty string."""
        text = "```\n```"
        result = JSONExtractor.strip_markdown_code_blocks(text)
        assert result == ""

    def test_multiline_json(self):
        """Test multiline JSON in code block."""
        text = '```json\n{\n  "name": "Bob",\n  "age": 30\n}\n```'
        result = JSONExtractor.strip_markdown_code_blocks(text)
        assert '"name": "Bob"' in result
        assert '"age": 30' in result


class TestExtractJson:
    """Tests for extract_json method."""

    def test_extract_from_code_block(self):
        """Test extracting JSON from markdown code block."""
        text = '```json\n{"name": "Alice", "age": 25}\n```'
        result = JSONExtractor.extract_json(text)
        assert result == {"name": "Alice", "age": 25}

    def test_extract_raw_json(self):
        """Test extracting raw JSON without code blocks."""
        text = '{"key": "value"}'
        result = JSONExtractor.extract_json(text)
        assert result == {"key": "value"}

    def test_extract_json_array(self):
        """Test extracting JSON array."""
        text = '[{"id": 1}, {"id": 2}]'
        result = JSONExtractor.extract_json(text)
        assert result == [{"id": 1}, {"id": 2}]

    def test_extract_embedded_object(self):
        """Test extracting JSON object embedded in text."""
        text = 'Here is the data: {"name": "Bob"} as requested.'
        result = JSONExtractor.extract_json(text)
        assert result == {"name": "Bob"}

    def test_extract_embedded_array(self):
        """Test extracting JSON array embedded in text."""
        text = 'Results: [1, 2, 3] end.'
        result = JSONExtractor.extract_json(text)
        assert result == [1, 2, 3]

    def test_returns_empty_dict_on_failure(self):
        """Test returns empty dict when no JSON found."""
        text = "This is just plain text."
        result = JSONExtractor.extract_json(text)
        assert result == {}

    def test_handles_nested_json(self):
        """Test handling nested JSON structures."""
        text = '{"outer": {"inner": {"value": 42}}}'
        result = JSONExtractor.extract_json(text)
        assert result == {"outer": {"inner": {"value": 42}}}

    def test_handles_malformed_json_gracefully(self):
        """Test graceful handling of malformed JSON."""
        text = '{"incomplete": '
        result = JSONExtractor.extract_json(text)
        assert result == {}

    def test_prefers_code_block_over_embedded(self):
        """Test code block JSON is preferred over embedded."""
        text = '{"wrong": 1}\n```json\n{"correct": 2}\n```'
        result = JSONExtractor.extract_json(text)
        assert result == {"correct": 2}


class TestExtractJsonArray:
    """Tests for extract_json_array method."""

    def test_extract_array(self):
        """Test extracting array returns list."""
        text = '[{"name": "Alice"}, {"name": "Bob"}]'
        result = JSONExtractor.extract_json_array(text)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Bob"

    def test_wraps_single_object(self):
        """Test single object is wrapped in list."""
        text = '{"name": "Charlie"}'
        result = JSONExtractor.extract_json_array(text)
        assert len(result) == 1
        assert result[0]["name"] == "Charlie"

    def test_returns_empty_list_on_failure(self):
        """Test returns empty list when no JSON found."""
        text = "No JSON here"
        result = JSONExtractor.extract_json_array(text)
        assert result == []

    def test_filters_non_dict_items(self):
        """Test non-dict items in array are filtered."""
        text = '[{"valid": true}, "string", 123, {"also_valid": true}]'
        result = JSONExtractor.extract_json_array(text)
        assert len(result) == 2
        assert result[0]["valid"] is True
        assert result[1]["also_valid"] is True


class TestExtractJsonObject:
    """Tests for extract_json_object method."""

    def test_extract_object(self):
        """Test extracting object returns dict."""
        text = '{"name": "Dave"}'
        result = JSONExtractor.extract_json_object(text)
        assert result == {"name": "Dave"}

    def test_extract_first_from_array(self):
        """Test extracts first object from array."""
        text = '[{"first": 1}, {"second": 2}]'
        result = JSONExtractor.extract_json_object(text)
        assert result == {"first": 1}

    def test_uses_fallback(self):
        """Test uses fallback when extraction fails."""
        text = "No JSON"
        fallback = {"default": "value"}
        result = JSONExtractor.extract_json_object(text, fallback=fallback)
        assert result == {"default": "value"}

    def test_default_fallback_is_empty_dict(self):
        """Test default fallback is empty dict."""
        text = "No JSON"
        result = JSONExtractor.extract_json_object(text)
        assert result == {}

    def test_skips_empty_dicts(self):
        """Test skips empty dicts in arrays."""
        text = "[{}, {}, {\"real\": true}]"
        result = JSONExtractor.extract_json_object(text)
        assert result == {"real": True}


class TestTryParse:
    """Tests for try_parse method."""

    def test_success_with_object(self):
        """Test successful parse of object."""
        success, data = JSONExtractor.try_parse('{"key": "value"}')
        assert success is True
        assert data == {"key": "value"}

    def test_success_with_array(self):
        """Test successful parse of array."""
        success, data = JSONExtractor.try_parse("[1, 2, 3]")
        assert success is True
        assert data == [1, 2, 3]

    def test_failure_with_invalid(self):
        """Test failure with invalid JSON."""
        success, data = JSONExtractor.try_parse("not json")
        assert success is False
        assert data == {}

    def test_failure_with_empty_object(self):
        """Test failure with empty object."""
        success, data = JSONExtractor.try_parse("{}")
        assert success is False
        assert data == {}

    def test_failure_with_empty_array(self):
        """Test failure with empty array."""
        success, data = JSONExtractor.try_parse("[]")
        assert success is False
        assert data == []


class TestRealWorldScenarios:
    """Tests for real-world LLM response scenarios."""

    def test_anthropic_style_response(self):
        """Test typical Anthropic response format."""
        text = """Here are the personas based on your research data:

```json
[
  {
    "id": "persona-1",
    "name": "Alice Developer",
    "goals": ["Build great software"]
  },
  {
    "id": "persona-2",
    "name": "Bob Manager",
    "goals": ["Ship on time"]
  }
]
```

I've created two distinct personas based on the patterns in your data."""

        result = JSONExtractor.extract_json_array(text)
        assert len(result) == 2
        assert result[0]["name"] == "Alice Developer"
        assert result[1]["name"] == "Bob Manager"

    def test_openai_style_response(self):
        """Test typical OpenAI response format."""
        text = """{"personas": [{"id": "p1", "name": "User A"}, {"id": "p2", "name": "User B"}]}"""

        result = JSONExtractor.extract_json(text)
        assert "personas" in result
        assert len(result["personas"]) == 2

    def test_llm_with_preamble(self):
        """Test LLM response with natural language preamble."""
        text = """Based on my analysis, here is the persona:

{"id": "persona-expert", "name": "Technical Expert", "role": "Developer"}

This persona represents the main user archetype."""

        result = JSONExtractor.extract_json_object(text)
        assert result["name"] == "Technical Expert"

    def test_llm_with_nested_code_blocks(self):
        """Test response with code language specifier."""
        text = """```json
{
    "id": "complex-1",
    "nested": {
        "level1": {
            "level2": "deep value"
        }
    }
}
```"""
        result = JSONExtractor.extract_json(text)
        assert result["nested"]["level1"]["level2"] == "deep value"
