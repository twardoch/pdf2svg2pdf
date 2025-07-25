#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/backends/fitz.py
"""PyMuPDF (Fitz) backend implementation."""

from __future__ import annotations

from pathlib import Path

import fitz
from loguru import logger

from ..types import BackendCapability, BackendName, PathLike
from ..utils.async_utils import run_async
from .base import Backend


class FitzBackend(Backend):
    """Backend using PyMuPDF (Fitz)."""
    
    @property
    def name(self) -> BackendName:
        """Backend identifier."""
        return "fitz"
    
    @property
    def capabilities(self) -> set[BackendCapability]:
        """Set of supported capabilities."""
        return {
            BackendCapability.PDF_SPLIT,
            BackendCapability.PDF_MERGE,
        }
    
    @property
    def required_commands(self) -> list[str]:
        """List of required system commands."""
        # Fitz is a Python library, no system commands needed
        return []
    
    def is_available(self) -> bool:
        """Check if backend is available.
        
        Returns:
            True if PyMuPDF is installed
        """
        try:
            import fitz
            return True
        except ImportError:
            return False
    
    async def split_pdf(
        self,
        input_path: PathLike,
        output_dir: PathLike,
        prefix: str = "page",
    ) -> list[Path]:
        """Split PDF into individual pages.
        
        Args:
            input_path: Path to input PDF
            output_dir: Directory for output pages
            prefix: Prefix for output filenames
            
        Returns:
            List of paths to individual page PDFs
        """
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        
        def split_sync() -> list[Path]:
            """Synchronous split function."""
            doc = fitz.open(str(input_path))
            output_files = []
            
            try:
                for i in range(len(doc)):
                    # Create single page document
                    output_path = output_dir / f"{prefix}_{i:04d}.pdf"
                    single_page_doc = fitz.open()
                    
                    try:
                        single_page_doc.insert_pdf(doc, from_page=i, to_page=i)
                        single_page_doc.save(str(output_path))
                        output_files.append(output_path)
                    finally:
                        single_page_doc.close()
                
                logger.debug(f"Split {input_path} into {len(output_files)} pages")
                return output_files
                
            finally:
                doc.close()
        
        return await run_async(split_sync)
    
    async def merge_pdfs(
        self,
        input_paths: list[PathLike],
        output_path: PathLike,
    ) -> Path:
        """Merge multiple PDFs into one.
        
        Args:
            input_paths: List of PDF paths to merge
            output_path: Path for merged PDF
            
        Returns:
            Path to merged PDF
        """
        output_path = Path(output_path)
        
        def merge_sync() -> Path:
            """Synchronous merge function."""
            merged_doc = fitz.open()
            
            try:
                for input_path in input_paths:
                    doc = fitz.open(str(input_path))
                    try:
                        merged_doc.insert_pdf(doc)
                    finally:
                        doc.close()
                
                merged_doc.save(str(output_path))
                logger.debug(f"Merged {len(input_paths)} PDFs into {output_path}")
                return output_path
                
            finally:
                merged_doc.close()
        
        return await run_async(merge_sync)
    
    async def pdf_to_svg(
        self,
        input_path: PathLike,
        output_path: PathLike,
    ) -> Path:
        """Convert PDF to SVG.
        
        Args:
            input_path: Path to input PDF
            output_path: Path for output SVG
            
        Returns:
            Path to output SVG
        """
        # PyMuPDF doesn't have direct PDF to SVG conversion
        raise NotImplementedError(
            "Fitz backend does not support PDF to SVG conversion"
        )
    
    async def svg_to_pdf(
        self,
        input_path: PathLike,
        output_path: PathLike,
    ) -> Path:
        """Convert SVG to PDF.
        
        Args:
            input_path: Path to input SVG
            output_path: Path for output PDF
            
        Returns:
            Path to output PDF
        """
        # PyMuPDF doesn't support SVG to PDF conversion
        raise NotImplementedError(
            "Fitz backend does not support SVG to PDF conversion"
        )