#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/utils/validation.py
"""Input validation utilities."""

from __future__ import annotations

from pathlib import Path

from ..core.exceptions import ValidationError
from ..types import PathLike


def validate_path(
    path: PathLike,
    must_exist: bool = True,
    must_be_file: bool = False,
    must_be_dir: bool = False,
    allowed_extensions: set[str] | None = None,
) -> Path:
    """Validate a file path.

    Args:
        path: Path to validate
        must_exist: Whether path must exist
        must_be_file: Whether path must be a file
        must_be_dir: Whether path must be a directory
        allowed_extensions: Set of allowed file extensions

    Returns:
        Validated Path object

    Raises:
        ValidationError: If validation fails
    """
    path = Path(path)

    if must_exist and not path.exists():
        raise ValidationError(
            f"Path does not exist: {path}",
            field="path",
            value=str(path),
        )

    if must_be_file and path.exists() and not path.is_file():
        raise ValidationError(
            f"Path is not a file: {path}",
            field="path",
            value=str(path),
        )

    if must_be_dir and path.exists() and not path.is_dir():
        raise ValidationError(
            f"Path is not a directory: {path}",
            field="path",
            value=str(path),
        )

    if allowed_extensions and path.suffix.lower() not in allowed_extensions:
        raise ValidationError(
            f"Invalid file extension: {path.suffix}",
            field="extension",
            value=path.suffix,
            details={"allowed": list(allowed_extensions)},
        )

    return path


def validate_file_size(
    path: PathLike,
    max_size_mb: float,
) -> None:
    """Validate file size.

    Args:
        path: File path
        max_size_mb: Maximum size in megabytes

    Raises:
        ValidationError: If file is too large
    """
    path = Path(path)
    if not path.exists():
        return

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValidationError(
            f"File too large: {size_mb:.1f}MB (max: {max_size_mb}MB)",
            field="file_size",
            value=size_mb,
            details={"path": str(path), "max_size_mb": max_size_mb},
        )


def validate_page_range(
    start: int | None,
    end: int | None,
    total_pages: int,
) -> tuple[int, int]:
    """Validate and normalize page range.

    Args:
        start: Start page (1-indexed, inclusive)
        end: End page (1-indexed, inclusive)
        total_pages: Total number of pages

    Returns:
        Tuple of (start, end) normalized to 0-indexed

    Raises:
        ValidationError: If range is invalid
    """
    if start is None:
        start = 1
    if end is None:
        end = total_pages

    if start < 1 or start > total_pages:
        raise ValidationError(
            f"Invalid start page: {start} (total: {total_pages})",
            field="start_page",
            value=start,
        )

    if end < 1 or end > total_pages:
        raise ValidationError(
            f"Invalid end page: {end} (total: {total_pages})",
            field="end_page",
            value=end,
        )

    if start > end:
        raise ValidationError(
            f"Start page ({start}) is after end page ({end})",
            field="page_range",
            value=(start, end),
        )

    # Convert to 0-indexed
    return start - 1, end - 1
