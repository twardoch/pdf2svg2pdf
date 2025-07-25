#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/utils/security.py
"""Security utilities."""

from __future__ import annotations

import os
import re
from pathlib import Path

from ..core.exceptions import ValidationError
from ..types import PathLike


def sanitize_path(path: PathLike) -> Path:
    """Sanitize a file path for security.
    
    Args:
        path: Path to sanitize
        
    Returns:
        Sanitized path
        
    Raises:
        ValidationError: If path is invalid
    """
    path = Path(path)
    
    # Remove any null bytes
    path_str = str(path).replace("\0", "")
    
    # Normalize the path
    path = Path(path_str).resolve()
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r"\.\./",  # Parent directory traversal
        r"^\.",    # Hidden files
        r"~",      # Home directory expansion
        r"\$",     # Variable expansion
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, str(path)):
            raise ValidationError(
                f"Suspicious path pattern detected: {pattern}",
                field="path",
                value=str(path),
            )
    
    return path


def check_path_traversal(
    path: PathLike,
    base_dir: PathLike,
) -> None:
    """Check for path traversal attacks.
    
    Args:
        path: Path to check
        base_dir: Base directory that path should be within
        
    Raises:
        ValidationError: If path traversal detected
    """
    path = Path(path).resolve()
    base_dir = Path(base_dir).resolve()
    
    try:
        path.relative_to(base_dir)
    except ValueError:
        raise ValidationError(
            f"Path traversal detected: {path} is outside {base_dir}",
            field="path",
            value=str(path),
            details={"base_dir": str(base_dir)},
        )


def sanitize_svg_content(content: str) -> str:
    """Sanitize SVG content for security.
    
    Args:
        content: SVG content
        
    Returns:
        Sanitized content
    """
    # Remove potentially dangerous elements
    dangerous_patterns = [
        (r"<script[^>]*>.*?</script>", ""),  # Scripts
        (r"<embed[^>]*>", ""),               # Embedded content
        (r"<object[^>]*>.*?</object>", ""),  # Objects
        (r"<iframe[^>]*>.*?</iframe>", ""),  # Iframes
        (r"on\w+\s*=\s*[\"'].*?[\"']", ""), # Event handlers
        (r"javascript:", ""),                 # JavaScript URLs
        (r"data:text/html", ""),             # Data URLs with HTML
    ]
    
    sanitized = content
    for pattern, replacement in dangerous_patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized


def validate_command_args(args: list[str]) -> None:
    """Validate command arguments for security.
    
    Args:
        args: Command arguments
        
    Raises:
        ValidationError: If arguments are invalid
    """
    dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "{", "}", "[", "]", "<", ">"]
    
    for arg in args:
        for char in dangerous_chars:
            if char in arg:
                raise ValidationError(
                    f"Dangerous character '{char}' in command argument",
                    field="command_arg",
                    value=arg,
                )


def create_secure_temp_dir(prefix: str = "pdf2svg2pdf_") -> Path:
    """Create a secure temporary directory.
    
    Args:
        prefix: Directory name prefix
        
    Returns:
        Path to secure temporary directory
    """
    import tempfile
    
    # Create with restrictive permissions
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    path = Path(temp_dir)
    
    # Set secure permissions (owner only)
    os.chmod(path, 0o700)
    
    return path