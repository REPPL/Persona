"""
Context window awareness (F-062).

Provides context budget management and warnings for LLM interactions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WarningLevel(Enum):
    """Warning severity levels."""
    
    GREEN = "green"       # < 70% usage
    YELLOW = "yellow"     # 70-85% usage
    ORANGE = "orange"     # 85-95% usage
    RED = "red"           # > 95% usage


@dataclass
class ContextBudget:
    """
    Context budget breakdown.
    
    Tracks how context window is being used.
    """
    
    total_tokens: int
    system_prompt_tokens: int = 0
    input_data_tokens: int = 0
    reserved_output_tokens: int = 0
    
    @property
    def used_tokens(self) -> int:
        """Total tokens used (excluding reserved)."""
        return self.system_prompt_tokens + self.input_data_tokens
    
    @property
    def available_tokens(self) -> int:
        """Tokens available for additional input."""
        return self.total_tokens - self.used_tokens - self.reserved_output_tokens
    
    @property
    def usage_percentage(self) -> float:
        """Percentage of context used."""
        if self.total_tokens == 0:
            return 0.0
        return (self.used_tokens + self.reserved_output_tokens) / self.total_tokens * 100
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_tokens": self.total_tokens,
            "system_prompt_tokens": self.system_prompt_tokens,
            "input_data_tokens": self.input_data_tokens,
            "reserved_output_tokens": self.reserved_output_tokens,
            "used_tokens": self.used_tokens,
            "available_tokens": self.available_tokens,
            "usage_percentage": round(self.usage_percentage, 1),
        }


@dataclass
class ContextWarning:
    """
    Warning about context usage.
    
    Provides actionable suggestions when approaching limits.
    """
    
    level: WarningLevel
    message: str
    usage_percentage: float
    budget: ContextBudget
    suggestions: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "level": self.level.value,
            "message": self.message,
            "usage_percentage": round(self.usage_percentage, 1),
            "budget": self.budget.to_dict(),
            "suggestions": self.suggestions,
        }


# Model context windows (tokens)
MODEL_CONTEXT_WINDOWS: dict[str, int] = {
    # Anthropic
    "claude-opus-4-20250514": 200000,
    "claude-sonnet-4-20250514": 200000,
    "claude-3-5-sonnet-20241022": 200000,
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 200000,
    "claude-3-haiku-20240307": 200000,
    # OpenAI
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4": 8192,
    "gpt-3.5-turbo": 16385,
    "o1-preview": 128000,
    "o1-mini": 128000,
    # Google
    "gemini-1.5-pro": 2000000,
    "gemini-1.5-flash": 1000000,
    "gemini-2.0-flash-exp": 1000000,
}

# Default output reservation (tokens)
DEFAULT_OUTPUT_RESERVATION: dict[str, int] = {
    "anthropic": 15000,
    "openai": 10000,
    "gemini": 15000,
}


class ContextManager:
    """
    Manages context window budgets.
    
    Tracks token usage and provides warnings when approaching limits.
    
    Example:
        >>> manager = ContextManager()
        >>> budget = manager.calculate_budget(
        ...     model="claude-sonnet-4-20250514",
        ...     system_tokens=3000,
        ...     input_tokens=150000,
        ... )
        >>> warning = manager.check_warning(budget)
        >>> if warning:
        ...     print(warning.message)
    """
    
    # Warning thresholds (percentage)
    THRESHOLDS = {
        WarningLevel.GREEN: 70.0,
        WarningLevel.YELLOW: 85.0,
        WarningLevel.ORANGE: 95.0,
    }
    
    def __init__(
        self,
        custom_windows: dict[str, int] | None = None,
        output_reservation: int | None = None,
    ):
        """
        Initialise the context manager.
        
        Args:
            custom_windows: Custom context windows by model.
            output_reservation: Default output token reservation.
        """
        self._context_windows = {**MODEL_CONTEXT_WINDOWS}
        if custom_windows:
            self._context_windows.update(custom_windows)
        self._default_reservation = output_reservation or 15000
    
    def get_context_window(self, model: str) -> int:
        """
        Get context window size for a model.
        
        Args:
            model: Model identifier.
        
        Returns:
            Context window size in tokens.
        """
        # Direct match
        if model in self._context_windows:
            return self._context_windows[model]
        
        # Prefix match
        for key, window in self._context_windows.items():
            if model.startswith(key.split("-")[0]):
                return window
        
        # Default
        return 128000
    
    def calculate_budget(
        self,
        model: str,
        system_tokens: int = 0,
        input_tokens: int = 0,
        output_reservation: int | None = None,
    ) -> ContextBudget:
        """
        Calculate context budget.
        
        Args:
            model: Model identifier.
            system_tokens: Tokens used by system prompt.
            input_tokens: Tokens used by input data.
            output_reservation: Tokens reserved for output.
        
        Returns:
            ContextBudget instance.
        """
        total = self.get_context_window(model)
        reserved = output_reservation or self._default_reservation
        
        return ContextBudget(
            total_tokens=total,
            system_prompt_tokens=system_tokens,
            input_data_tokens=input_tokens,
            reserved_output_tokens=reserved,
        )
    
    def check_warning(
        self,
        budget: ContextBudget,
        model: str | None = None,
    ) -> ContextWarning | None:
        """
        Check if a warning should be displayed.
        
        Args:
            budget: Context budget to check.
            model: Optional model name for suggestions.
        
        Returns:
            ContextWarning if usage is concerning, None otherwise.
        """
        usage = budget.usage_percentage
        
        if usage < self.THRESHOLDS[WarningLevel.GREEN]:
            return None
        
        # Determine level
        if usage >= self.THRESHOLDS[WarningLevel.ORANGE]:
            level = WarningLevel.RED
            message = "Context window nearly exhausted"
        elif usage >= self.THRESHOLDS[WarningLevel.YELLOW]:
            level = WarningLevel.ORANGE
            message = "Context usage very high"
        else:
            level = WarningLevel.YELLOW
            message = "Context usage approaching limit"
        
        # Generate suggestions
        suggestions = self._generate_suggestions(budget, model, level)
        
        return ContextWarning(
            level=level,
            message=message,
            usage_percentage=usage,
            budget=budget,
            suggestions=suggestions,
        )
    
    def can_fit(
        self,
        budget: ContextBudget,
        additional_tokens: int,
    ) -> bool:
        """
        Check if additional tokens can fit in the budget.
        
        Args:
            budget: Current budget.
            additional_tokens: Tokens to add.
        
        Returns:
            True if tokens can fit.
        """
        return budget.available_tokens >= additional_tokens
    
    def suggest_chunk_size(
        self,
        budget: ContextBudget,
        target_usage: float = 70.0,
    ) -> int:
        """
        Suggest maximum chunk size to stay within target usage.
        
        Args:
            budget: Current budget (excluding input_data_tokens).
            target_usage: Target usage percentage.
        
        Returns:
            Maximum tokens for input data.
        """
        available_for_input = (
            budget.total_tokens * (target_usage / 100)
            - budget.system_prompt_tokens
            - budget.reserved_output_tokens
        )
        return max(0, int(available_for_input))
    
    def _generate_suggestions(
        self,
        budget: ContextBudget,
        model: str | None,
        level: WarningLevel,
    ) -> list[str]:
        """Generate suggestions for reducing context usage."""
        suggestions = []
        
        # Suggest larger model
        if model and level in (WarningLevel.ORANGE, WarningLevel.RED):
            larger_models = self._find_larger_models(model, budget.total_tokens)
            if larger_models:
                suggestions.append(
                    f"Use a larger context model ({', '.join(larger_models)})"
                )
        
        # Always suggest chunking
        if budget.input_data_tokens > budget.total_tokens * 0.5:
            suggestions.append("Split data into multiple runs")
        
        # Suggest summarisation for very large inputs
        if budget.input_data_tokens > 100000:
            suggestions.append("Summarise input data first")
        
        # Reduce output reservation
        if budget.reserved_output_tokens > 20000:
            suggestions.append("Reduce output token reservation")
        
        return suggestions
    
    def _find_larger_models(
        self,
        current_model: str,
        current_window: int,
    ) -> list[str]:
        """Find models with larger context windows."""
        larger = []
        for model, window in self._context_windows.items():
            if window > current_window * 1.5:  # At least 50% larger
                larger.append(model)
        return larger[:3]  # Return top 3


def check_context_usage(
    model: str,
    system_tokens: int,
    input_tokens: int,
) -> ContextWarning | None:
    """
    Convenience function to check context usage.
    
    Args:
        model: Model identifier.
        system_tokens: System prompt tokens.
        input_tokens: Input data tokens.
    
    Returns:
        ContextWarning if concerning, None otherwise.
    """
    manager = ContextManager()
    budget = manager.calculate_budget(model, system_tokens, input_tokens)
    return manager.check_warning(budget, model)
