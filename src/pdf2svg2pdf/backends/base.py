#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/backends/base.py
"""Base classes and registry for backends."""

from __future__ import annotations

import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger

from ..core.exceptions import BackendError, DependencyError
from ..types import BackendCapability, BackendName, PathLike

if TYPE_CHECKING:
    from ..config import Configuration


class Backend(ABC):
    """Abstract base class for all backends."""

    def __init__(self, config: Configuration | None = None) -> None:
        """Initialize backend with configuration.

        Args:
            config: Optional configuration
        """
        self.config = config
        self._available: bool | None = None

    @property
    @abstractmethod
    def name(self) -> BackendName:
        """Backend identifier."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> set[BackendCapability]:
        """Set of supported capabilities."""
        ...

    @property
    @abstractmethod
    def required_commands(self) -> list[str]:
        """List of required system commands."""
        ...

    def is_available(self) -> bool:
        """Check if backend is available on the system.

        Returns:
            True if all required commands are available
        """
        if self._available is None:
            self._available = all(
                shutil.which(cmd) is not None for cmd in self.required_commands
            )
            if not self._available:
                missing = [
                    cmd for cmd in self.required_commands if shutil.which(cmd) is None
                ]
                logger.warning(
                    f"Backend {self.name} is not available. "
                    f"Missing commands: {', '.join(missing)}"
                )
        return self._available

    async def check_health(self) -> tuple[bool, str]:
        """Check backend health and return status with message.

        Returns:
            Tuple of (is_healthy, message)
        """
        if not self.is_available():
            return False, f"Backend {self.name} is not available"

        # Try to run a simple command to verify the backend works
        try:
            for cmd in self.required_commands:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    return False, f"Command {cmd} failed: {result.stderr}"

            return True, f"Backend {self.name} is healthy"
        except Exception as e:
            return False, f"Health check failed: {e}"

    def _run_command(
        self,
        command: list[str],
        timeout: float | None = None,
        check: bool = True,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        """Run a command with error handling.

        Args:
            command: Command and arguments
            timeout: Optional timeout in seconds
            check: Whether to check return code
            **kwargs: Additional arguments for subprocess.run

        Returns:
            Completed process

        Raises:
            BackendError: If command fails
        """
        try:
            logger.debug(f"Running command: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout or self.config.processing.timeout_seconds
                if self.config
                else 300,
                check=False,
                **kwargs,
            )

            if check and result.returncode != 0:
                raise BackendError(
                    f"Command failed with exit code {result.returncode}",
                    backend_name=self.name,
                    operation=" ".join(command),
                    details={
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode,
                    },
                )

            return result
        except subprocess.TimeoutExpired as e:
            raise BackendError(
                f"Command timed out after {e.timeout} seconds",
                backend_name=self.name,
                operation=" ".join(command),
            ) from e
        except Exception as e:
            raise BackendError(
                f"Failed to run command: {e}",
                backend_name=self.name,
                operation=" ".join(command),
            ) from e

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...


class BackendRegistry:
    """Registry for backend implementations."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._backends: dict[BackendName, type[Backend]] = {}
        self._instances: dict[BackendName, Backend] = {}

    def register(self, backend_class: type[Backend]) -> None:
        """Register a backend class.

        Args:
            backend_class: Backend class to register
        """
        instance = backend_class()
        name = instance.name
        self._backends[name] = backend_class
        logger.debug(f"Registered backend: {name}")

    def get(
        self,
        name: BackendName,
        config: Configuration | None = None,
    ) -> Backend:
        """Get a backend instance.

        Args:
            name: Backend name
            config: Optional configuration

        Returns:
            Backend instance

        Raises:
            BackendError: If backend not found
        """
        if name not in self._backends:
            raise BackendError(
                f"Backend not found: {name}",
                backend_name=name,
                details={"available": list(self._backends.keys())},
            )

        # Create instance if needed
        if name not in self._instances:
            self._instances[name] = self._backends[name](config)

        return self._instances[name]

    def get_available(
        self,
        capability: BackendCapability | None = None,
        config: Configuration | None = None,
    ) -> list[Backend]:
        """Get all available backends.

        Args:
            capability: Optional capability filter
            config: Optional configuration

        Returns:
            List of available backend instances
        """
        backends = []

        for name in self._backends:
            try:
                backend = self.get(name, config)
                if backend.is_available() and (
                    capability is None or capability in backend.capabilities
                ):
                    backends.append(backend)
            except Exception as e:
                logger.warning(f"Failed to check backend {name}: {e}")

        return backends

    def find_best(
        self,
        capability: BackendCapability,
        config: Configuration | None = None,
    ) -> Backend:
        """Find the best available backend for a capability.

        Args:
            capability: Required capability
            config: Optional configuration

        Returns:
            Best available backend

        Raises:
            DependencyError: If no backend available
        """
        available = self.get_available(capability, config)

        if not available:
            raise DependencyError(
                f"No backend available for capability: {capability}",
                dependency=f"backend with {capability}",
                install_command="Please install poppler-utils or pymupdf",
            )

        # Sort by priority if config provided
        if config and config.backends:
            priority_map = {
                bc.name: bc.priority for bc in config.backends if bc.enabled
            }
            available.sort(
                key=lambda b: priority_map.get(b.name, 0),
                reverse=True,
            )

        return available[0]


# Global registry instance
registry = BackendRegistry()
