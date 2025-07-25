#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/core/__init__.py
"""Core functionality for pdf2svg2pdf."""

from .converter import Converter
from .exceptions import (
    PDF2SVG2PDFError,
    BackendError,
    FilterError,
    ValidationError,
    ConfigurationError,
)
from .pipeline import ProcessingPipeline

__all__ = [
    "Converter",
    "ProcessingPipeline",
    "PDF2SVG2PDFError",
    "BackendError",
    "FilterError",
    "ValidationError",
    "ConfigurationError",
]