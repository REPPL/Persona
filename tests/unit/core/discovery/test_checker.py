"""Tests for model availability checking (F-056)."""


from persona.core.discovery.checker import (
    DEPRECATED_MODELS,
    MODEL_ALTERNATIVES,
    ModelAvailability,
    ModelChecker,
    ModelStatus,
    check_model,
    warn_if_deprecated,
)


class TestModelStatus:
    """Tests for ModelStatus enum."""

    def test_all_statuses_defined(self):
        """All expected statuses are defined."""
        assert ModelStatus.AVAILABLE
        assert ModelStatus.DEPRECATED
        assert ModelStatus.UNAVAILABLE
        assert ModelStatus.UNKNOWN


class TestModelAvailability:
    """Tests for ModelAvailability dataclass."""

    def test_is_available_when_available(self):
        """Is available when status is AVAILABLE."""
        availability = ModelAvailability(
            model="gpt-4o",
            provider="openai",
            status=ModelStatus.AVAILABLE,
        )
        assert availability.is_available

    def test_is_available_when_deprecated(self):
        """Is available when status is DEPRECATED."""
        availability = ModelAvailability(
            model="gpt-4-0314",
            provider="openai",
            status=ModelStatus.DEPRECATED,
        )
        assert availability.is_available

    def test_not_available_when_unavailable(self):
        """Not available when status is UNAVAILABLE."""
        availability = ModelAvailability(
            model="nonexistent",
            provider="openai",
            status=ModelStatus.UNAVAILABLE,
        )
        assert not availability.is_available

    def test_is_deprecated(self):
        """Is deprecated when status is DEPRECATED."""
        availability = ModelAvailability(
            model="gpt-4-0314",
            provider="openai",
            status=ModelStatus.DEPRECATED,
        )
        assert availability.is_deprecated

    def test_to_dict(self):
        """Converts to dictionary."""
        availability = ModelAvailability(
            model="gpt-4o",
            provider="openai",
            status=ModelStatus.AVAILABLE,
            message="Model verified",
            alternatives=["gpt-4o-mini"],
        )

        data = availability.to_dict()
        assert data["model"] == "gpt-4o"
        assert data["provider"] == "openai"
        assert data["status"] == "available"
        assert "checked_at" in data


class TestModelChecker:
    """Tests for ModelChecker."""

    def test_check_known_deprecated_model(self):
        """Identifies known deprecated model."""
        checker = ModelChecker()
        result = checker.check("claude-2.0", "anthropic")

        assert result.status == ModelStatus.DEPRECATED
        assert result.is_deprecated
        assert result.replacement is not None

    def test_check_caches_result(self):
        """Caches check result."""
        checker = ModelChecker()

        # First check
        result1 = checker.check("gpt-4o", "openai")

        # Second check (should be cached)
        result2 = checker.check("gpt-4o", "openai")

        assert result1.checked_at == result2.checked_at

    def test_check_force_refresh(self):
        """Force refresh bypasses cache."""
        checker = ModelChecker()

        # First check
        result1 = checker.check("gpt-4o", "openai")

        # Force refresh
        result2 = checker.check("gpt-4o", "openai", force_refresh=True)

        # Timestamps should differ
        assert result1.checked_at != result2.checked_at

    def test_check_multiple(self):
        """Checks multiple models."""
        checker = ModelChecker()
        results = checker.check_multiple(
            [
                ("gpt-4o", "openai"),
                ("claude-2.0", "anthropic"),
            ]
        )

        assert len(results) == 2
        assert "openai:gpt-4o" in results
        assert "anthropic:claude-2.0" in results

    def test_get_alternatives(self):
        """Returns alternatives for model."""
        checker = ModelChecker()
        alternatives = checker.get_alternatives("claude-2.0", "anthropic")

        assert len(alternatives) >= 1

    def test_get_alternatives_deprecated_replacement(self):
        """Returns replacement for deprecated model."""
        checker = ModelChecker()
        alternatives = checker.get_alternatives("claude-2.0", "anthropic")

        # Should include the replacement
        assert DEPRECATED_MODELS["claude-2.0"]["replacement"] in alternatives

    def test_is_deprecated(self):
        """Quick deprecation check."""
        checker = ModelChecker()

        assert checker.is_deprecated("claude-2.0")
        assert not checker.is_deprecated("claude-sonnet-4-20250514")

    def test_get_deprecation_info(self):
        """Gets deprecation info."""
        checker = ModelChecker()
        info = checker.get_deprecation_info("claude-2.0")

        assert info is not None
        assert "replacement" in info
        assert "date" in info

    def test_get_deprecation_info_not_deprecated(self):
        """Returns None for non-deprecated model."""
        checker = ModelChecker()
        info = checker.get_deprecation_info("gpt-4o")

        assert info is None

    def test_suggest_model(self):
        """Suggests model for provider."""
        checker = ModelChecker()

        suggestion = checker.suggest_model("anthropic")
        assert suggestion is not None

        suggestion = checker.suggest_model("openai")
        assert suggestion is not None

    def test_suggest_model_unknown_provider(self):
        """Returns None for unknown provider."""
        checker = ModelChecker()
        suggestion = checker.suggest_model("unknown-provider")

        assert suggestion is None

    def test_clear_cache(self):
        """Clears availability cache."""
        checker = ModelChecker()

        # Populate cache
        checker.check("gpt-4o", "openai")
        assert len(checker._cache) > 0

        checker.clear_cache()
        assert len(checker._cache) == 0

    def test_get_cached_status(self):
        """Gets cached status without refresh."""
        checker = ModelChecker()

        # No cache yet
        cached = checker.get_cached_status("gpt-4o", "openai")
        assert cached is None

        # Populate cache
        checker.check("gpt-4o", "openai")

        # Now should have cached status
        cached = checker.get_cached_status("gpt-4o", "openai")
        assert cached is not None


class TestDeprecatedModels:
    """Tests for DEPRECATED_MODELS constant."""

    def test_anthropic_models(self):
        """Anthropic deprecated models are listed."""
        assert "claude-2.0" in DEPRECATED_MODELS
        assert "claude-2.1" in DEPRECATED_MODELS
        assert "claude-instant-1.2" in DEPRECATED_MODELS

    def test_openai_models(self):
        """OpenAI deprecated models are listed."""
        assert "gpt-3.5-turbo-0301" in DEPRECATED_MODELS
        assert "gpt-4-0314" in DEPRECATED_MODELS

    def test_gemini_models(self):
        """Gemini deprecated models are listed."""
        assert "gemini-pro" in DEPRECATED_MODELS

    def test_all_have_replacement(self):
        """All deprecated models have replacement."""
        for model, info in DEPRECATED_MODELS.items():
            assert "replacement" in info, f"{model} missing replacement"

    def test_all_have_date(self):
        """All deprecated models have date."""
        for model, info in DEPRECATED_MODELS.items():
            assert "date" in info, f"{model} missing date"


class TestModelAlternatives:
    """Tests for MODEL_ALTERNATIVES constant."""

    def test_anthropic_alternatives(self):
        """Anthropic has alternatives."""
        assert "anthropic" in MODEL_ALTERNATIVES
        assert len(MODEL_ALTERNATIVES["anthropic"]) > 0

    def test_openai_alternatives(self):
        """OpenAI has alternatives."""
        assert "openai" in MODEL_ALTERNATIVES
        assert len(MODEL_ALTERNATIVES["openai"]) > 0

    def test_gemini_alternatives(self):
        """Gemini has alternatives."""
        assert "gemini" in MODEL_ALTERNATIVES
        assert len(MODEL_ALTERNATIVES["gemini"]) > 0


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_check_model(self):
        """check_model returns availability."""
        result = check_model("gpt-4o", "openai")
        assert isinstance(result, ModelAvailability)

    def test_warn_if_deprecated_deprecated(self):
        """warn_if_deprecated returns warning for deprecated model."""
        warning = warn_if_deprecated("claude-2.0", "anthropic")

        assert warning is not None
        assert "deprecated" in warning.lower()
        assert "claude-2.0" in warning

    def test_warn_if_deprecated_not_deprecated(self):
        """warn_if_deprecated returns None for non-deprecated model."""
        warning = warn_if_deprecated("gpt-4o", "openai")

        assert warning is None
