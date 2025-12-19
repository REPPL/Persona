"""
Persona generation pipeline.

This module provides the main orchestration class that combines
data loading, prompt rendering, LLM generation, and output parsing.
"""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path

from persona.core.data import DataLoader
from persona.core.generation.parser import ParseResult, Persona, PersonaParser
from persona.core.prompts import Workflow, WorkflowLoader
from persona.core.providers import LLMProvider, LLMResponse, ProviderFactory


@dataclass
class GenerationConfig:
    """
    Configuration for a persona generation run.

    Attributes:
        data_path: Path to input data file or directory.
        count: Number of personas to generate.
        provider: LLM provider name.
        model: Model identifier (optional, uses provider default).
        workflow: Workflow name or path.
        complexity: Generation complexity (simple, moderate, complex).
        detail_level: Output detail level (minimal, standard, detailed).
        include_reasoning: Whether to include LLM reasoning.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
    """

    data_path: str | Path
    count: int = 3
    provider: str = "anthropic"
    model: str | None = None
    workflow: str = "default"
    complexity: str = "moderate"
    detail_level: str = "standard"
    include_reasoning: bool = False
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class GenerationResult:
    """
    Result of a persona generation run.

    Attributes:
        personas: List of generated personas.
        reasoning: Optional LLM reasoning.
        input_tokens: Number of input tokens used.
        output_tokens: Number of output tokens used.
        model: Model used for generation.
        provider: Provider used.
        source_files: List of input files processed.
        url_sources: List of URL sources (when loading from URLs).
        prompt: The rendered prompt used.
        raw_response: The full LLM response.
        config: The generation configuration used.
    """

    personas: list[Persona]
    reasoning: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    provider: str = ""
    source_files: list[Path] = field(default_factory=list)
    url_sources: list = field(default_factory=list)  # List of URLSource objects
    prompt: str = ""
    raw_response: str = ""
    config: "GenerationConfig | None" = None


class GenerationPipeline:
    """
    Main pipeline for generating personas from data.

    Orchestrates the complete generation workflow:
    1. Load and combine input data
    2. Load workflow configuration
    3. Render prompt template
    4. Call LLM provider
    5. Parse and return personas

    Example:
        pipeline = GenerationPipeline()
        result = pipeline.generate(GenerationConfig(
            data_path="./interviews",
            count=3,
            provider="anthropic",
        ))
        for persona in result.personas:
            print(f"{persona.name}: {persona.goals}")
    """

    def __init__(
        self,
        data_loader: DataLoader | None = None,
        workflow_loader: WorkflowLoader | None = None,
        parser: PersonaParser | None = None,
    ) -> None:
        """
        Initialise the generation pipeline.

        Args:
            data_loader: Optional custom data loader.
            workflow_loader: Optional custom workflow loader.
            parser: Optional custom persona parser.
        """
        self._data_loader = data_loader or DataLoader()
        self._workflow_loader = workflow_loader or WorkflowLoader()
        self._parser = parser or PersonaParser()
        self._progress_callback: Callable[[str], None] | None = None

    def set_progress_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set a callback for progress updates.

        Args:
            callback: Function to call with progress messages.
        """
        self._progress_callback = callback

    def _progress(self, message: str) -> None:
        """Report progress if callback is set."""
        if self._progress_callback:
            self._progress_callback(message)

    def generate(self, config: GenerationConfig) -> GenerationResult:
        """
        Generate personas based on configuration.

        Args:
            config: Generation configuration.

        Returns:
            GenerationResult with generated personas.

        Raises:
            FileNotFoundError: If data path doesn't exist.
            ValueError: If no loadable data found.
            RuntimeError: If LLM generation fails.
        """
        self._progress("Loading input data...")
        data_content, source_files = self._load_data(config.data_path)

        self._progress("Loading workflow configuration...")
        workflow = self._load_workflow(config.workflow)

        self._progress("Rendering prompt...")
        prompt = self._render_prompt(workflow, config, data_content)

        self._progress(f"Generating with {config.provider}...")
        provider = self._create_provider(config)
        llm_response = self._call_llm(provider, prompt, config)

        self._progress("Parsing response...")
        parse_result = self._parse_response(llm_response.content)

        self._progress("Generation complete!")

        return GenerationResult(
            personas=parse_result.personas,
            reasoning=parse_result.reasoning,
            input_tokens=llm_response.input_tokens,
            output_tokens=llm_response.output_tokens,
            model=llm_response.model,
            provider=config.provider,
            source_files=source_files,
            prompt=prompt,
            raw_response=llm_response.content,
        )

    def _load_data(self, path: str | Path) -> tuple[str, list[Path]]:
        """Load and combine input data."""
        return self._data_loader.load_path(path)

    def _load_workflow(self, workflow: str) -> Workflow:
        """Load workflow configuration."""
        # Check if it's a file path
        if Path(workflow).exists():
            return self._workflow_loader.load(workflow)

        # Try as built-in workflow
        try:
            return self._workflow_loader.load_builtin(workflow)
        except ValueError:
            # Default to 'default' workflow
            return self._workflow_loader.load_builtin("default")

    def _render_prompt(
        self,
        workflow: Workflow,
        config: GenerationConfig,
        data: str,
    ) -> str:
        """Render the prompt template with variables."""
        return workflow.render_prompt(
            count=config.count,
            data=data,
            complexity=config.complexity,
            detail_level=config.detail_level,
            include_reasoning=config.include_reasoning,
        )

    def _create_provider(self, config: GenerationConfig) -> LLMProvider:
        """Create the LLM provider."""
        return ProviderFactory.create(config.provider)

    def _call_llm(
        self,
        provider: LLMProvider,
        prompt: str,
        config: GenerationConfig,
    ) -> LLMResponse:
        """Call the LLM provider."""
        return provider.generate(
            prompt=prompt,
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )

    def _parse_response(self, response: str) -> ParseResult:
        """Parse the LLM response."""
        return self._parser.parse(response)

    async def generate_async(self, config: GenerationConfig) -> GenerationResult:
        """
        Generate personas asynchronously based on configuration.

        Args:
            config: Generation configuration.

        Returns:
            GenerationResult with generated personas.

        Raises:
            FileNotFoundError: If data path doesn't exist.
            ValueError: If no loadable data found.
            RuntimeError: If LLM generation fails.
        """
        self._progress("Loading input data...")
        data_content, source_files = await self._load_data_async(config.data_path)

        self._progress("Loading workflow configuration...")
        workflow = await self._load_workflow_async(config.workflow)

        self._progress("Rendering prompt...")
        prompt = self._render_prompt(workflow, config, data_content)

        self._progress(f"Generating with {config.provider}...")
        provider = self._create_provider(config)
        llm_response = await self._call_llm_async(provider, prompt, config)

        self._progress("Parsing response...")
        parse_result = await self._parse_response_async(llm_response.content)

        self._progress("Generation complete!")

        return GenerationResult(
            personas=parse_result.personas,
            reasoning=parse_result.reasoning,
            input_tokens=llm_response.input_tokens,
            output_tokens=llm_response.output_tokens,
            model=llm_response.model,
            provider=config.provider,
            source_files=source_files,
            prompt=prompt,
            raw_response=llm_response.content,
        )

    async def _load_data_async(self, path: str | Path) -> tuple[str, list[Path]]:
        """Load and combine input data asynchronously."""
        return await self._data_loader.load_path_async(path)

    async def _load_workflow_async(self, workflow: str) -> Workflow:
        """Load workflow configuration asynchronously."""
        # Run synchronous workflow loading in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._load_workflow(workflow))

    async def _call_llm_async(
        self,
        provider: LLMProvider,
        prompt: str,
        config: GenerationConfig,
    ) -> LLMResponse:
        """Call the LLM provider asynchronously."""
        return await provider.generate_async(
            prompt=prompt,
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )

    async def _parse_response_async(self, response: str) -> ParseResult:
        """Parse the LLM response asynchronously."""
        # Run synchronous parsing in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._parser.parse(response))

    async def generate_batch_async(
        self,
        configs: list[GenerationConfig],
        max_concurrent: int = 3,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> list[GenerationResult]:
        """
        Generate multiple persona sets concurrently.

        Args:
            configs: List of generation configurations.
            max_concurrent: Maximum concurrent generations.
            progress_callback: Optional async callback(completed, total).

        Returns:
            List of GenerationResult objects.

        Example:
            results = await pipeline.generate_batch_async(
                [config1, config2, config3],
                max_concurrent=2,
            )
        """
        from persona.core.async_utils import gather_with_concurrency

        total = len(configs)
        completed = 0

        async def generate_with_progress(cfg: GenerationConfig) -> GenerationResult:
            nonlocal completed
            result = await self.generate_async(cfg)
            completed += 1
            if progress_callback:
                await progress_callback(completed, total)
            return result

        tasks = [generate_with_progress(cfg) for cfg in configs]
        return await gather_with_concurrency(max_concurrent, *tasks)
