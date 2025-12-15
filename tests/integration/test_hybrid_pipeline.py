"""
Integration test for hybrid pipeline.

This test demonstrates the hybrid pipeline working end-to-end.
Requires Ollama to be running with qwen2.5:7b model installed.

Run with:
    pytest tests/integration/test_hybrid_pipeline.py -v
"""

import pytest

from persona.core.hybrid import HybridConfig, HybridPipeline


@pytest.mark.real_api
async def test_hybrid_pipeline_local_only():
    """
    Test hybrid pipeline in local-only mode.

    This test requires:
    - Ollama running (ollama serve)
    - qwen2.5:7b model installed (ollama pull qwen2.5:7b)
    - qwen2.5:72b model installed for judge (ollama pull qwen2.5:72b)
    """
    # Sample research data
    input_data = """
    User Interview Transcript:

    Interview 1: Sarah, 34, Marketing Manager
    "I spend most of my day in meetings and responding to emails. I need tools
    that help me stay organized and prioritize tasks. I get frustrated when
    software has too many features that I never use."

    Interview 2: Michael, 28, Software Developer
    "I prefer keyboard shortcuts over clicking through menus. Performance matters
    to me - slow loading times are a dealbreaker. I also value good documentation."

    Interview 3: Lisa, 42, Project Coordinator
    "I collaborate with people across different time zones. Real-time updates and
    notifications are essential for my work. I appreciate when software is
    intuitive and doesn't require training."
    """

    # Configure local-only pipeline
    config = HybridConfig(
        local_model="qwen2.5:7b",
        frontier_provider=None,  # Local-only mode
        quality_threshold=0.7,
        batch_size=3,
    )

    # Create and run pipeline
    pipeline = HybridPipeline(config)
    result = await pipeline.generate(input_data=input_data, count=3)

    # Verify results
    assert result.persona_count == 3
    assert result.draft_count == 3
    assert result.passing_count >= 0  # May or may not pass threshold
    assert result.refined_count == 0  # No frontier refinement in local-only mode
    assert result.total_cost == 0.0  # Ollama is free

    # Verify personas have required fields
    for persona in result.personas:
        assert "id" in persona
        assert "name" in persona

    # Print results for manual verification
    print(f"\n{'=' * 60}")
    print(f"Hybrid Pipeline Test Results (Local-Only Mode)")
    print(f"{'=' * 60}")
    print(f"Generated: {result.persona_count} personas")
    print(f"Time: {result.generation_time:.2f}s")
    print(f"Cost: ${result.total_cost:.4f}")
    print(f"\nPersonas:")
    for i, persona in enumerate(result.personas, 1):
        print(f"  {i}. {persona.get('name', 'Unknown')} ({persona.get('id', 'unknown')})")
    print(f"{'=' * 60}\n")


@pytest.mark.real_api
@pytest.mark.skipif(
    True,  # Skip by default - run manually with paid APIs
    reason="Requires frontier APIs with costs - run manually with API keys configured",
)
async def test_hybrid_pipeline_full_hybrid():
    """
    Test full hybrid pipeline with frontier refinement.

    This test requires:
    - Ollama running with qwen2.5:7b and qwen2.5:72b
    - ANTHROPIC_API_KEY environment variable set
    - --run-paid-api pytest flag (to acknowledge API costs)

    Run with:
        pytest tests/integration/test_hybrid_pipeline.py::test_hybrid_pipeline_full_hybrid -v --run-paid-api
    """
    # Sample research data
    input_data = """
    Brief user feedback:
    - "I need something simple and fast"
    - "Too many options confuse me"
    - "Mobile experience is important"
    """

    # Configure full hybrid pipeline
    config = HybridConfig(
        local_model="qwen2.5:7b",
        frontier_provider="anthropic",
        frontier_model="claude-3-5-haiku-20241022",  # Use cheaper model for testing
        quality_threshold=0.8,  # High threshold to trigger refinement
        max_cost=0.50,  # Low budget limit
        batch_size=2,
    )

    # Create and run pipeline
    pipeline = HybridPipeline(config)
    result = await pipeline.generate(input_data=input_data, count=2)

    # Verify results
    assert result.persona_count == 2
    assert result.draft_count == 2
    assert result.total_cost < 0.50  # Respects budget

    # Print results
    print(f"\n{'=' * 60}")
    print(f"Hybrid Pipeline Test Results (Full Hybrid Mode)")
    print(f"{'=' * 60}")
    print(f"Generated: {result.persona_count} personas")
    print(f"Drafts: {result.draft_count}")
    print(f"Passed threshold: {result.passing_count}")
    print(f"Refined: {result.refined_count}")
    print(f"Time: {result.generation_time:.2f}s")
    print(f"Cost: ${result.total_cost:.4f}")
    print(f"\nPersonas:")
    for i, persona in enumerate(result.personas, 1):
        status = "[refined]" if persona.get("_refined", False) else "[draft]"
        print(f"  {i}. {persona.get('name', 'Unknown')} {status}")
    print(f"{'=' * 60}\n")
