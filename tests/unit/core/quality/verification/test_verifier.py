"""Tests for MultiModelVerifier."""

import pytest

from persona.core.quality.verification import (
    MultiModelVerifier,
    VerificationConfig,
    verify_multi_model,
    verify_self_consistency,
)


# Test model names with proper provider prefixes
MODEL1 = "anthropic:claude-sonnet-4"
MODEL2 = "openai:gpt-4o"
MODEL3 = "gemini:gemini-2.0-flash"


@pytest.mark.asyncio
class TestMultiModelVerifier:
    """Tests for MultiModelVerifier."""

    async def test_basic_verification(self):
        """Test basic multi-model verification."""
        config = VerificationConfig(
            models=["anthropic:claude-sonnet-4", "openai:gpt-4o"],
            samples_per_model=2,
            voting_strategy="majority",
        )

        verifier = MultiModelVerifier(config)
        report = await verifier.verify(
            data="Test data for persona generation",
            count=3,
        )

        assert report.persona_id == "verification"
        assert 0.0 <= report.consistency_score <= 1.0
        assert isinstance(report.agreed_attributes, list)
        assert isinstance(report.disputed_attributes, list)
        assert report.metrics is not None

    async def test_verification_with_persona_id(self):
        """Test verification with custom persona ID."""
        config = VerificationConfig(models=[MODEL1])

        verifier = MultiModelVerifier(config)
        report = await verifier.verify(
            data="Test data",
            count=1,
            persona_id="custom-id",
        )

        assert report.persona_id == "custom-id"

    async def test_verification_parallel_mode(self):
        """Test verification in parallel mode."""
        config = VerificationConfig(
            models=[MODEL1, MODEL2, MODEL3],
            parallel=True,
        )

        verifier = MultiModelVerifier(config)
        report = await verifier.verify(data="Test data", count=2)

        # Should have outputs from multiple models
        assert len(report.model_outputs) > 0

    async def test_verification_sequential_mode(self):
        """Test verification in sequential mode."""
        config = VerificationConfig(
            models=[MODEL1, MODEL2],
            parallel=False,
        )

        verifier = MultiModelVerifier(config)
        report = await verifier.verify(data="Test data", count=2)

        assert len(report.model_outputs) > 0

    async def test_verify_self_consistency(self):
        """Test self-consistency verification."""
        config = VerificationConfig(
            models=[MODEL1],
            samples_per_model=5,
        )

        verifier = MultiModelVerifier(config)
        report = await verifier.verify_self_consistency(
            data="Test data",
            model=MODEL1,
            samples=5,
        )

        assert "self-consistency" in report.persona_id
        assert report.consistency_score >= 0.0

    async def test_verify_self_consistency_custom_id(self):
        """Test self-consistency with custom ID."""
        config = VerificationConfig(models=[MODEL1])

        verifier = MultiModelVerifier(config)
        report = await verifier.verify_self_consistency(
            data="Test data",
            model=MODEL1,
            samples=3,
            persona_id="custom-self-check",
        )

        assert report.persona_id == "custom-self-check"

    async def test_verify_batch(self):
        """Test batch verification."""
        config = VerificationConfig(models=[MODEL1, MODEL2])

        verifier = MultiModelVerifier(config)
        reports = await verifier.verify_batch(
            data="Test data",
            count=3,
        )

        assert isinstance(reports, list)
        assert len(reports) > 0

    async def test_passed_status(self):
        """Test verification pass/fail status."""
        # High threshold - likely to fail
        config_strict = VerificationConfig(
            models=[MODEL1, MODEL2],
            consistency_threshold=0.99,
        )

        verifier_strict = MultiModelVerifier(config_strict)
        report_strict = await verifier_strict.verify(data="Test", count=1)

        # Low threshold - likely to pass
        config_lenient = VerificationConfig(
            models=[MODEL1, MODEL2],
            consistency_threshold=0.01,
        )

        verifier_lenient = MultiModelVerifier(config_lenient)
        report_lenient = await verifier_lenient.verify(data="Test", count=1)

        # At least one should have a clear pass/fail status
        assert isinstance(report_strict.passed, bool)
        assert isinstance(report_lenient.passed, bool)

    async def test_consensus_persona(self):
        """Test consensus persona extraction."""
        config = VerificationConfig(
            models=[MODEL1, MODEL2],
            voting_strategy="majority",
        )

        verifier = MultiModelVerifier(config)
        report = await verifier.verify(data="Test data", count=2)

        consensus = report.get_consensus_persona()
        assert isinstance(consensus, dict)

    async def test_different_voting_strategies(self):
        """Test different voting strategies."""
        strategies = ["majority", "unanimous", "weighted"]

        for strategy in strategies:
            config = VerificationConfig(
                models=[MODEL1, MODEL2],
                voting_strategy=strategy,
            )

            verifier = MultiModelVerifier(config)
            report = await verifier.verify(data="Test", count=1)

            assert report.config.voting_strategy == strategy


@pytest.mark.asyncio
class TestConvenienceFunctions:
    """Tests for convenience functions."""

    async def test_verify_multi_model(self):
        """Test verify_multi_model convenience function."""
        report = await verify_multi_model(
            data="Test data",
            models=[MODEL1, MODEL2],
            count=2,
            samples_per_model=2,
            voting_strategy="majority",
            consistency_threshold=0.7,
            parallel=True,
        )

        assert report is not None
        assert report.config.models == [MODEL1, MODEL2]
        assert report.config.voting_strategy == "majority"
        assert report.config.consistency_threshold == 0.7

    async def test_verify_self_consistency_func(self):
        """Test verify_self_consistency convenience function."""
        report = await verify_self_consistency(
            data="Test data",
            model=MODEL1,
            samples=5,
            consistency_threshold=0.75,
        )

        assert report is not None
        assert report.config.samples_per_model == 5
        assert report.config.consistency_threshold == 0.75

    async def test_verify_multi_model_defaults(self):
        """Test verify_multi_model with default parameters."""
        report = await verify_multi_model(
            data="Test data",
            models=[MODEL1],
            count=1,
        )

        # Should use defaults
        assert report.config.samples_per_model == 3
        assert report.config.voting_strategy == "majority"
        assert report.config.consistency_threshold == 0.7
        assert report.config.parallel is True


class TestVerificationWorkflow:
    """Integration tests for complete verification workflow."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete verification workflow."""
        # Step 1: Configure verification
        config = VerificationConfig(
            models=[MODEL1, MODEL2, MODEL3],
            samples_per_model=2,
            voting_strategy="majority",
            consistency_threshold=0.7,
        )

        # Step 2: Create verifier
        verifier = MultiModelVerifier(config)

        # Step 3: Run verification
        report = await verifier.verify(
            data="User interview transcripts...",
            count=3,
            persona_id="user-researcher",
        )

        # Step 4: Check results
        assert report.persona_id == "user-researcher"
        assert report.consistency_score >= 0.0
        assert isinstance(report.passed, bool)

        # Step 5: Get consensus
        consensus = report.get_consensus_persona()
        assert isinstance(consensus, dict)

        # Step 6: Get detailed agreement
        details = report.get_agreement_details()
        assert isinstance(details, dict)

        # Step 7: Export report
        markdown = report.to_markdown()
        assert isinstance(markdown, str)
        assert "Verification Report" in markdown

        report_dict = report.to_dict()
        assert isinstance(report_dict, dict)
        assert "consistency_score" in report_dict

    @pytest.mark.asyncio
    async def test_workflow_with_prompt_template(self):
        """Test verification with custom prompt template."""
        config = VerificationConfig(models=[MODEL1, MODEL2])
        verifier = MultiModelVerifier(config)

        custom_prompt = "Generate personas from this data: {data}"

        report = await verifier.verify(
            data="Test data",
            count=2,
            prompt_template=custom_prompt,
        )

        assert report is not None

    @pytest.mark.asyncio
    async def test_workflow_different_configurations(self):
        """Test verification with different configurations."""
        configs = [
            VerificationConfig(
                models=[MODEL1],
                voting_strategy="majority",
            ),
            VerificationConfig(
                models=[MODEL1, MODEL2],
                voting_strategy="unanimous",
            ),
            VerificationConfig(
                models=[MODEL1, MODEL2, MODEL3],
                voting_strategy="weighted",
            ),
        ]

        for config in configs:
            verifier = MultiModelVerifier(config)
            report = await verifier.verify(data="Test", count=1)

            assert report.config.voting_strategy == config.voting_strategy
            assert len(report.config.models) == len(config.models)
