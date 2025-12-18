"""
Data analysis for synthetic data generation.

This module provides the DataAnalyser class that extracts schema,
statistical distributions, and patterns from input data to guide
synthetic data generation.
"""

import csv
import json
from pathlib import Path
from typing import Any

import yaml

from persona.core.synthetic.models import (
    ColumnType,
    DataSchema,
    DistributionStats,
)


class DataAnalyser:
    """
    Analyses input data to extract schema and distributions.

    Extracts schema (column names, types), statistical distributions
    (categorical frequencies, numeric ranges), and relationships to
    inform synthetic data generation.

    Example:
        analyser = DataAnalyser()
        schema = analyser.analyse_file("interviews.csv")
        print(f"Schema: {schema.column_names()}")
    """

    def __init__(self) -> None:
        """Initialise the data analyser."""
        pass

    def analyse_file(self, file_path: Path | str) -> DataSchema:
        """
        Analyse a data file and extract schema.

        Args:
            file_path: Path to CSV, JSON, or YAML file.

        Returns:
            DataSchema with column information and distributions.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file format is unsupported.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine format and load data
        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            data = self._load_csv(file_path)
            format_type = "csv"
        elif suffix == ".json":
            data = self._load_json(file_path)
            format_type = "json"
        elif suffix in [".yaml", ".yml"]:
            data = self._load_yaml(file_path)
            format_type = "yaml"
        else:
            raise ValueError(
                f"Unsupported file format: {suffix}. "
                "Supported formats: .csv, .json, .yaml, .yml"
            )

        # Analyse the data
        return self._analyse_data(data, format_type)

    def analyse_data(
        self, data: list[dict[str, Any]], format_type: str = "csv"
    ) -> DataSchema:
        """
        Analyse structured data (list of dictionaries).

        Args:
            data: List of records as dictionaries.
            format_type: Original data format (csv, json, yaml).

        Returns:
            DataSchema with column information and distributions.
        """
        return self._analyse_data(data, format_type)

    def _load_csv(self, file_path: Path) -> list[dict[str, Any]]:
        """Load CSV file into list of dictionaries."""
        data = []
        with open(file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data

    def _load_json(self, file_path: Path) -> list[dict[str, Any]]:
        """Load JSON file into list of dictionaries."""
        with open(file_path, encoding="utf-8") as f:
            content = json.load(f)

        # Handle different JSON structures
        if isinstance(content, list):
            return content
        elif isinstance(content, dict):
            # Check for common wrapper keys
            for key in ["data", "records", "items", "interviews"]:
                if key in content and isinstance(content[key], list):
                    return content[key]
            # If dict has no list wrapper, wrap it
            return [content]
        else:
            raise ValueError("JSON must be a list or dictionary")

    def _load_yaml(self, file_path: Path) -> list[dict[str, Any]]:
        """Load YAML file into list of dictionaries."""
        with open(file_path, encoding="utf-8") as f:
            content = yaml.safe_load(f)

        # Handle different YAML structures
        if isinstance(content, list):
            return content
        elif isinstance(content, dict):
            # Check for common wrapper keys
            for key in ["data", "records", "items", "interviews"]:
                if key in content and isinstance(content[key], list):
                    return content[key]
            # If dict has no list wrapper, wrap it
            return [content]
        else:
            raise ValueError("YAML must be a list or dictionary")

    def _analyse_data(self, data: list[dict[str, Any]], format_type: str) -> DataSchema:
        """Analyse structured data and build schema."""
        if not data:
            raise ValueError("No data to analyse")

        row_count = len(data)

        # Extract all column names
        all_keys = set()
        for row in data:
            all_keys.update(row.keys())

        column_names = sorted(all_keys)

        # Analyse each column
        columns = []
        for col_name in column_names:
            dist = self._analyse_column(col_name, data)
            columns.append(dist)

        # Detect relationships (simplified - just note which columns might be related)
        relationships = self._detect_relationships(columns, data)

        return DataSchema(
            columns=columns,
            row_count=row_count,
            format=format_type,
            relationships=relationships,
        )

    def _analyse_column(
        self,
        col_name: str,
        data: list[dict[str, Any]],
    ) -> DistributionStats:
        """Analyse a single column to determine type and distribution."""
        values = []
        null_count = 0

        # Extract values
        for row in data:
            value = row.get(col_name)
            if (
                value is None
                or value == ""
                or (isinstance(value, str) and value.strip() == "")
            ):
                null_count += 1
            else:
                values.append(value)

        unique_count = len(set(str(v) for v in values))

        # Infer column type
        col_type = self._infer_type(values)

        # Sample values (up to 5)
        sample_values = list(set(values))[:5]

        # Build distribution based on type
        categorical_dist = None
        numeric_stats = None

        if col_type == ColumnType.CATEGORICAL or col_type == ColumnType.TEXT:
            # For categorical, count frequencies
            if unique_count <= 50:  # Reasonable categorical limit
                categorical_dist = self._calculate_categorical_distribution(values)
            else:
                # Too many unique values, treat as text
                col_type = ColumnType.TEXT

        elif col_type == ColumnType.NUMERIC:
            numeric_stats = self._calculate_numeric_stats(values)

        elif col_type == ColumnType.BOOLEAN:
            categorical_dist = self._calculate_categorical_distribution(values)

        return DistributionStats(
            column_name=col_name,
            column_type=col_type,
            unique_count=unique_count,
            null_count=null_count,
            sample_values=sample_values,
            categorical_distribution=categorical_dist,
            numeric_stats=numeric_stats,
        )

    def _infer_type(self, values: list[Any]) -> ColumnType:
        """Infer column type from values."""
        if not values:
            return ColumnType.UNKNOWN

        # Sample for type detection (up to 100 values)
        sample = values[:100]

        # Check for boolean
        bool_values = {
            True,
            False,
            "true",
            "false",
            "True",
            "False",
            "yes",
            "no",
            "Yes",
            "No",
        }
        if all(v in bool_values for v in sample):
            return ColumnType.BOOLEAN

        # Check for numeric
        numeric_count = 0
        for val in sample:
            try:
                float(val)
                numeric_count += 1
            except (ValueError, TypeError):
                pass

        if numeric_count == len(sample):
            return ColumnType.NUMERIC

        # Check for categorical (low cardinality text)
        unique_ratio = len(set(str(v) for v in sample)) / len(sample)
        if unique_ratio < 0.5:  # Less than 50% unique values
            return ColumnType.CATEGORICAL

        # Default to text
        return ColumnType.TEXT

    def _calculate_categorical_distribution(
        self,
        values: list[Any],
    ) -> dict[str, int]:
        """Calculate frequency distribution for categorical data."""
        distribution = {}
        for value in values:
            key = str(value)
            distribution[key] = distribution.get(key, 0) + 1
        return distribution

    def _calculate_numeric_stats(
        self,
        values: list[Any],
    ) -> dict[str, float]:
        """Calculate statistics for numeric data."""
        numeric_values = []
        for val in values:
            try:
                numeric_values.append(float(val))
            except (ValueError, TypeError):
                pass

        if not numeric_values:
            return {
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "std": 0.0,
            }

        mean = sum(numeric_values) / len(numeric_values)
        variance = sum((x - mean) ** 2 for x in numeric_values) / len(numeric_values)
        std = variance**0.5

        return {
            "min": min(numeric_values),
            "max": max(numeric_values),
            "mean": mean,
            "std": std,
        }

    def _detect_relationships(
        self,
        columns: list[DistributionStats],
        data: list[dict[str, Any]],
    ) -> dict[str, list[str]]:
        """
        Detect potential relationships between columns.

        This is a simplified implementation that looks for common patterns.
        In a more sophisticated version, this could use correlation analysis.
        """
        relationships = {}

        # Look for ID columns that might relate to other columns
        id_columns = [
            col.column_name
            for col in columns
            if "id" in col.column_name.lower() or col.column_name.endswith("_id")
        ]

        for id_col in id_columns:
            # Find columns that might be related (same cardinality)
            id_col_obj = next(c for c in columns if c.column_name == id_col)
            related = []

            for col in columns:
                if col.column_name != id_col:
                    # If similar unique count, might be related
                    if abs(col.unique_count - id_col_obj.unique_count) < 5:
                        related.append(col.column_name)

            if related:
                relationships[id_col] = related

        return relationships
