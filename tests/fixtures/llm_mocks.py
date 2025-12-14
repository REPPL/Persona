"""
LLM provider mock response factories.

This module provides functions to create mock API responses for testing
without making actual API calls.
"""

import json
from typing import Any


def create_openai_response(
    content: str,
    model: str = "gpt-4",
    finish_reason: str = "stop",
    prompt_tokens: int = 100,
    completion_tokens: int = 200,
) -> dict[str, Any]:
    """
    Create a mock OpenAI chat completion response.

    Args:
        content: The response content text
        model: Model identifier
        finish_reason: Why generation stopped
        prompt_tokens: Input token count
        completion_tokens: Output token count

    Returns:
        Dict matching OpenAI API response structure
    """
    return {
        "id": "chatcmpl-test-12345",
        "object": "chat.completion",
        "created": 1702000000,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def create_anthropic_response(
    content: str,
    model: str = "claude-3-sonnet-20240229",
    stop_reason: str = "end_turn",
    input_tokens: int = 100,
    output_tokens: int = 200,
) -> dict[str, Any]:
    """
    Create a mock Anthropic messages response.

    Args:
        content: The response content text
        model: Model identifier
        stop_reason: Why generation stopped
        input_tokens: Input token count
        output_tokens: Output token count

    Returns:
        Dict matching Anthropic API response structure
    """
    return {
        "id": "msg_test_12345",
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": [
            {
                "type": "text",
                "text": content,
            }
        ],
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
    }


def create_gemini_response(
    content: str,
    model: str = "gemini-1.5-pro",
    finish_reason: str = "STOP",
    prompt_tokens: int = 100,
    candidates_tokens: int = 200,
) -> dict[str, Any]:
    """
    Create a mock Google Gemini generate content response.

    Args:
        content: The response content text
        model: Model identifier
        finish_reason: Why generation stopped
        prompt_tokens: Input token count
        candidates_tokens: Output token count

    Returns:
        Dict matching Gemini API response structure
    """
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": content,
                        }
                    ],
                    "role": "model",
                },
                "finishReason": finish_reason,
                "index": 0,
            }
        ],
        "usageMetadata": {
            "promptTokenCount": prompt_tokens,
            "candidatesTokenCount": candidates_tokens,
            "totalTokenCount": prompt_tokens + candidates_tokens,
        },
        "modelVersion": model,
    }


def create_persona_generation_response(
    personas: list[dict[str, Any]] | None = None,
    reasoning: str | None = None,
) -> str:
    """
    Create a mock LLM response containing personas with optional reasoning.

    Args:
        personas: List of persona dictionaries (uses default if None)
        reasoning: Optional reasoning trace to include

    Returns:
        String response formatted as expected by persona parser
    """
    if personas is None:
        personas = [
            {
                "id": "persona-001",
                "name": "Alex Chen",
                "demographics": {
                    "age_range": "25-34",
                    "occupation": "Software Developer",
                    "location": "Urban",
                },
                "goals": [
                    "Streamline workflow efficiency",
                    "Stay updated with latest technologies",
                ],
                "pain_points": [
                    "Too many tools to manage",
                    "Difficulty finding reliable documentation",
                ],
                "behaviours": [
                    "Heavy keyboard shortcut user",
                    "Prefers CLI over GUI",
                ],
                "quotes": [
                    "I just want things to work without friction.",
                ],
            }
        ]

    response_parts = []

    if reasoning:
        response_parts.append(f"<reasoning>\n{reasoning}\n</reasoning>")

    response_parts.append("<output>")
    response_parts.append(json.dumps({"personas": personas}, indent=2))
    response_parts.append("</output>")

    return "\n".join(response_parts)


def create_error_response(
    provider: str,
    error_type: str = "authentication_error",
    message: str = "Invalid API key",
) -> dict[str, Any]:
    """
    Create a mock error response for a provider.

    Args:
        provider: Provider name (openai, anthropic, gemini)
        error_type: Type of error
        message: Error message

    Returns:
        Dict matching provider's error response structure
    """
    if provider == "openai":
        return {
            "error": {
                "message": message,
                "type": error_type,
                "param": None,
                "code": "invalid_api_key",
            }
        }
    elif provider == "anthropic":
        return {
            "type": "error",
            "error": {
                "type": error_type,
                "message": message,
            },
        }
    elif provider == "gemini":
        return {
            "error": {
                "code": 401,
                "message": message,
                "status": "UNAUTHENTICATED",
            }
        }
    else:
        raise ValueError(f"Unknown provider: {provider}")
