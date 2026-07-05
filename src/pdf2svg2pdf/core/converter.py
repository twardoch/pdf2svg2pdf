#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/core/converter.py
"""Main converter class for pdf2svg2pdf."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from ..filters.base import pdf_filter_registry, svg_filter_registry
from ..types import (
    BackendCapability,
    ConversionResult,
    PageInfo,
    PathLike,
    ProcessingMetrics,
    ProgressCallback,
)
from ..utils.io import ensure_directory, safe_temp_directory
from ..utils.validation import validate_file_size, validate_path
from .exceptions import ProcessingError, ValidationError
from .pipeline import ProcessingPipeline

if TYPE_CHECKING:
    from ..config import Configuration


class Converter:
    """Main converter class for PDF to SVG to PDF conversion."""

    def __init__(
        self,
        config: Configuration,
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        """Initialize converter.

        Args:
            config: Configuration object
            progress_callback: Optional progress callback
        """
        self.config = config
        self.progress_callback = progress_callback
        self.pipeline = ProcessingPipeline(config)

        # Set up logging
        config.setup_logging()

        # Initialize backends
        self._init_backends()

        # Initialize filters
        self._init_filters()

    def _init_backends(self) -> None:
        """Initialize and validate backends."""
        # Import the backend registry lazily to avoid a core<->backends import
        # cycle (backends.base imports core.exceptions).
        from ..backends import CairoBackend, FitzBackend, PopplerBackend
        from ..backends.base import registry as backend_registry

        backend_registry.register(PopplerBackend)
        backend_registry.register(FitzBackend)
        backend_registry.register(CairoBackend)

        # Check availability
        available = backend_registry.get_available(config=self.config)
        if not available:
            raise ValidationError(
                "No backends available. Please install required dependencies.",
                details={
                    "poppler": "apt-get install poppler-utils",
                    "pymupdf": "pip install PyMuPDF",
                    "cairo": "apt-get install libcairo2",
                },
            )

        logger.info(f"Available backends: {[b.name for b in available]}")

    def _init_filters(self) -> None:
        """Initialize filter registries."""
        # Register all filter implementations
        from ..filters import (
            GrayscaleFilter,
            PDFCompressFilter,
            SVGOptimizeFilter,
            SVGTransparentWhiteFilter,
        )

        pdf_filter_registry.register(GrayscaleFilter)
        pdf_filter_registry.register(PDFCompressFilter)
        svg_filter_registry.register(SVGOptimizeFilter)
        svg_filter_registry.register(SVGTransparentWhiteFilter)

        logger.info(
            f"Registered PDF filters: {list(pdf_filter_registry.get_all().keys())}"
        )
        logger.info(
            f"Registered SVG filters: {list(svg_filter_registry.get_all().keys())}"
        )

    async def convert(
        self,
        input_path: PathLike,
        output_path: PathLike | None = None,
        output_dir: PathLike | None = None,
    ) -> ConversionResult:
        """Convert a PDF file.

        Args:
            input_path: Path to input PDF
            output_path: Optional path for output PDF
            output_dir: Optional output directory

        Returns:
            Conversion result
        """
        from ..backends.base import registry as backend_registry

        try:
            # Validate input
            input_path = validate_path(
                input_path,
                must_exist=True,
                must_be_file=True,
                allowed_extensions={".pdf"},
            )

            # Validate file size
            if self.config.security.max_file_size_mb:
                validate_file_size(
                    input_path,
                    self.config.security.max_file_size_mb,
                )

            # Determine output path
            if output_path is None:
                if output_dir is None:
                    output_dir = input_path.parent
                else:
                    output_dir = ensure_directory(output_dir)

                output_path = output_dir / (
                    input_path.stem + self.config.output_suffix + ".pdf"
                )
            else:
                output_path = Path(output_path)
                ensure_directory(output_path.parent)

            # Process the file
            logger.info(f"Converting {input_path} to {output_path}")

            with safe_temp_directory(
                cleanup=self.config.processing.cleanup_on_error
            ) as temp_dir:
                # Create subdirectories
                pdf_pages_dir = ensure_directory(temp_dir / "pdf_pages")
                svg_dir = ensure_directory(temp_dir / "svg")
                pdf_output_dir = ensure_directory(temp_dir / "pdf_output")

                # Split PDF into pages
                if self.progress_callback:
                    self.progress_callback(0.1, "Splitting PDF into pages")

                split_backend = backend_registry.find_best(
                    BackendCapability.PDF_SPLIT,
                    self.config,
                )
                page_paths = await split_backend.split_pdf(
                    input_path,
                    pdf_pages_dir,
                )

                # Create page info objects
                pages = [
                    PageInfo(
                        page_number=i,
                        input_path=page_path,
                        temp_pdf_path=page_path,
                    )
                    for i, page_path in enumerate(page_paths)
                ]

                # Process pages through pipeline
                if self.progress_callback:
                    self.progress_callback(0.2, "Processing pages")

                processed_pages = await self.pipeline.process_pages(
                    pages,
                    svg_dir,
                    pdf_output_dir,
                    self.progress_callback,
                )

                # Merge processed PDFs
                if self.progress_callback:
                    self.progress_callback(0.9, "Merging processed pages")

                merge_backend = backend_registry.find_best(
                    BackendCapability.PDF_MERGE,
                    self.config,
                )

                output_pdfs: list[str | Path] = [
                    p.output_pdf_path
                    for p in processed_pages
                    if p.output_pdf_path and p.output_pdf_path.exists()
                ]

                if not output_pdfs:
                    raise ProcessingError("No pages were successfully processed")

                await merge_backend.merge_pdfs(output_pdfs, output_path)

                # Calculate metrics
                metrics = ProcessingMetrics(
                    total_pages=len(pages),
                    processed_pages=len(output_pdfs),
                    failed_pages=len(pages) - len(output_pdfs),
                    processing_time_ms=0,  # TODO: Add timing
                    memory_usage_mb=0,  # TODO: Add memory tracking
                    input_file_size_mb=input_path.stat().st_size / (1024 * 1024),
                    output_file_size_mb=output_path.stat().st_size / (1024 * 1024),
                )

                if self.progress_callback:
                    self.progress_callback(1.0, "Conversion complete")

                logger.info(f"Successfully converted to {output_path}")

                return ConversionResult(
                    success=True,
                    output_path=output_path,
                    error=None,
                    metrics=metrics,
                )

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return ConversionResult(
                success=False,
                output_path=None,
                error=str(e),
                metrics=None,
            )

    def convert_sync(
        self,
        input_path: PathLike,
        output_path: PathLike | None = None,
        output_dir: PathLike | None = None,
    ) -> ConversionResult:
        """Synchronous wrapper for convert method.

        Args:
            input_path: Path to input PDF
            output_path: Optional path for output PDF
            output_dir: Optional output directory

        Returns:
            Conversion result
        """
        return asyncio.run(self.convert(input_path, output_path, output_dir))

    async def convert_batch(
        self,
        input_paths: list[PathLike],
        output_dir: PathLike | None = None,
    ) -> list[ConversionResult]:
        """Convert multiple PDF files.

        Args:
            input_paths: List of input PDF paths
            output_dir: Optional output directory

        Returns:
            List of conversion results
        """
        tasks = [
            self.convert(input_path, output_dir=output_dir)
            for input_path in input_paths
        ]

        return await asyncio.gather(*tasks)

    def convert_batch_sync(
        self,
        input_paths: list[PathLike],
        output_dir: PathLike | None = None,
    ) -> list[ConversionResult]:
        """Synchronous wrapper for convert_batch method.

        Args:
            input_paths: List of input PDF paths
            output_dir: Optional output directory

        Returns:
            List of conversion results
        """
        return asyncio.run(self.convert_batch(input_paths, output_dir))
