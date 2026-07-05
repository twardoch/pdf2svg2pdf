#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/core/pipeline.py
"""Processing pipeline for pdf2svg2pdf."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from ..filters.base import pdf_filter_registry, svg_filter_registry
from ..types import (
    BackendCapability,
    PageInfo,
    PathLike,
    ProcessingStatus,
    ProgressCallback,
)
from ..utils.async_utils import AsyncPool
from ..utils.io import ensure_directory
from ..utils.security import sanitize_svg_content
from .exceptions import ProcessingError

if TYPE_CHECKING:
    from ..config import Configuration


class ProcessingPipeline:
    """Pipeline for processing PDF pages through filters."""

    def __init__(self, config: Configuration) -> None:
        """Initialize pipeline.

        Args:
            config: Configuration object
        """
        self.config = config

        # Create filter chains
        self.pdf_filter_chain = pdf_filter_registry.create_chain(
            config.pdf_filters,
            name="pdf_filters",
        )
        self.svg_filter_chain = svg_filter_registry.create_chain(
            config.svg_filters,
            name="svg_filters",
        )

    async def process_pages(
        self,
        pages: list[PageInfo],
        svg_dir: PathLike,
        pdf_output_dir: PathLike,
        progress_callback: ProgressCallback | None = None,
    ) -> list[PageInfo]:
        """Process pages through the pipeline.

        Args:
            pages: List of pages to process
            svg_dir: Directory for SVG files
            pdf_output_dir: Directory for output PDFs
            progress_callback: Optional progress callback

        Returns:
            List of processed pages
        """
        svg_dir = ensure_directory(svg_dir)
        pdf_output_dir = ensure_directory(pdf_output_dir)

        # Create task pool
        pool = AsyncPool(self.config.processing.parallel_pages)

        # Process each page. AsyncPool.submit is a coroutine, so it must be
        # awaited or the page is never scheduled onto the pool.
        for i, page in enumerate(pages):
            await pool.submit(
                self._process_single_page(
                    page,
                    svg_dir,
                    pdf_output_dir,
                )
            )

            # Update progress
            if progress_callback:
                base_progress = 0.2
                page_progress = 0.7 * (i + 1) / len(pages)
                progress_callback(
                    base_progress + page_progress,
                    f"Processing page {i + 1}/{len(pages)}",
                )

        # Wait for all tasks
        await pool.gather()

        # Return successfully processed pages
        return [p for p in pages if p.status == ProcessingStatus.COMPLETED]

    async def _process_single_page(
        self,
        page: PageInfo,
        svg_dir: Path,
        pdf_output_dir: Path,
    ) -> None:
        """Process a single page.

        Args:
            page: Page to process
            svg_dir: Directory for SVG files
            pdf_output_dir: Directory for output PDFs
        """
        try:
            page.status = ProcessingStatus.IN_PROGRESS

            # Apply PDF filters if any
            if self.pdf_filter_chain.filters and page.temp_pdf_path:
                logger.debug(f"Applying PDF filters to page {page.page_number}")

                with open(page.temp_pdf_path, "rb") as f:
                    pdf_content = f.read()

                filtered_pdf = self.pdf_filter_chain(pdf_content)

                # Write filtered PDF
                filtered_path = page.temp_pdf_path.parent / (
                    page.temp_pdf_path.stem + "_filtered.pdf"
                )
                with open(filtered_path, "wb") as f:
                    f.write(filtered_pdf)

                page.temp_pdf_path = filtered_path

            # Convert PDF to SVG
            svg_path = svg_dir / f"page_{page.page_number:04d}.svg"
            page.svg_path = await self._pdf_to_svg(page.temp_pdf_path, svg_path)

            # Apply SVG filters if any
            if self.svg_filter_chain.filters and page.svg_path:
                logger.debug(f"Applying SVG filters to page {page.page_number}")

                with open(page.svg_path, encoding="utf-8") as f:
                    svg_content = f.read()

                # Sanitize SVG for security
                if self.config.security.sanitize_svg:
                    svg_content = sanitize_svg_content(svg_content)

                filtered_svg = self.svg_filter_chain(svg_content)

                # Write filtered SVG
                with open(page.svg_path, "w", encoding="utf-8") as f:
                    f.write(filtered_svg)

            # Convert SVG back to PDF
            output_pdf_path = pdf_output_dir / f"page_{page.page_number:04d}.pdf"
            page.output_pdf_path = await self._svg_to_pdf(
                page.svg_path, output_pdf_path
            )

            page.status = ProcessingStatus.COMPLETED
            logger.debug(f"Successfully processed page {page.page_number}")

        except Exception as e:
            page.status = ProcessingStatus.FAILED
            page.error = e
            logger.error(f"Failed to process page {page.page_number}: {e}")

            # Re-raise if configured
            if not self.config.processing.cleanup_on_error:
                raise ProcessingError(
                    f"Failed to process page {page.page_number}",
                    page_number=page.page_number,
                    stage="pipeline",
                ) from e

    async def _pdf_to_svg(
        self,
        pdf_path: Path | None,
        svg_path: Path,
    ) -> Path:
        """Convert PDF to SVG.

        Args:
            pdf_path: Input PDF path
            svg_path: Output SVG path

        Returns:
            Path to SVG file
        """
        if not pdf_path:
            raise ProcessingError("No PDF path provided")

        # Imported lazily to avoid a core<->backends import cycle.
        from ..backends.base import registry as backend_registry

        backend = backend_registry.find_best(
            BackendCapability.PDF_TO_SVG,
            self.config,
        )

        return await backend.pdf_to_svg(pdf_path, svg_path)

    async def _svg_to_pdf(
        self,
        svg_path: Path | None,
        pdf_path: Path,
    ) -> Path:
        """Convert SVG to PDF.

        Args:
            svg_path: Input SVG path
            pdf_path: Output PDF path

        Returns:
            Path to PDF file
        """
        if not svg_path:
            raise ProcessingError("No SVG path provided")

        # Imported lazily to avoid a core<->backends import cycle.
        from ..backends.base import registry as backend_registry

        backend = backend_registry.find_best(
            BackendCapability.SVG_TO_PDF,
            self.config,
        )

        return await backend.svg_to_pdf(svg_path, pdf_path)
