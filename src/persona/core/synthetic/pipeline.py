"""
Synthetic data generation pipeline.

This module provides the SyntheticPipeline class that orchestrates
privacy-preserving synthetic data generation from sensitive sources
using local LLMs.
"""

import csv
import json
import time
from pathlib import Path
from typing import Any

import yaml

from persona.core.providers import ProviderFactory
from persona.core.synthetic.analyser import DataAnalyser
from persona.core.synthetic.models import (
    DataSchema,
    GenerationConfig,
    SyntheticResult,
)
from persona.core.synthetic.validator import SyntheticValidator


class SyntheticPipeline:
    """
    Privacy-preserving synthetic data generation pipeline.

    Generates synthetic data from sensitive sources using local LLMs,
    preserving statistical properties while removing PII.

    IMPORTANT: Named SyntheticPipeline (not SyntheticGenerator) to avoid
    confusion with the existing SyntheticDataGenerator class that creates
    demo/test data.

    Example:
        pipeline = SyntheticPipeline(provider="ollama", model="qwen2.5:72b")
        result = pipeline.synthesise(
            input_path="interviews.csv",
            output_path="synthetic.csv",
            count=100
        )
    """

    def __init__(
        self,
        provider: str = "ollama",
        model: str | None = None,
    ) -> None:
        """
        Initialise the synthetic data pipeline.

        Args:
            provider: LLM provider to use (ollama, anthropic, openai, gemini).
            model: Specific model to use (if None, uses provider default).
        """
        self.provider_name = provider
        self.model_name = model
        self.analyser = DataAnalyser()
        self.validator = SyntheticValidator()

        # Initialise provider
        self._provider = ProviderFactory.create(provider)

        # Set model if specified
        if model:
            self.model_name = model
        else:
            self.model_name = self._provider.default_model

    def synthesise(
        self,
        input_path: Path | str,
        output_path: Path | str,
        count: int = 100,
        preserve_schema: bool = True,
        preserve_distribution: bool = True,
        batch_size: int = 10,
        temperature: float = 0.7,
        validate: bool = True,
    ) -> SyntheticResult:
        """
        Generate synthetic data from sensitive source.

        Args:
            input_path: Path to original data file (CSV, JSON, YAML).
            output_path: Path to save synthetic data.
            count: Number of synthetic records to generate.
            preserve_schema: Whether to match original schema exactly.
            preserve_distribution: Whether to preserve statistical distribution.
            batch_size: Number of records to generate per API call.
            temperature: Temperature for LLM generation (0.0-1.0).
            validate: Whether to validate output quality.

        Returns:
            SyntheticResult with generation details and validation.

        Raises:
            FileNotFoundError: If input file doesn't exist.
            ValueError: If input format is unsupported or data is invalid.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        start_time = time.time()

        # Step 1: Analyse original data
        schema = self.analyser.analyse_file(input_path)

        # Step 2: Generate synthetic data
        synthetic_data = self._generate_records(
            schema=schema,
            count=count,
            preserve_distribution=preserve_distribution,
            batch_size=batch_size,
            temperature=temperature,
        )

        # Step 3: Save synthetic data
        self._save_data(synthetic_data, output_path, schema.format)

        generation_time = time.time() - start_time

        # Step 4: Validate if requested
        validation_result = None
        if validate:
            validation_result = self.validator.validate(
                original_path=input_path,
                synthetic_path=output_path,
            )

        return SyntheticResult(
            input_path=input_path,
            output_path=output_path,
            data_schema=schema,
            row_count=len(synthetic_data),
            model=self.model_name,
            provider=self.provider_name,
            generation_time=generation_time,
            validation=validation_result,
            metadata={
                "preserve_schema": preserve_schema,
                "preserve_distribution": preserve_distribution,
                "batch_size": batch_size,
                "temperature": temperature,
            },
        )

    def _generate_records(
        self,
        schema: DataSchema,
        count: int,
        preserve_distribution: bool,
        batch_size: int,
        temperature: float,
    ) -> list[dict[str, Any]]:
        """Generate synthetic records using LLM."""
        all_records = []
        batches = (count + batch_size - 1) // batch_size  # Ceiling division

        for batch_idx in range(batches):
            # Determine how many records for this batch
            remaining = count - len(all_records)
            batch_count = min(batch_size, remaining)

            # Build generation prompt
            prompt = self._build_generation_prompt(
                schema=schema,
                count=batch_count,
                preserve_distribution=preserve_distribution,
            )

            # Generate with LLM
            response = self._provider.generate(
                prompt=prompt,
                model=self.model_name,
                temperature=temperature,
                max_tokens=4096,
            )

            # Parse response
            batch_records = self._parse_llm_response(response.content, schema)

            all_records.extend(batch_records)

            # Stop if we've generated enough
            if len(all_records) >= count:
                break

        # Trim to exact count
        return all_records[:count]

    def _build_generation_prompt(
        self,
        schema: DataSchema,
        count: int,
        preserve_distribution: bool,
    ) -> str:
        """Build prompt for LLM to generate synthetic data."""
        prompt_parts = [
            "Generate synthetic data that matches the following schema and statistical properties.",
            "",
            "CRITICAL REQUIREMENTS:",
            "1. DO NOT include any personally identifiable information (PII)",
            "2. Generate realistic but entirely fictional data",
            "3. Match the schema exactly",
        ]

        if preserve_distribution:
            prompt_parts.append("4. Preserve the statistical distributions described below")

        prompt_parts.extend([
            "",
            "# Schema Definition",
            "",
        ])

        # Add column definitions
        for col in schema.columns:
            prompt_parts.append(f"## Column: {col.column_name}")
            prompt_parts.append(f"- Type: {col.column_type}")
            prompt_parts.append(f"- Unique values: {col.unique_count}")

            if col.null_count > 0:
                null_rate = col.null_count / schema.row_count
                prompt_parts.append(f"- Null rate: {null_rate:.1%}")

            if col.sample_values:
                prompt_parts.append(f"- Example values: {', '.join(str(v) for v in col.sample_values[:3])}")

            if col.categorical_distribution and preserve_distribution:
                prompt_parts.append("- Distribution:")
                # Show top 5 categories
                sorted_dist = sorted(
                    col.categorical_distribution.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]
                for value, freq in sorted_dist:
                    percentage = (freq / schema.row_count) * 100
                    prompt_parts.append(f"  - {value}: {percentage:.1f}%")

            if col.numeric_stats:
                prompt_parts.append("- Numeric range:")
                prompt_parts.append(f"  - Min: {col.numeric_stats['min']:.2f}")
                prompt_parts.append(f"  - Max: {col.numeric_stats['max']:.2f}")
                prompt_parts.append(f"  - Mean: {col.numeric_stats['mean']:.2f}")
                prompt_parts.append(f"  - Std: {col.numeric_stats['std']:.2f}")

            prompt_parts.append("")

        prompt_parts.extend([
            f"Generate {count} synthetic records as a JSON array.",
            "Each record should be an object with the column names as keys.",
            "Ensure NO PII is included - use only fictional data.",
            "",
            "Format your response as valid JSON only, no additional text:",
            "[",
            "  {",
            '    "' + schema.columns[0].column_name + '": "value",',
            "    ...",
            "  },",
            "  ...",
            "]",
        ])

        return "\n".join(prompt_parts)

    def _parse_llm_response(
        self,
        response: str,
        schema: DataSchema,
    ) -> list[dict[str, Any]]:
        """Parse LLM response into structured records."""
        # Try to extract JSON from response
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```"):
            # Find start and end of code block
            lines = response.split("\n")
            start_idx = 0
            end_idx = len(lines)

            for i, line in enumerate(lines):
                if line.strip().startswith("```"):
                    if start_idx == 0:
                        start_idx = i + 1
                    else:
                        end_idx = i
                        break

            response = "\n".join(lines[start_idx:end_idx])

        # Try to parse as JSON
        try:
            data = json.loads(response)

            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Single record, wrap in list
                return [data]
            else:
                raise ValueError("Response is not a list or dict")

        except json.JSONDecodeError as e:
            # Fallback: try to find JSON array in text
            start_idx = response.find("[")
            end_idx = response.rfind("]")

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx : end_idx + 1]
                try:
                    data = json.loads(json_str)
                    return data if isinstance(data, list) else [data]
                except json.JSONDecodeError:
                    pass

            # If all parsing fails, return empty list
            # TODO: Add proper logging/warning
            return []

    def _save_data(
        self,
        data: list[dict[str, Any]],
        output_path: Path,
        format_type: str,
    ) -> None:
        """Save synthetic data to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format_type == "csv":
            self._save_csv(data, output_path)
        elif format_type == "json":
            self._save_json(data, output_path)
        elif format_type == "yaml":
            self._save_yaml(data, output_path)
        else:
            # Default to CSV
            self._save_csv(data, output_path)

    def _save_csv(self, data: list[dict[str, Any]], output_path: Path) -> None:
        """Save data as CSV."""
        if not data:
            return

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def _save_json(self, data: list[dict[str, Any]], output_path: Path) -> None:
        """Save data as JSON."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _save_yaml(self, data: list[dict[str, Any]], output_path: Path) -> None:
        """Save data as YAML."""
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
