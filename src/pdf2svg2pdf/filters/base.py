#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/filters/base.py
"""Base classes and registry for filters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from loguru import logger

from ..core.exceptions import FilterError
from ..types import FilterConfig

ContentType = TypeVar("ContentType", bytes, str)


class Filter(ABC):
    """Abstract base class for all filters."""

    def __init__(self, config: FilterConfig | None = None) -> None:
        """Initialize filter with configuration.

        Args:
            config: Optional filter configuration
        """
        self.config = config or FilterConfig(name=self.name)

    @property
    @abstractmethod
    def name(self) -> str:
        """Filter identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""
        ...

    @property
    @abstractmethod
    def supported_formats(self) -> set[str]:
        """Set of supported file formats (pdf, svg)."""
        ...

    def validate(self, content: ContentType) -> tuple[bool, str]:
        """Validate if filter can be applied to content.

        Args:
            content: Content to validate

        Returns:
            Tuple of (is_valid, message)
        """
        # Basic validation - can be overridden
        if not content:
            return False, "Empty content"

        return True, "Content is valid"

    @abstractmethod
    def apply(self, content: ContentType) -> ContentType:
        """Apply filter to content.

        Args:
            content: Content to filter

        Returns:
            Filtered content
        """
        ...

    def __call__(self, content: ContentType) -> ContentType:
        """Make filter callable.

        Args:
            content: Content to filter

        Returns:
            Filtered content
        """
        # Validate first
        is_valid, message = self.validate(content)
        if not is_valid:
            raise FilterError(
                f"Validation failed: {message}",
                filter_name=self.name,
            )

        # Apply filter
        try:
            logger.debug(f"Applying filter: {self.name}")
            return self.apply(content)
        except Exception as e:
            raise FilterError(
                f"Failed to apply filter: {e}",
                filter_name=self.name,
            ) from e


class ChainFilter(Filter):
    """Filter that chains multiple filters together."""

    def __init__(
        self,
        filters: list[Filter],
        name: str = "chain",
        config: FilterConfig | None = None,
    ) -> None:
        """Initialize chain filter.

        Args:
            filters: List of filters to chain
            name: Name for the chain
            config: Optional configuration
        """
        super().__init__(config)
        self.filters = filters
        self._name = name

    @property
    def name(self) -> str:
        """Filter identifier."""
        return self._name

    @property
    def description(self) -> str:
        """Human-readable description."""
        filter_names = ", ".join(f.name for f in self.filters)
        return f"Chain of filters: {filter_names}"

    @property
    def supported_formats(self) -> set[str]:
        """Set of supported file formats."""
        # Intersection of all filter formats
        if not self.filters:
            return set()

        formats = self.filters[0].supported_formats
        for f in self.filters[1:]:
            formats &= f.supported_formats

        return formats

    def validate(self, content: ContentType) -> tuple[bool, str]:
        """Validate content against all filters.

        Args:
            content: Content to validate

        Returns:
            Tuple of (is_valid, message)
        """
        for f in self.filters:
            is_valid, message = f.validate(content)
            if not is_valid:
                return False, f"{f.name}: {message}"

        return True, "All filters validated"

    def apply(self, content: ContentType) -> ContentType:
        """Apply all filters in sequence.

        Args:
            content: Content to filter

        Returns:
            Filtered content
        """
        result = content
        for f in self.filters:
            result = f(result)
        return result


class FilterRegistry:
    """Registry for filter implementations."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._filters: dict[str, type[Filter]] = {}
        self._instances: dict[str, Filter] = {}

    def register(self, filter_class: type[Filter]) -> None:
        """Register a filter class.

        Args:
            filter_class: Filter class to register
        """
        instance = filter_class()
        name = instance.name
        self._filters[name] = filter_class
        logger.debug(f"Registered filter: {name}")

    def get(
        self,
        name: str,
        config: FilterConfig | None = None,
    ) -> Filter:
        """Get a filter instance.

        Args:
            name: Filter name
            config: Optional configuration

        Returns:
            Filter instance

        Raises:
            FilterError: If filter not found
        """
        if name not in self._filters:
            raise FilterError(
                f"Filter not found: {name}",
                filter_name=name,
                details={"available": list(self._filters.keys())},
            )

        # Create instance with config
        return self._filters[name](config)

    def create_chain(
        self,
        configs: list[FilterConfig],
        name: str = "chain",
    ) -> ChainFilter:
        """Create a chain of filters from configurations.

        Args:
            configs: List of filter configurations
            name: Name for the chain

        Returns:
            Chain filter instance
        """
        filters = []
        for config in configs:
            if config.enabled:
                filters.append(self.get(config.name, config))

        return ChainFilter(filters, name)

    def get_all(self, format: str | None = None) -> dict[str, type[Filter]]:
        """Get all registered filters.

        Args:
            format: Optional format filter (pdf, svg)

        Returns:
            Dictionary of filter classes
        """
        if format is None:
            return self._filters.copy()

        result = {}
        for name, filter_class in self._filters.items():
            instance = filter_class()
            if format in instance.supported_formats:
                result[name] = filter_class

        return result


# Global registry instances
pdf_filter_registry = FilterRegistry()
svg_filter_registry = FilterRegistry()
