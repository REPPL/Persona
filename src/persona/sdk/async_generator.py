"""
Async persona generator SDK class.

This module provides async versions of the SDK for integration
with async applications like FastAPI.
"""

import asyncio
from pathlib import Path
from typing import Any, Callable, Coroutine

from persona.sdk.models import (
    PersonaConfig,
    GenerationResultModel,
)
from persona.sdk.exceptions import (
    ConfigurationError,
    DataError,
    GenerationError,
    ProviderError,
)
from persona.sdk.generator import PersonaGenerator


class AsyncPersonaGenerator:
    """
    Async persona generator for integration with async applications.

    Provides async versions of all PersonaGenerator methods, enabling
    non-blocking generation and parallel processing.

    Example:
        import asyncio
        from persona.sdk import AsyncPersonaGenerator, PersonaConfig

        async def main():
            generator = AsyncPersonaGenerator(provider="anthropic")

            # Single generation
            result = await generator.agenerate("./interviews.csv")

            # Parallel generation
            results = await asyncio.gather(
                generator.agenerate("./data1.csv"),
                generator.agenerate("./data2.csv"),
                generator.agenerate("./data3.csv"),
            )

        asyncio.run(main())
    """

    def __init__(
        self,
        provider: str = "anthropic",
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """
        Initialise AsyncPersonaGenerator.

        Args:
            provider: LLM provider name (anthropic, openai, gemini).
            model: Model identifier. If None, uses provider default.
            api_key: API key. If None, uses environment variable.

        Raises:
            ConfigurationError: If provider is invalid.
        """
        # Validate provider using sync generator
        self._sync_generator = PersonaGenerator(
            provider=provider,
            model=model,
            api_key=api_key,
        )
        self._provider = provider
        self._model = model
        self._api_key = api_key
        self._progress_callback: Callable[[str, int, int], Coroutine[Any, Any, None]] | None = None

    @property
    def provider(self) -> str:
        """Return configured provider."""
        return self._provider

    @property
    def model(self) -> str | None:
        """Return configured model."""
        return self._model

    def set_progress_callback(
        self,
        callback: Callable[[str, int, int], Coroutine[Any, Any, None]],
    ) -> None:
        """
        Set an async callback for progress updates.

        The callback receives (message, current_step, total_steps).

        Args:
            callback: Async progress callback function.

        Example:
            async def on_progress(message, step, total):
                print(f"[{step}/{total}] {message}")
                await notify_ui(step, total)

            generator.set_progress_callback(on_progress)
        """
        self._progress_callback = callback

    async def agenerate(
        self,
        data_path: str | Path,
        config: PersonaConfig | None = None,
    ) -> GenerationResultModel:
        """
        Asynchronously generate personas from input data.

        This method runs the generation in a thread pool to avoid
        blocking the event loop, since the underlying LLM calls
        are currently synchronous.

        Args:
            data_path: Path to input data file or directory.
            config: Generation configuration. If None, uses defaults.

        Returns:
            GenerationResultModel with generated personas.

        Raises:
            DataError: If input data cannot be loaded.
            ProviderError: If LLM provider fails.
            GenerationError: If generation or parsing fails.

        Example:
            result = await generator.agenerate(
                "./interviews.csv",
                config=PersonaConfig(count=3)
            )
        """
        config = config or PersonaConfig()
        data_path = Path(data_path)

        # Validate data path
        if not data_path.exists():
            raise DataError(
                f"Data path not found: {data_path}",
                path=str(data_path),
            )

        # Run sync generation in thread pool
        loop = asyncio.get_event_loop()

        # Set up sync progress callback that calls async one
        if self._progress_callback:
            def sync_callback(message: str, step: int, total: int) -> None:
                # Schedule async callback
                asyncio.run_coroutine_threadsafe(
                    self._progress_callback(message, step, total),  # type: ignore
                    loop,
                )

            self._sync_generator.set_progress_callback(sync_callback)

        try:
            result = await loop.run_in_executor(
                None,
                lambda: self._sync_generator.generate(data_path, config),
            )
            return result
        except DataError:
            raise
        except ProviderError:
            raise
        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(
                f"Async generation failed: {e}",
                stage="async_wrapper",
            ) from e

    async def agenerate_batch(
        self,
        data_paths: list[str | Path],
        config: PersonaConfig | None = None,
        max_concurrent: int = 3,
    ) -> list[GenerationResultModel]:
        """
        Generate personas from multiple data sources in parallel.

        Limits concurrency to avoid overwhelming the API.

        Args:
            data_paths: List of paths to input data.
            config: Shared generation configuration.
            max_concurrent: Maximum concurrent generations.

        Returns:
            List of GenerationResultModel, one per data path.

        Example:
            results = await generator.agenerate_batch(
                ["./data1.csv", "./data2.csv", "./data3.csv"],
                config=PersonaConfig(count=3),
                max_concurrent=2,
            )
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_with_semaphore(path: str | Path) -> GenerationResultModel:
            async with semaphore:
                return await self.agenerate(path, config)

        tasks = [generate_with_semaphore(path) for path in data_paths]
        return await asyncio.gather(*tasks)

    async def aestimate_cost(
        self,
        data_path: str | Path,
        config: PersonaConfig | None = None,
    ) -> dict[str, Any]:
        """
        Asynchronously estimate the cost of generation.

        Args:
            data_path: Path to input data file or directory.
            config: Generation configuration.

        Returns:
            Dictionary with cost estimation details.

        Example:
            estimate = await generator.aestimate_cost("./interviews.csv")
            print(f"Estimated cost: ${estimate['estimated_cost']:.2f}")
        """
        config = config or PersonaConfig()
        data_path = Path(data_path)

        if not data_path.exists():
            raise DataError(
                f"Data path not found: {data_path}",
                path=str(data_path),
            )

        # Run sync estimation in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._sync_generator.estimate_cost(data_path, config),
        )

    def validate_config(self, config: PersonaConfig) -> list[str]:
        """
        Validate configuration (sync, no IO needed).

        Args:
            config: Configuration to validate.

        Returns:
            List of validation warnings.
        """
        return self._sync_generator.validate_config(config)


async def agenerate_parallel(
    data_paths: list[str | Path],
    provider: str = "anthropic",
    model: str | None = None,
    config: PersonaConfig | None = None,
    max_concurrent: int = 3,
) -> list[GenerationResultModel]:
    """
    Convenience function for parallel generation.

    Creates a generator and runs batch generation.

    Args:
        data_paths: List of paths to input data.
        provider: LLM provider name.
        model: Model identifier.
        config: Shared generation configuration.
        max_concurrent: Maximum concurrent generations.

    Returns:
        List of GenerationResultModel.

    Example:
        results = await agenerate_parallel(
            ["./data1.csv", "./data2.csv"],
            provider="anthropic",
            max_concurrent=2,
        )
    """
    generator = AsyncPersonaGenerator(provider=provider, model=model)
    return await generator.agenerate_batch(
        data_paths,
        config=config,
        max_concurrent=max_concurrent,
    )
