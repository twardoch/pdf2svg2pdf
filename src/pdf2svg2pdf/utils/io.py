#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/utils/io.py
"""I/O utility functions."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from loguru import logger

from ..types import PathLike


def ensure_directory(path: PathLike, mode: int = 0o755) -> Path:
    """Ensure directory exists with proper permissions.

    Args:
        path: Directory path
        mode: Directory permissions

    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True, mode=mode)
    return path


@contextmanager
def safe_temp_directory(
    prefix: str = "pdf2svg2pdf_",
    cleanup: bool = True,
) -> Generator[Path, None, None]:
    """Create a temporary directory with cleanup.

    Args:
        prefix: Directory name prefix
        cleanup: Whether to cleanup on exit

    Yields:
        Path to temporary directory
    """
    temp_dir = None
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        logger.debug(f"Created temporary directory: {temp_dir}")
        yield temp_dir
    finally:
        if temp_dir and cleanup and temp_dir.exists():
            import shutil

            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up temporary directory: {temp_dir}")


@contextmanager
def atomic_write(
    path: PathLike,
    mode: str = "w",
    encoding: str = "utf-8",
) -> Generator[Any, None, None]:
    """Write file atomically using a temporary file.

    Args:
        path: Target file path
        mode: File mode
        encoding: Text encoding

    Yields:
        File handle
    """
    path = Path(path)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )

    try:
        if "b" in mode:
            with os.fdopen(temp_fd, mode) as f:
                yield f
        else:
            with os.fdopen(temp_fd, mode, encoding=encoding) as f:
                yield f

        # Atomic rename
        os.replace(temp_path, path)
        logger.debug(f"Atomically wrote file: {path}")
    except Exception:
        # Clean up on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def get_file_size_mb(path: PathLike) -> float:
    """Get file size in megabytes.

    Args:
        path: File path

    Returns:
        Size in MB
    """
    path = Path(path)
    return path.stat().st_size / (1024 * 1024)


def read_file_chunked(
    path: PathLike,
    chunk_size: int = 8192,
) -> Generator[bytes, None, None]:
    """Read file in chunks.

    Args:
        path: File path
        chunk_size: Size of each chunk

    Yields:
        File chunks
    """
    path = Path(path)
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk
