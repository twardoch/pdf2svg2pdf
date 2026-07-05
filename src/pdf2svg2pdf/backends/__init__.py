#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/backends/__init__.py
"""Backend implementations for pdf2svg2pdf."""

from .base import Backend, BackendRegistry
from .cairo import CairoBackend
from .fitz import FitzBackend
from .poppler import PopplerBackend

__all__ = [
    "Backend",
    "BackendRegistry",
    "PopplerBackend",
    "FitzBackend",
    "CairoBackend",
]
