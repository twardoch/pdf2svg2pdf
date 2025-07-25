#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/cli.py
"""Command-line interface for pdf2svg2pdf."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import fire
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from .config import Configuration, load_configuration
from .core.converter import Converter
from .core.exceptions import PDF2SVG2PDFError
from .types import ConversionResult, PathLike, ProgressCallback
from . import __version__


console = Console()


class RichProgressCallback:
    """Progress callback that updates Rich progress bar."""
    
    def __init__(self, progress: Progress, task_id: Any) -> None:
        """Initialize callback.
        
        Args:
            progress: Rich Progress instance
            task_id: Task ID to update
        """
        self.progress = progress
        self.task_id = task_id
    
    def __call__(self, fraction: float, message: str) -> None:
        """Update progress.
        
        Args:
            fraction: Progress fraction (0.0 to 1.0)
            message: Progress message
        """
        self.progress.update(
            self.task_id,
            completed=int(fraction * 100),
            description=message,
        )


class PDF2SVG2PDFCLI:
    """Command-line interface for pdf2svg2pdf."""
    
    def __init__(self, verbose: bool = False, config: str | None = None) -> None:
        """Initialize CLI.
        
        Args:
            verbose: Enable verbose output
            config: Path to configuration file
        """
        self.verbose = verbose
        self.config_path = config
        
        # Set up basic logging
        if verbose:
            logger.add(
                sink=lambda msg: console.print(f"[dim]{msg}[/dim]", end=""),
                level="DEBUG",
            )
        else:
            logger.remove()  # Remove default handler
    
    def _load_config(self, **overrides: Any) -> Configuration:
        """Load configuration with overrides.
        
        Args:
            **overrides: Configuration overrides
            
        Returns:
            Configuration instance
        """
        # Load base configuration
        config = load_configuration(self.config_path)
        
        # Apply overrides
        if overrides.get("parallel_pages"):
            config.processing.parallel_pages = overrides["parallel_pages"]
        if overrides.get("timeout"):
            config.processing.timeout_seconds = overrides["timeout"]
        
        return config
    
    def _show_result(self, result: ConversionResult, path: Path) -> None:
        """Show conversion result.
        
        Args:
            result: Conversion result
            path: Input file path
        """
        if result["success"]:
            console.print(
                f"✅ [green]Successfully converted[/green] {path.name} → "
                f"{result['output_path'].name if result['output_path'] else 'N/A'}"
            )
            
            if result["metrics"] and self.verbose:
                m = result["metrics"]
                console.print(
                    f"   Pages: {m.processed_pages}/{m.total_pages} | "
                    f"Size: {m.input_file_size_mb:.1f}MB → {m.output_file_size_mb:.1f}MB"
                )
        else:
            console.print(
                f"❌ [red]Failed to convert[/red] {path.name}: {result['error']}"
            )
    
    def convert(
        self,
        input_path: str,
        output: str | None = None,
        output_dir: str | None = None,
        parallel_pages: int | None = None,
        timeout: float | None = None,
        pdf_filters: str | None = None,
        svg_filters: str | None = None,
    ) -> None:
        """Convert a PDF file.
        
        Args:
            input_path: Path to input PDF file
            output: Output file path
            output_dir: Output directory (alternative to output)
            parallel_pages: Number of pages to process in parallel
            timeout: Timeout in seconds
            pdf_filters: Comma-separated list of PDF filters
            svg_filters: Comma-separated list of SVG filters
        """
        try:
            # Load configuration
            config = self._load_config(
                parallel_pages=parallel_pages,
                timeout=timeout,
            )
            
            # Parse filters
            if pdf_filters:
                from .types import FilterConfig
                config.pdf_filters = [
                    FilterConfig(name=name.strip(), enabled=True)
                    for name in pdf_filters.split(",")
                ]
            if svg_filters:
                from .types import FilterConfig
                config.svg_filters = [
                    FilterConfig(name=name.strip(), enabled=True)
                    for name in svg_filters.split(",")
                ]
            
            # Create converter
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Converting PDF...", total=100)
                callback = RichProgressCallback(progress, task)
                
                converter = Converter(config, progress_callback=callback)
                
                # Convert file
                result = converter.convert_sync(
                    input_path,
                    output_path=output,
                    output_dir=output_dir,
                )
                
                # Show result
                self._show_result(result, Path(input_path))
                
                if not result["success"]:
                    sys.exit(1)
                    
        except PDF2SVG2PDFError as e:
            console.print(f"[red]Error:[/red] {e}")
            if self.verbose and e.details:
                console.print("[dim]Details:[/dim]", e.details)
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Unexpected error:[/red] {e}")
            if self.verbose:
                console.print_exception()
            sys.exit(1)
    
    def batch(
        self,
        *input_paths: str,
        input_dir: str | None = None,
        output_dir: str | None = None,
        pattern: str = "*.pdf",
        parallel_pages: int | None = None,
        parallel_files: int = 1,
    ) -> None:
        """Convert multiple PDF files.
        
        Args:
            *input_paths: Input PDF file paths
            input_dir: Input directory to scan for PDFs
            output_dir: Output directory for converted files
            pattern: File pattern for directory scanning
            parallel_pages: Number of pages to process in parallel per file
            parallel_files: Number of files to process in parallel
        """
        try:
            # Collect input files
            files = []
            
            # Add explicit paths
            files.extend(Path(p) for p in input_paths)
            
            # Add files from directory
            if input_dir:
                dir_path = Path(input_dir)
                if not dir_path.is_dir():
                    raise ValueError(f"Not a directory: {input_dir}")
                files.extend(dir_path.glob(pattern))
            
            if not files:
                console.print("[yellow]No files to convert[/yellow]")
                return
            
            # Load configuration
            config = self._load_config(
                parallel_pages=parallel_pages,
            )
            
            # Show summary
            console.print(
                Panel(
                    f"Converting {len(files)} files\n"
                    f"Output directory: {output_dir or 'Same as input'}\n"
                    f"Parallel files: {parallel_files}",
                    title="Batch Conversion",
                    border_style="blue",
                )
            )
            
            # Create converter
            converter = Converter(config)
            
            # Convert files
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Converting {len(files)} files...",
                    total=len(files),
                )
                
                results = []
                for i, file_path in enumerate(files):
                    progress.update(
                        task,
                        description=f"Converting {file_path.name}...",
                    )
                    
                    result = converter.convert_sync(
                        file_path,
                        output_dir=output_dir,
                    )
                    results.append((file_path, result))
                    
                    progress.update(task, advance=1)
            
            # Show results summary
            success_count = sum(1 for _, r in results if r["success"])
            
            table = Table(title="Conversion Results")
            table.add_column("File", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Output", style="blue")
            
            for file_path, result in results:
                status = "✅ Success" if result["success"] else f"❌ Failed: {result['error']}"
                output = str(result["output_path"].name) if result["output_path"] else "N/A"
                table.add_row(file_path.name, status, output)
            
            console.print(table)
            console.print(
                f"\nCompleted: {success_count}/{len(files)} files converted successfully"
            )
            
            if success_count < len(files):
                sys.exit(1)
                
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            if self.verbose:
                console.print_exception()
            sys.exit(1)
    
    def list_filters(self) -> None:
        """List available filters."""
        from .filters.base import pdf_filter_registry, svg_filter_registry
        
        # Initialize filters
        from .filters import (
            GrayscaleFilter,
            PDFCompressFilter,
            SVGOptimizeFilter,
            SVGTransparentWhiteFilter,
        )
        
        pdf_filter_registry.register(GrayscaleFilter)
        pdf_filter_registry.register(PDFCompressFilter)
        svg_filter_registry.register(SVGOptimizeFilter)
        svg_filter_registry.register(SVGTransparentWhiteFilter)
        
        # Create table
        table = Table(title="Available Filters")
        table.add_column("Type", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description", style="white")
        
        # Add PDF filters
        for name, filter_class in pdf_filter_registry.get_all().items():
            filter_instance = filter_class()
            table.add_row("PDF", name, filter_instance.description)
        
        # Add SVG filters
        for name, filter_class in svg_filter_registry.get_all().items():
            filter_instance = filter_class()
            table.add_row("SVG", name, filter_instance.description)
        
        console.print(table)
    
    def version(self) -> None:
        """Show version information."""
        console.print(
            Panel(
                f"pdf2svg2pdf version {__version__}\n"
                f"Python {sys.version.split()[0]}",
                title="Version Information",
                border_style="blue",
            )
        )


def main() -> None:
    """Main entry point."""
    # Customize Fire output
    fire.core.Display = lambda lines, out: rprint(*lines, file=out)
    
    # Create and run CLI
    cli = PDF2SVG2PDFCLI()
    fire.Fire(cli)


if __name__ == "__main__":
    main()