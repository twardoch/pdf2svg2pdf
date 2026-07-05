#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/core/exceptions.py
"""Custom exceptions for pdf2svg2pdf."""

from __future__ import annotations

from typing import Any


class PDF2SVG2PDFError(Exception):
    """Base exception for all pdf2svg2pdf errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize exception with message and optional details.

        Args:
            message: Error message
            details: Additional error context
        """
        super().__init__(message)
        self.details = details or {}


class BackendError(PDF2SVG2PDFError):
    """Error related to backend operations."""

    def __init__(
        self,
        message: str,
        backend_name: str,
        operation: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize backend error.

        Args:
            message: Error message
            backend_name: Name of the backend that failed
            operation: Operation that failed
            details: Additional error context
        """
        super().__init__(message, details)
        self.backend_name = backend_name
        self.operation = operation


class FilterError(PDF2SVG2PDFError):
    """Error related to filter operations."""

    def __init__(
        self,
        message: str,
        filter_name: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize filter error.

        Args:
            message: Error message
            filter_name: Name of the filter that failed
            details: Additional error context
        """
        super().__init__(message, details)
        self.filter_name = filter_name


class ValidationError(PDF2SVG2PDFError):
    """Error related to input validation."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
            details: Additional error context
        """
        super().__init__(message, details)
        self.field = field
        self.value = value


class ConfigurationError(PDF2SVG2PDFError):
    """Error related to configuration."""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            config_key: Configuration key that caused the error
            details: Additional error context
        """
        super().__init__(message, details)
        self.config_key = config_key


class DependencyError(PDF2SVG2PDFError):
    """Error related to missing dependencies."""

    def __init__(
        self,
        message: str,
        dependency: str,
        install_command: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize dependency error.

        Args:
            message: Error message
            dependency: Name of missing dependency
            install_command: Command to install the dependency
            details: Additional error context
        """
        super().__init__(message, details)
        self.dependency = dependency
        self.install_command = install_command


class ProcessingError(PDF2SVG2PDFError):
    """Error during processing pipeline."""

    def __init__(
        self,
        message: str,
        page_number: int | None = None,
        stage: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize processing error.

        Args:
            message: Error message
            page_number: Page number where error occurred
            stage: Processing stage where error occurred
            details: Additional error context
        """
        super().__init__(message, details)
        self.page_number = page_number
        self.stage = stage


class TimeoutError(PDF2SVG2PDFError):
    """Operation timed out."""

    def __init__(
        self,
        message: str,
        operation: str,
        timeout_seconds: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize timeout error.

        Args:
            message: Error message
            operation: Operation that timed out
            timeout_seconds: Timeout duration
            details: Additional error context
        """
        super().__init__(message, details)
        self.operation = operation
        self.timeout_seconds = timeout_seconds
