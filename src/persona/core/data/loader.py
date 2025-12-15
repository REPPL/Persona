"""
Base data loader and file discovery functionality.

This module provides the core DataLoader class that handles loading
qualitative research data from various file formats.
"""

import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import tiktoken


class FormatLoader(ABC):
    """Abstract base class for format-specific loaders."""

    @property
    @abstractmethod
    def extensions(self) -> list[str]:
        """Return list of supported file extensions."""
        ...

    @abstractmethod
    def load(self, path: Path) -> str:
        """
        Load content from a file.

        Args:
            path: Path to the file to load.

        Returns:
            String content of the file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file cannot be parsed.
        """
        ...

    def can_load(self, path: Path) -> bool:
        """Check if this loader can handle the given file."""
        return path.suffix.lower() in self.extensions


class DataLoader:
    """
    Main data loader that discovers and combines files from various formats.

    Supports loading from single files or directories, combining content
    with clear separators for LLM processing.

    Example:
        loader = DataLoader()
        content, files = loader.load_path("./data")
        token_count = loader.count_tokens(content)
    """

    # File separator used when combining multiple files
    FILE_SEPARATOR = "\n\n---\n\n"

    # Default encoding model for token counting
    DEFAULT_ENCODING = "cl100k_base"

    def __init__(self) -> None:
        """Initialise the data loader with format-specific handlers."""
        from persona.core.data.formats import (
            CSVLoader,
            HTMLLoader,
            JSONLoader,
            MarkdownLoader,
            OrgLoader,
            TextLoader,
            YAMLLoader,
        )

        self._loaders: list[FormatLoader] = [
            CSVLoader(),
            HTMLLoader(),
            JSONLoader(),
            MarkdownLoader(),
            OrgLoader(),
            TextLoader(),
            YAMLLoader(),
        ]
        self._encoding: tiktoken.Encoding | None = None

    @property
    def supported_extensions(self) -> list[str]:
        """Return all supported file extensions."""
        extensions = []
        for loader in self._loaders:
            extensions.extend(loader.extensions)
        return extensions

    def discover_files(self, path: Path, recursive: bool = True) -> list[Path]:
        """
        Discover all loadable files in a path.

        Args:
            path: File or directory path.
            recursive: Whether to search subdirectories (default: True).

        Returns:
            List of discovered file paths, sorted alphabetically.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if path.is_file():
            return [path] if self._can_load(path) else []

        # Directory: find all supported files
        files = []
        pattern = "**/*" if recursive else "*"

        for file_path in path.glob(pattern):
            if file_path.is_file() and self._can_load(file_path):
                files.append(file_path)

        return sorted(files)

    def load_file(self, path: Path) -> str:
        """
        Load content from a single file.

        Args:
            path: Path to the file.

        Returns:
            String content of the file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If no loader supports the file format.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {path}")

        loader = self._get_loader(path)
        if loader is None:
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {', '.join(self.supported_extensions)}"
            )

        return loader.load(path)

    def load_path(
        self,
        path: str | Path,
        recursive: bool = True,
    ) -> tuple[str, list[Path]]:
        """
        Load and combine content from a file or directory.

        Args:
            path: File or directory path.
            recursive: Whether to search subdirectories (default: True).

        Returns:
            Tuple of (combined content, list of loaded files).

        Raises:
            FileNotFoundError: If the path does not exist.
            ValueError: If no loadable files are found.
        """
        path = Path(path)
        files = self.discover_files(path, recursive=recursive)

        if not files:
            raise ValueError(
                f"No loadable files found in: {path}. "
                f"Supported formats: {', '.join(self.supported_extensions)}"
            )

        contents = []
        for file_path in files:
            try:
                file_content = self.load_file(file_path)
                # Add file header for context
                header = f"# Source: {file_path.name}\n\n"
                contents.append(header + file_content)
            except Exception as e:
                # Skip files that fail to load, but log the error
                # TODO: Add proper logging
                pass

        if not contents:
            raise ValueError(f"Failed to load any files from: {path}")

        combined = self.FILE_SEPARATOR.join(contents)
        return combined, files

    def count_tokens(self, text: str, model: str | None = None) -> int:
        """
        Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for.
            model: Optional model name for encoding selection.

        Returns:
            Number of tokens in the text.
        """
        if self._encoding is None:
            try:
                if model:
                    self._encoding = tiktoken.encoding_for_model(model)
                else:
                    self._encoding = tiktoken.get_encoding(self.DEFAULT_ENCODING)
            except Exception:
                # Fallback to default encoding
                self._encoding = tiktoken.get_encoding(self.DEFAULT_ENCODING)

        return len(self._encoding.encode(text))

    def validate_content(self, content: str, min_length: int = 100) -> bool:
        """
        Validate that content meets minimum requirements.

        Args:
            content: Content to validate.
            min_length: Minimum character length (default: 100).

        Returns:
            True if content is valid, False otherwise.
        """
        if not content or not content.strip():
            return False

        if len(content.strip()) < min_length:
            return False

        return True

    def _can_load(self, path: Path) -> bool:
        """Check if any loader can handle this file."""
        return any(loader.can_load(path) for loader in self._loaders)

    def _get_loader(self, path: Path) -> FormatLoader | None:
        """Get the appropriate loader for a file."""
        for loader in self._loaders:
            if loader.can_load(path):
                return loader
        return None

    async def load_file_async(self, path: Path) -> str:
        """
        Load content from a single file asynchronously.

        Args:
            path: Path to the file.

        Returns:
            String content of the file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If no loader supports the file format.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {path}")

        loader = self._get_loader(path)
        if loader is None:
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {', '.join(self.supported_extensions)}"
            )

        # Run synchronous loader in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: loader.load(path))

    async def load_path_async(
        self,
        path: str | Path,
        recursive: bool = True,
    ) -> tuple[str, list[Path]]:
        """
        Load and combine content from a file or directory asynchronously.

        Args:
            path: File or directory path.
            recursive: Whether to search subdirectories (default: True).

        Returns:
            Tuple of (combined content, list of loaded files).

        Raises:
            FileNotFoundError: If the path does not exist.
            ValueError: If no loadable files are found.
        """
        path = Path(path)
        files = self.discover_files(path, recursive=recursive)

        if not files:
            raise ValueError(
                f"No loadable files found in: {path}. "
                f"Supported formats: {', '.join(self.supported_extensions)}"
            )

        # Load all files concurrently
        async def load_with_header(file_path: Path) -> str | None:
            try:
                file_content = await self.load_file_async(file_path)
                # Add file header for context
                header = f"# Source: {file_path.name}\n\n"
                return header + file_content
            except Exception:
                # Skip files that fail to load
                # TODO: Add proper logging
                return None

        # Load files concurrently
        tasks = [load_with_header(file_path) for file_path in files]
        contents = await asyncio.gather(*tasks)

        # Filter out None values (failed loads)
        valid_contents = [c for c in contents if c is not None]

        if not valid_contents:
            raise ValueError(f"Failed to load any files from: {path}")

        combined = self.FILE_SEPARATOR.join(valid_contents)
        return combined, files
