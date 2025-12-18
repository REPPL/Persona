"""Tests for context window awareness (F-062)."""


from persona.core.batch.context import (
    MODEL_CONTEXT_WINDOWS,
    ContextBudget,
    ContextManager,
    ContextWarning,
    WarningLevel,
    check_context_usage,
)


class TestContextBudget:
    """Tests for ContextBudget."""

    def test_used_tokens(self):
        """Calculates used tokens."""
        budget = ContextBudget(
            total_tokens=200000,
            system_prompt_tokens=3000,
            input_data_tokens=50000,
            reserved_output_tokens=15000,
        )

        assert budget.used_tokens == 53000

    def test_available_tokens(self):
        """Calculates available tokens."""
        budget = ContextBudget(
            total_tokens=200000,
            system_prompt_tokens=3000,
            input_data_tokens=50000,
            reserved_output_tokens=15000,
        )

        assert budget.available_tokens == 132000

    def test_usage_percentage(self):
        """Calculates usage percentage."""
        budget = ContextBudget(
            total_tokens=100000,
            system_prompt_tokens=25000,
            input_data_tokens=25000,
            reserved_output_tokens=20000,
        )

        assert budget.usage_percentage == 70.0

    def test_usage_percentage_zero_total(self):
        """Handles zero total tokens."""
        budget = ContextBudget(total_tokens=0)
        assert budget.usage_percentage == 0.0

    def test_to_dict(self):
        """Converts to dictionary."""
        budget = ContextBudget(
            total_tokens=200000,
            system_prompt_tokens=3000,
            input_data_tokens=50000,
        )
        data = budget.to_dict()

        assert "total_tokens" in data
        assert "used_tokens" in data
        assert "available_tokens" in data
        assert "usage_percentage" in data


class TestContextWarning:
    """Tests for ContextWarning."""

    def test_to_dict(self):
        """Converts to dictionary."""
        budget = ContextBudget(total_tokens=100000)
        warning = ContextWarning(
            level=WarningLevel.YELLOW,
            message="Test message",
            usage_percentage=75.0,
            budget=budget,
            suggestions=["suggestion 1"],
        )

        data = warning.to_dict()

        assert data["level"] == "yellow"
        assert data["message"] == "Test message"
        assert "suggestions" in data


class TestContextManager:
    """Tests for ContextManager."""

    def test_get_context_window_known_model(self):
        """Gets context for known model."""
        manager = ContextManager()
        window = manager.get_context_window("claude-sonnet-4-20250514")

        assert window == 200000

    def test_get_context_window_unknown_model(self):
        """Returns default for unknown model."""
        manager = ContextManager()
        window = manager.get_context_window("unknown-model")

        assert window == 128000  # Default

    def test_get_context_window_custom(self):
        """Uses custom context windows."""
        manager = ContextManager(custom_windows={"custom-model": 500000})
        window = manager.get_context_window("custom-model")

        assert window == 500000

    def test_calculate_budget(self):
        """Calculates budget correctly."""
        manager = ContextManager()
        budget = manager.calculate_budget(
            model="gpt-4o",
            system_tokens=1000,
            input_tokens=50000,
        )

        assert budget.total_tokens == 128000
        assert budget.system_prompt_tokens == 1000
        assert budget.input_data_tokens == 50000

    def test_check_warning_none_below_threshold(self):
        """Returns None when usage below threshold."""
        manager = ContextManager()
        budget = ContextBudget(
            total_tokens=200000,
            system_prompt_tokens=3000,
            input_data_tokens=50000,
            reserved_output_tokens=15000,
        )

        warning = manager.check_warning(budget)

        assert warning is None  # ~34% usage

    def test_check_warning_yellow(self):
        """Returns yellow warning at 70-85%."""
        manager = ContextManager()
        budget = ContextBudget(
            total_tokens=100000,
            system_prompt_tokens=20000,
            input_data_tokens=50000,
            reserved_output_tokens=10000,
        )  # 80% usage

        warning = manager.check_warning(budget)

        assert warning is not None
        assert warning.level == WarningLevel.YELLOW

    def test_check_warning_orange(self):
        """Returns orange warning at 85-95%."""
        manager = ContextManager()
        budget = ContextBudget(
            total_tokens=100000,
            system_prompt_tokens=30000,
            input_data_tokens=50000,
            reserved_output_tokens=10000,
        )  # 90% usage

        warning = manager.check_warning(budget)

        assert warning is not None
        assert warning.level == WarningLevel.ORANGE

    def test_check_warning_red(self):
        """Returns red warning above 95%."""
        manager = ContextManager()
        budget = ContextBudget(
            total_tokens=100000,
            system_prompt_tokens=40000,
            input_data_tokens=50000,
            reserved_output_tokens=10000,
        )  # 100% usage

        warning = manager.check_warning(budget)

        assert warning is not None
        assert warning.level == WarningLevel.RED

    def test_can_fit_true(self):
        """Returns true when tokens can fit."""
        manager = ContextManager()
        budget = ContextBudget(
            total_tokens=200000,
            system_prompt_tokens=3000,
            input_data_tokens=50000,
            reserved_output_tokens=15000,
        )

        assert manager.can_fit(budget, 100000)

    def test_can_fit_false(self):
        """Returns false when tokens cannot fit."""
        manager = ContextManager()
        budget = ContextBudget(
            total_tokens=200000,
            system_prompt_tokens=3000,
            input_data_tokens=50000,
            reserved_output_tokens=15000,
        )

        assert not manager.can_fit(budget, 200000)

    def test_suggest_chunk_size(self):
        """Suggests appropriate chunk size."""
        manager = ContextManager()
        budget = ContextBudget(
            total_tokens=100000,
            system_prompt_tokens=5000,
            reserved_output_tokens=10000,
        )

        suggested = manager.suggest_chunk_size(budget, target_usage=70.0)

        assert suggested > 0
        assert suggested < 100000


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_check_context_usage_no_warning(self):
        """Returns None for low usage."""
        warning = check_context_usage(
            model="claude-sonnet-4-20250514",
            system_tokens=3000,
            input_tokens=50000,
        )

        assert warning is None

    def test_check_context_usage_with_warning(self):
        """Returns warning for high usage."""
        warning = check_context_usage(
            model="gpt-4",  # Only 8192 tokens
            system_tokens=3000,
            input_tokens=5000,
        )

        assert warning is not None


class TestModelContextWindows:
    """Tests for model context window data."""

    def test_anthropic_models_present(self):
        """Anthropic models are configured."""
        assert "claude-sonnet-4-20250514" in MODEL_CONTEXT_WINDOWS
        assert "claude-opus-4-20250514" in MODEL_CONTEXT_WINDOWS

    def test_openai_models_present(self):
        """OpenAI models are configured."""
        assert "gpt-4o" in MODEL_CONTEXT_WINDOWS
        assert "gpt-4" in MODEL_CONTEXT_WINDOWS

    def test_gemini_models_present(self):
        """Gemini models are configured."""
        assert "gemini-1.5-pro" in MODEL_CONTEXT_WINDOWS
        assert "gemini-1.5-flash" in MODEL_CONTEXT_WINDOWS
