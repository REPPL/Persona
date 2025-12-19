"""
Unit tests for pipeline stage base classes (F-130, F-134).
"""

import pytest

from persona.core.hybrid.stages.base import (
    PipelineContext,
    PipelineStage,
    StageInput,
    StageOutput,
)


class TestStageInput:
    """Tests for StageInput dataclass."""

    def test_default_values(self):
        """Test default field values."""
        input_data = StageInput()

        assert input_data.personas == []
        assert input_data.raw_data == ""
        assert input_data.config is None
        assert input_data.count == 0
        assert input_data.threshold == 0.0

    def test_custom_values(self):
        """Test setting custom values."""
        personas = [{"id": "p1", "name": "Alice"}]
        input_data = StageInput(
            personas=personas,
            raw_data="Test data",
            count=10,
            threshold=0.7,
        )

        assert input_data.personas == personas
        assert input_data.raw_data == "Test data"
        assert input_data.count == 10
        assert input_data.threshold == 0.7


class TestStageOutput:
    """Tests for StageOutput dataclass."""

    def test_default_values(self):
        """Test default field values."""
        output = StageOutput()

        assert output.personas == []
        assert output.passed == []
        assert output.failed == []
        assert output.metrics == {}
        assert output.tokens_used == {}

    def test_custom_values(self):
        """Test setting custom values."""
        personas = [{"id": "p1", "name": "Alice"}]
        passed = [{"id": "p1", "name": "Alice"}]
        failed = [{"id": "p2", "name": "Bob"}]
        metrics = {"quality_score": 0.8}
        tokens = {"input": 100, "output": 50}

        output = StageOutput(
            personas=personas,
            passed=passed,
            failed=failed,
            metrics=metrics,
            tokens_used=tokens,
        )

        assert output.personas == personas
        assert output.passed == passed
        assert output.failed == failed
        assert output.metrics == metrics
        assert output.tokens_used == tokens


class TestPipelineContext:
    """Tests for PipelineContext dataclass."""

    def test_default_values(self):
        """Test default field values."""
        context = PipelineContext()

        assert context.cost_tracker is None
        assert context.progress_callback is None
        assert context.stage_results == {}
        assert context.metadata == {}

    def test_record_stage_result(self):
        """Test recording stage results."""
        context = PipelineContext()
        output = StageOutput(personas=[{"id": "p1"}])

        context.record_stage_result("draft", output)

        assert "draft" in context.stage_results
        assert context.stage_results["draft"] == output

    def test_record_multiple_stage_results(self):
        """Test recording multiple stage results."""
        context = PipelineContext()
        draft_output = StageOutput(personas=[{"id": "p1"}])
        filter_output = StageOutput(
            passed=[{"id": "p1"}],
            failed=[],
        )

        context.record_stage_result("draft", draft_output)
        context.record_stage_result("filter", filter_output)

        assert len(context.stage_results) == 2
        assert context.stage_results["draft"].personas == [{"id": "p1"}]
        assert context.stage_results["filter"].passed == [{"id": "p1"}]

    def test_overwrites_existing_stage_result(self):
        """Test that recording overwrites existing result."""
        context = PipelineContext()
        first_output = StageOutput(personas=[{"id": "p1"}])
        second_output = StageOutput(personas=[{"id": "p2"}])

        context.record_stage_result("draft", first_output)
        context.record_stage_result("draft", second_output)

        assert context.stage_results["draft"].personas == [{"id": "p2"}]


class ConcreteStage(PipelineStage):
    """Concrete implementation for testing."""

    def __init__(self, stage_name: str = "test_stage"):
        self._name = stage_name

    @property
    def name(self) -> str:
        return self._name

    async def execute(
        self,
        input_data: StageInput,
        context: PipelineContext,
    ) -> StageOutput:
        return StageOutput(personas=input_data.personas)


class SkippableStage(ConcreteStage):
    """Stage that can be conditionally skipped."""

    def __init__(self, should_skip: bool = False):
        super().__init__("skippable_stage")
        self._should_skip_flag = should_skip

    def should_skip(
        self,
        input_data: StageInput,
        context: PipelineContext,
    ) -> bool:
        return self._should_skip_flag


class TestPipelineStage:
    """Tests for PipelineStage abstract base class."""

    def test_concrete_implementation_has_name(self):
        """Test that concrete stage has name property."""
        stage = ConcreteStage("my_stage")

        assert stage.name == "my_stage"

    @pytest.mark.asyncio
    async def test_execute_returns_output(self):
        """Test that execute returns StageOutput."""
        stage = ConcreteStage()
        input_data = StageInput(personas=[{"id": "p1"}])
        context = PipelineContext()

        result = await stage.execute(input_data, context)

        assert isinstance(result, StageOutput)
        assert result.personas == [{"id": "p1"}]

    def test_should_skip_default(self):
        """Test that should_skip returns False by default."""
        stage = ConcreteStage()
        input_data = StageInput()
        context = PipelineContext()

        assert stage.should_skip(input_data, context) is False

    def test_should_skip_override(self):
        """Test that should_skip can be overridden."""
        stage = SkippableStage(should_skip=True)
        input_data = StageInput()
        context = PipelineContext()

        assert stage.should_skip(input_data, context) is True

    @pytest.mark.asyncio
    async def test_pre_execute_hook(self):
        """Test that pre_execute hook is callable."""
        stage = ConcreteStage()
        input_data = StageInput()
        context = PipelineContext()

        # Should not raise
        await stage.pre_execute(input_data, context)

    @pytest.mark.asyncio
    async def test_post_execute_hook(self):
        """Test that post_execute hook is callable."""
        stage = ConcreteStage()
        output = StageOutput()
        context = PipelineContext()

        # Should not raise
        await stage.post_execute(output, context)


class TestModuleExports:
    """Tests for module exports."""

    def test_can_import_from_stages(self):
        """Test that base classes are exported from stages package."""
        from persona.core.hybrid.stages import (
            PipelineContext,
            PipelineStage,
            StageInput,
            StageOutput,
        )

        assert PipelineStage is not None
        assert StageInput is not None
        assert StageOutput is not None
        assert PipelineContext is not None

    def test_can_import_stage_functions(self):
        """Test that stage functions are exported."""
        from persona.core.hybrid.stages import (
            draft_personas,
            filter_personas,
            refine_personas,
        )

        assert draft_personas is not None
        assert filter_personas is not None
        assert refine_personas is not None
