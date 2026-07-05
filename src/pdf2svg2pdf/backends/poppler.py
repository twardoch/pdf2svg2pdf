#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/backends/poppler.py
"""Poppler backend implementation."""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from ..types import BackendCapability, BackendName, PathLike
from ..utils.async_utils import run_async
from .base import Backend


class PopplerBackend(Backend):
    """Backend using Poppler utilities."""

    @property
    def name(self) -> BackendName:
        """Backend identifier."""
        return "poppler"

    @property
    def capabilities(self) -> set[BackendCapability]:
        """Set of supported capabilities."""
        return {
            BackendCapability.PDF_SPLIT,
            BackendCapability.PDF_MERGE,
            BackendCapability.PDF_TO_SVG,
        }

    @property
    def required_commands(self) -> list[str]:
        """List of required system commands."""
        return ["pdfseparate", "pdfunite", "pdftocairo"]

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

        # Create output pattern
        output_pattern = str(output_dir / f"{prefix}_%04d.pdf")

        # Run pdfseparate
        command = ["pdfseparate", str(input_path), output_pattern]
        await run_async(self._run_command, command)

        # Find generated files
        page_files = sorted(output_dir.glob(f"{prefix}_*.pdf"))

        logger.debug(f"Split {input_path} into {len(page_files)} pages")
        return page_files

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

        # Build command
        command = ["pdfunite"]
        command.extend(str(p) for p in input_paths)
        command.append(str(output_path))

        # Run pdfunite
        await run_async(self._run_command, command)

        logger.debug(f"Merged {len(input_paths)} PDFs into {output_path}")
        return output_path

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
        input_path = Path(input_path)
        output_path = Path(output_path)

        # Run pdftocairo
        command = ["pdftocairo", "-svg", str(input_path), str(output_path)]
        await run_async(self._run_command, command)

        logger.debug(f"Converted {input_path} to {output_path}")
        return output_path

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
        # Poppler doesn't support SVG to PDF conversion
        raise NotImplementedError(
            "Poppler backend does not support SVG to PDF conversion"
        )
