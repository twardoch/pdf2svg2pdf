#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/__init__.py
"""PDF to SVG to PDF converter with optional transformations."""

import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

# New API imports
from .config import Configuration, load_configuration
from .core import (
    Converter,
    ProcessingPipeline,
    PDF2SVG2PDFError,
    BackendError,
    FilterError,
    ValidationError,
    ConfigurationError,
)
from .backends import Backend, BackendRegistry
from .filters import Filter, FilterRegistry

# Legacy API imports for backwards compatibility
from .pdf2svg2pdf import PDF2SVG2PDF
from .pdf2svg2pdf import convert_pdfs

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
