#!/usr/bin/env python3
# this_file: src/pdf2svg2pdf/config.py
"""Configuration management for pdf2svg2pdf."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from .core.exceptions import ConfigurationError, ValidationError
from .types import BackendConfig, FilterConfig, PathLike


@dataclass
class ProcessingConfig:
    """Configuration for processing operations."""

    parallel_pages: int = 4
    max_memory_mb: int = 1024
    timeout_seconds: float = 300.0
    retry_count: int = 3
    retry_delay_seconds: float = 1.0
    cleanup_on_error: bool = True
    preserve_temp_files: bool = False
    progress_updates: bool = True


@dataclass
class SecurityConfig:
    """Security configuration."""

    validate_paths: bool = True
    allow_symlinks: bool = False
    max_file_size_mb: int = 500
    allowed_extensions: set[str] = field(default_factory=lambda: {".pdf", ".svg"})
    sanitize_svg: bool = True
    temp_dir_permissions: int = 0o700


@dataclass
class CacheConfig:
    """Cache configuration."""

    enabled: bool = True
    directory: Path | None = None
    max_size_mb: int = 1024
    ttl_seconds: int = 86400  # 24 hours
    compression: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    format: str = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    )
    file: Path | None = None
    rotation: str = "10 MB"
    retention: str = "7 days"
    backtrace: bool = True
    diagnose: bool = True


@dataclass
class Configuration:
    """Main configuration class."""

    # Processing settings
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)

    # Security settings
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # Cache settings
    cache: CacheConfig = field(default_factory=CacheConfig)

    # Logging settings
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Backend configurations
    backends: list[BackendConfig] = field(default_factory=list)

    # Filter configurations
    pdf_filters: list[FilterConfig] = field(default_factory=list)
    svg_filters: list[FilterConfig] = field(default_factory=list)

    # Output settings
    output_suffix: str = "-converted"
    output_format: str = "pdf"
    compress_output: bool = True

    @classmethod
    def from_file(cls, path: PathLike) -> Configuration:
        """Load configuration from file.

        Args:
            path: Path to configuration file (YAML or TOML)

        Returns:
            Configuration instance

        Raises:
            ConfigurationError: If file cannot be loaded
        """
        path = Path(path)
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")

        try:
            with open(path) as f:
                if path.suffix in {".yaml", ".yml"}:
                    data = yaml.safe_load(f)
                elif path.suffix == ".toml":
                    import tomllib

                    data = tomllib.loads(f.read())
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration format: {path.suffix}"
                    )

            return cls.from_dict(data)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration from {path}: {e}"
            ) from e

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Configuration:
        """Create configuration from dictionary.

        Args:
            data: Configuration data

        Returns:
            Configuration instance
        """
        config = cls()

        # Load processing config
        if "processing" in data:
            config.processing = ProcessingConfig(**data["processing"])

        # Load security config
        if "security" in data:
            sec_data = data["security"].copy()
            if "allowed_extensions" in sec_data:
                sec_data["allowed_extensions"] = set(sec_data["allowed_extensions"])
            config.security = SecurityConfig(**sec_data)

        # Load cache config
        if "cache" in data:
            cache_data = data["cache"].copy()
            if "directory" in cache_data and cache_data["directory"]:
                cache_data["directory"] = Path(cache_data["directory"])
            config.cache = CacheConfig(**cache_data)

        # Load logging config
        if "logging" in data:
            log_data = data["logging"].copy()
            if "file" in log_data and log_data["file"]:
                log_data["file"] = Path(log_data["file"])
            config.logging = LoggingConfig(**log_data)

        # Load backends
        if "backends" in data:
            config.backends = [BackendConfig(**backend) for backend in data["backends"]]

        # Load filters
        if "pdf_filters" in data:
            config.pdf_filters = [FilterConfig(**f) for f in data["pdf_filters"]]
        if "svg_filters" in data:
            config.svg_filters = [FilterConfig(**f) for f in data["svg_filters"]]

        # Load other settings
        config.output_suffix = data.get("output_suffix", config.output_suffix)
        config.output_format = data.get("output_format", config.output_format)
        config.compress_output = data.get("compress_output", config.compress_output)

        return config

    @classmethod
    def from_env(cls) -> Configuration:
        """Create configuration from environment variables.

        Returns:
            Configuration instance
        """
        config = cls()

        # Processing settings
        if val := os.getenv("PDF2SVG2PDF_PARALLEL_PAGES"):
            config.processing.parallel_pages = int(val)
        if val := os.getenv("PDF2SVG2PDF_MAX_MEMORY_MB"):
            config.processing.max_memory_mb = int(val)
        if val := os.getenv("PDF2SVG2PDF_TIMEOUT_SECONDS"):
            config.processing.timeout_seconds = float(val)

        # Security settings
        if val := os.getenv("PDF2SVG2PDF_VALIDATE_PATHS"):
            config.security.validate_paths = val.lower() in ("true", "1", "yes")
        if val := os.getenv("PDF2SVG2PDF_MAX_FILE_SIZE_MB"):
            config.security.max_file_size_mb = int(val)

        # Cache settings
        if val := os.getenv("PDF2SVG2PDF_CACHE_ENABLED"):
            config.cache.enabled = val.lower() in ("true", "1", "yes")
        if val := os.getenv("PDF2SVG2PDF_CACHE_DIR"):
            config.cache.directory = Path(val)

        # Logging settings
        if val := os.getenv("PDF2SVG2PDF_LOG_LEVEL"):
            config.logging.level = val.upper()
        if val := os.getenv("PDF2SVG2PDF_LOG_FILE"):
            config.logging.file = Path(val)

        return config

    def merge(self, other: Configuration) -> Configuration:
        """Merge with another configuration.

        Args:
            other: Configuration to merge with

        Returns:
            New merged configuration
        """
        # This is a simple merge - could be enhanced with deep merging
        merged = Configuration()

        # Copy from self first
        merged.processing = self.processing
        merged.security = self.security
        merged.cache = self.cache
        merged.logging = self.logging
        merged.backends = self.backends.copy()
        merged.pdf_filters = self.pdf_filters.copy()
        merged.svg_filters = self.svg_filters.copy()
        merged.output_suffix = self.output_suffix
        merged.output_format = self.output_format
        merged.compress_output = self.compress_output

        # Override with other
        if other.processing != ProcessingConfig():
            merged.processing = other.processing
        if other.security != SecurityConfig():
            merged.security = other.security
        if other.cache != CacheConfig():
            merged.cache = other.cache
        if other.logging != LoggingConfig():
            merged.logging = other.logging
        if other.backends:
            merged.backends = other.backends
        if other.pdf_filters:
            merged.pdf_filters = other.pdf_filters
        if other.svg_filters:
            merged.svg_filters = other.svg_filters
        if other.output_suffix != "-converted":
            merged.output_suffix = other.output_suffix
        if other.output_format != "pdf":
            merged.output_format = other.output_format

        return merged

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValidationError: If configuration is invalid
        """
        # Validate processing settings
        if self.processing.parallel_pages < 1:
            raise ValidationError(
                "parallel_pages must be at least 1",
                field="processing.parallel_pages",
                value=self.processing.parallel_pages,
            )

        if self.processing.max_memory_mb < 64:
            raise ValidationError(
                "max_memory_mb must be at least 64",
                field="processing.max_memory_mb",
                value=self.processing.max_memory_mb,
            )

        # Validate security settings
        if self.security.max_file_size_mb < 1:
            raise ValidationError(
                "max_file_size_mb must be at least 1",
                field="security.max_file_size_mb",
                value=self.security.max_file_size_mb,
            )

        # Validate cache settings
        if (
            self.cache.enabled
            and self.cache.directory
            and not self.cache.directory.parent.exists()
        ):
            raise ValidationError(
                f"Cache directory parent does not exist: {self.cache.directory.parent}",
                field="cache.directory",
                value=str(self.cache.directory),
            )

        # Validate output format
        if self.output_format not in {"pdf", "svg"}:
            raise ValidationError(
                f"Invalid output format: {self.output_format}",
                field="output_format",
                value=self.output_format,
            )

        # Validate backends
        if not self.backends:
            # Add default backends if none specified
            self.backends = [
                BackendConfig(name="poppler", priority=100),
                BackendConfig(name="fitz", priority=90),
                BackendConfig(name="cairo", priority=80),
            ]

        # Validate filters have unique names
        pdf_filter_names = {f.name for f in self.pdf_filters}
        if len(pdf_filter_names) != len(self.pdf_filters):
            raise ValidationError("Duplicate PDF filter names found")

        svg_filter_names = {f.name for f in self.svg_filters}
        if len(svg_filter_names) != len(self.svg_filters):
            raise ValidationError("Duplicate SVG filter names found")

    def setup_logging(self) -> None:
        """Set up logging based on configuration."""
        logger.remove()  # Remove default handler

        # Add console handler
        logger.add(
            sink=lambda msg: print(msg, end=""),
            format=self.logging.format,
            level=self.logging.level,
            backtrace=self.logging.backtrace,
            diagnose=self.logging.diagnose,
        )

        # Add file handler if specified
        if self.logging.file:
            logger.add(
                sink=self.logging.file,
                format=self.logging.format,
                level=self.logging.level,
                rotation=self.logging.rotation,
                retention=self.logging.retention,
                backtrace=self.logging.backtrace,
                diagnose=self.logging.diagnose,
            )


def load_configuration(
    config_file: PathLike | None = None,
    use_env: bool = True,
) -> Configuration:
    """Load configuration from multiple sources.

    Args:
        config_file: Optional configuration file path
        use_env: Whether to load from environment variables

    Returns:
        Loaded and validated configuration
    """
    # Start with defaults
    config = Configuration()

    # Load from file if provided
    if config_file:
        file_config = Configuration.from_file(config_file)
        config = config.merge(file_config)

    # Load from environment if enabled
    if use_env:
        env_config = Configuration.from_env()
        config = config.merge(env_config)

    # Validate final configuration
    config.validate()

    return config
