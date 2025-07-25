# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Major Refactoring
- Complete architectural refactoring with modern Python 3.12+ patterns
- New modular structure with clear separation of concerns:
  - `core/` - Main converter and pipeline logic
  - `backends/` - Pluggable backend implementations (Poppler, Fitz, Cairo)
  - `filters/` - Extensible filter system for PDF and SVG transformations
  - `utils/` - Comprehensive utilities for I/O, validation, security, and async operations
- Rich CLI interface with progress bars and beautiful formatting
- Comprehensive configuration management system:
  - Support for YAML/TOML configuration files
  - Environment variable overrides
  - Validation and merging of configurations
- Security enhancements:
  - Input sanitization and validation
  - Path traversal protection
  - Secure subprocess execution (no more shell=True)
  - SVG content sanitization
- Async/await support throughout with sync wrappers
- Plugin architecture for backends and filters
- Comprehensive error handling with custom exception hierarchy
- Type hints throughout (mypy strict mode compatible)
- Loguru-based structured logging with correlation IDs
- Progress tracking and cancellation support
- Atomic file operations for safety
- Resource management with context managers
- New filters: grayscale, compress, optimize, transparent_white, color_replace, fill_unify

### Added - Infrastructure
- Git-tag-based semantic versioning with setuptools-scm
- Comprehensive test suite with pytest
- Build, test, and release scripts for local development
- GitHub Actions CI/CD pipeline with multiplatform support
- Binary artifact creation for Linux, macOS, and Windows
- Pre-commit hooks for code quality
- Security scanning with bandit and safety
- Coverage reporting with codecov
- Automated PyPI publishing on releases

### Changed
- Migrated from basic subprocess calls to secure command execution
- Unified PDF2SVG2PDF and pdf2svg2pdf_classic implementations
- Improved performance with parallel processing enhancements
- Enhanced CLI with rich formatting and interactive features
- Better error messages with context and recovery suggestions
- Updated pre-commit configuration with additional hooks
- Enhanced GitHub Actions workflow for better CI/CD
- Improved project structure for better maintainability
- Updated to Python 3.12+ with modern features

### Security
- Added comprehensive input validation
- Implemented secure temporary file handling
- Added command injection prevention
- SVG content sanitization to prevent XSS-like attacks
- Path traversal protection
- Secure file permissions for temporary files

### Fixed
- Various code quality improvements
- Better error handling and testing coverage
- Resource cleanup on errors
- Memory efficiency improvements

## [0.1.0] - Initial Release
- Basic PDF to SVG to PDF conversion functionality
- Command-line interface
- Python library interface
- Support for filters and modifications