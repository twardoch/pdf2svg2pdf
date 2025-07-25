#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/filters/pdf.py
"""PDF filter implementations."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from loguru import logger

from ..types import FilterConfig
from ..utils.async_utils import run_async
from .base import Filter


class GrayscaleFilter(Filter):
    """Convert PDF to grayscale using Ghostscript."""
    
    @property
    def name(self) -> str:
        """Filter identifier."""
        return "grayscale"
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return "Convert PDF to grayscale"
    
    @property
    def supported_formats(self) -> set[str]:
        """Set of supported file formats."""
        return {"pdf"}
    
    def apply(self, content: bytes) -> bytes:
        """Apply grayscale conversion to PDF.
        
        Args:
            content: PDF content as bytes
            
        Returns:
            Grayscale PDF content
        """
        # Check if ghostscript is available
        try:
            subprocess.run(["gs", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Ghostscript not available, skipping grayscale filter")
            return content
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as input_file:
            input_path = Path(input_file.name)
            input_file.write(content)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_file:
            output_path = Path(output_file.name)
        
        try:
            # Run ghostscript
            command = [
                "gs",
                "-sOutputFile=" + str(output_path),
                "-sDEVICE=pdfwrite",
                "-sColorConversionStrategy=Gray",
                "-dProcessColorModel=/DeviceGray",
                "-dCompatibilityLevel=1.4",
                "-dNOPAUSE",
                "-dBATCH",
                str(input_path),
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
            
            # Read output
            with open(output_path, "rb") as f:
                return f.read()
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Ghostscript failed: {e.stderr}")
            raise
        finally:
            # Cleanup
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


class PDFCompressFilter(Filter):
    """Compress PDF using Ghostscript."""
    
    def __init__(self, config: FilterConfig | None = None) -> None:
        """Initialize filter.
        
        Args:
            config: Filter configuration
        """
        super().__init__(config)
        # Get compression level from config
        self.quality = "screen"  # screen, ebook, printer, prepress
        if config and config.parameters:
            self.quality = config.parameters.get("quality", self.quality)
    
    @property
    def name(self) -> str:
        """Filter identifier."""
        return "compress"
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return "Compress PDF file size"
    
    @property
    def supported_formats(self) -> set[str]:
        """Set of supported file formats."""
        return {"pdf"}
    
    def apply(self, content: bytes) -> bytes:
        """Apply compression to PDF.
        
        Args:
            content: PDF content as bytes
            
        Returns:
            Compressed PDF content
        """
        # Check if ghostscript is available
        try:
            subprocess.run(["gs", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Ghostscript not available, skipping compress filter")
            return content
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as input_file:
            input_path = Path(input_file.name)
            input_file.write(content)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_file:
            output_path = Path(output_file.name)
        
        try:
            # Run ghostscript with compression
            command = [
                "gs",
                "-sOutputFile=" + str(output_path),
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS=/{self.quality}",
                "-dNOPAUSE",
                "-dBATCH",
                "-dQUIET",
                str(input_path),
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
            
            # Read output
            with open(output_path, "rb") as f:
                compressed = f.read()
            
            # Log compression ratio
            original_size = len(content)
            compressed_size = len(compressed)
            ratio = (1 - compressed_size / original_size) * 100
            logger.debug(
                f"Compressed PDF from {original_size} to {compressed_size} bytes "
                f"({ratio:.1f}% reduction)"
            )
            
            return compressed
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Ghostscript compression failed: {e.stderr}")
            raise
        finally:
            # Cleanup
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)