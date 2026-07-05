#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/backends/cairo.py
"""Cairo backend implementation."""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from ..types import BackendCapability, BackendName, PathLike
from ..utils.async_utils import run_async
from .base import Backend


class CairoBackend(Backend):
    """Backend using Cairo/CairoSVG."""

    @property
    def name(self) -> BackendName:
        """Backend identifier."""
        return "cairo"

    @property
    def capabilities(self) -> set[BackendCapability]:
        """Set of supported capabilities."""
        return {
            BackendCapability.SVG_TO_PDF,
        }

    @property
    def required_commands(self) -> list[str]:
        """List of required system commands."""
        return ["cairosvg"]

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
        raise NotImplementedError("Cairo backend does not support PDF splitting")

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
        raise NotImplementedError("Cairo backend does not support PDF merging")

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
        raise NotImplementedError(
            "Cairo backend does not support PDF to SVG conversion"
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
        input_path = Path(input_path)
        output_path = Path(output_path)

        # Run cairosvg
        command = [
            "cairosvg",
            "-f",
            "pdf",
            "-o",
            str(output_path),
            str(input_path),
        ]
        await run_async(self._run_command, command)

        logger.debug(f"Converted {input_path} to {output_path}")
        return output_path
