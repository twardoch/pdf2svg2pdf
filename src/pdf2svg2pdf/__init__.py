#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/__init__.py
"""PDF to SVG to PDF converter with optional transformations."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pdf2svg2pdf")
except PackageNotFoundError:  # pragma: no cover - only when running from a raw checkout
    __version__ = "0.0.0"

# New API imports
from .backends import Backend, BackendRegistry
from .config import Configuration, load_configuration
from .core import (
    BackendError,
    ConfigurationError,
    Converter,
    FilterError,
    PDF2SVG2PDFError,
    ProcessingPipeline,
    ValidationError,
)
from .filters import Filter, FilterRegistry

# Legacy API imports for backwards compatibility
from .pdf2svg2pdf import PDF2SVG2PDF, convert_pdfs

__all__ = [
    # Version
    "__version__",
    # New API
    "Configuration",
    "load_configuration",
    "Converter",
    "ProcessingPipeline",
    "Backend",
    "BackendRegistry",
    "Filter",
    "FilterRegistry",
    # Exceptions
    "PDF2SVG2PDFError",
    "BackendError",
    "FilterError",
    "ValidationError",
    "ConfigurationError",
    # Legacy API
    "PDF2SVG2PDF",
    "convert_pdfs",
]
