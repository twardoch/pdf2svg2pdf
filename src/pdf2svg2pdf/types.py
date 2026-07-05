#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/types.py
"""Type definitions and aliases for pdf2svg2pdf package."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Literal, Protocol, TypedDict

# Path types
type PathLike = str | Path
type PathList = list[Path]

# Filter types
type FilterFunction = Callable[[bytes], bytes]
type SVGFilterFunction = Callable[[str], str]
type PDFFilterFunction = Callable[[bytes], bytes]
type AsyncFilterFunction = Callable[[bytes], Awaitable[bytes]]

# Backend types
type BackendName = Literal["poppler", "fitz", "cairo", "cairosvg", "pdfcairo"]
type BackendList = list[BackendName]


class ProcessingStatus(Enum):
    """Status of processing operations."""

    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class BackendCapability(Enum):
    """Capabilities that backends can support."""

    PDF_SPLIT = auto()
    PDF_MERGE = auto()
    PDF_TO_SVG = auto()
    SVG_TO_PDF = auto()
    ASYNC_SUPPORT = auto()
    STREAMING = auto()
    BATCH_PROCESSING = auto()


@dataclass(frozen=True)
class ProcessingMetrics:
    """Metrics collected during processing."""

    total_pages: int
    processed_pages: int
    failed_pages: int
    processing_time_ms: float
    memory_usage_mb: float
    input_file_size_mb: float
    output_file_size_mb: float


@dataclass
class PageInfo:
    """Information about a single page."""

    page_number: int
    input_path: Path
    temp_pdf_path: Path | None = None
    svg_path: Path | None = None
    output_pdf_path: Path | None = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    error: Exception | None = None


class ConversionResult(TypedDict):
    """Result of a conversion operation."""

    success: bool
    output_path: Path | None
    error: str | None
    metrics: ProcessingMetrics | None


class Backend(Protocol):
    """Protocol for backend implementations."""

    @property
    def name(self) -> BackendName:
        """Backend identifier."""
        ...

    @property
    def capabilities(self) -> set[BackendCapability]:
        """Set of supported capabilities."""
        ...

    def is_available(self) -> bool:
        """Check if backend is available on the system."""
        ...

    async def check_health(self) -> tuple[bool, str]:
        """Check backend health and return status with message."""
        ...


class Filter(Protocol):
    """Protocol for filter implementations."""

    @property
    def name(self) -> str:
        """Filter identifier."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description."""
        ...

    @property
    def supported_formats(self) -> set[str]:
        """Set of supported file formats (pdf, svg)."""
        ...

    def validate(self, content: bytes | str) -> tuple[bool, str]:
        """Validate if filter can be applied to content."""
        ...

    def apply(self, content: bytes | str) -> bytes | str:
        """Apply filter to content."""
        ...


@dataclass
class FilterConfig:
    """Configuration for a filter."""

    name: str
    enabled: bool = True
    parameters: dict[str, Any] | None = None
    priority: int = 0  # Higher priority filters run first


@dataclass
class BackendConfig:
    """Configuration for a backend."""

    name: BackendName
    enabled: bool = True
    priority: int = 0  # Higher priority backends are tried first
    timeout_seconds: float = 300.0
    max_retries: int = 3
    parameters: dict[str, Any] | None = None


# Progress callback types
type ProgressCallback = Callable[[float, str], None]
type AsyncProgressCallback = Callable[[float, str], Awaitable[None]]

# Error types
type ErrorHandler = Callable[[Exception, PageInfo], bool]  # Return True to continue
type AsyncErrorHandler = Callable[[Exception, PageInfo], Awaitable[bool]]
