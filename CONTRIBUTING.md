# Contributing to pdf2svg2pdf

Thank you for your interest in contributing to pdf2svg2pdf! This document provides guidelines and information for contributors.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- External dependencies (see README.md for installation instructions):
  - poppler-utils (pdfseparate, pdfunite, pdftocairo)
  - cairosvg
  - ghostscript (optional, for some filters)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/pdf2svg2pdf.git
   cd pdf2svg2pdf
   ```

2. **Set up development environment**
   ```bash
   # Use our development setup script
   ./scripts/local-install.sh --dev
   
   # Or manually:
   python -m pip install --upgrade pip
   pip install -e .[testing]
   pip install black isort flake8 pytest pytest-cov pre-commit
   pre-commit install
   ```

3. **Verify installation**
   ```bash
   pytest tests/
   pdf2svg2pdf --help
   ```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_pdf2svg2pdf.py

# Run with verbose output
pytest -v

# Run integration tests (requires external tools)
pytest tests/test_integration.py
```

### Test Structure

- `tests/test_pdf2svg2pdf.py` - Main module tests
- `tests/test_classic.py` - Classic module tests
- `tests/test_integration.py` - Integration tests (may be skipped if external tools unavailable)

### Writing Tests

- Follow pytest conventions
- Use descriptive test names
- Include docstrings for complex tests
- Mock external dependencies when possible
- Test both success and error cases

## Code Style

This project uses several tools to maintain code quality:

### Formatting
- **Black**: Code formatting
- **isort**: Import sorting

### Linting
- **flake8**: General linting
- **bandit**: Security scanning
- **mypy**: Type checking

### Pre-commit Hooks
Pre-commit hooks automatically run these tools. Install them with:
```bash
pre-commit install
```

### Manual Code Quality Checks
```bash
# Format code
black src tests
isort src tests

# Check linting
flake8 src tests

# Security scan
bandit -r src

# Type checking
mypy src
```

## Submitting Changes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the style guidelines
   - Add or update tests
   - Update documentation if needed

3. **Test your changes**
   ```bash
   ./scripts/test.sh
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Guidelines
- Use imperative mood ("Add feature" not "Added feature")
- Keep first line under 50 characters
- Reference issues when applicable
- Include more details in the body if needed

### Pull Request Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated
- [ ] Pre-commit hooks pass

## Release Process

### For Maintainers

1. **Prepare release**
   ```bash
   # Update CHANGELOG.md
   # Ensure all tests pass
   ./scripts/test.sh
   
   # Build package
   ./scripts/build.sh
   ```

2. **Create release**
   ```bash
   ./scripts/release.sh --version 1.2.3 --push
   ```

3. **Verify release**
   - Check GitHub Actions completion
   - Verify PyPI package
   - Test binary downloads

### Versioning
This project uses [Semantic Versioning](https://semver.org/):
- MAJOR: Incompatible API changes
- MINOR: New functionality, backwards compatible
- PATCH: Bug fixes, backwards compatible

## Development Guidelines

### Code Organization
- Keep modules focused and single-purpose
- Use type hints where appropriate
- Write docstrings for public functions
- Handle errors gracefully

### Dependencies
- Minimize external dependencies
- Pin versions in requirements files
- Document system dependencies clearly

### Performance
- Consider memory usage for large files
- Profile code for bottlenecks
- Use appropriate data structures

### Security
- Never commit secrets or keys
- Validate user inputs
- Use secure file operations
- Run security scans regularly

## Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check README.md and docstrings
- **Code**: Look at existing code for patterns and examples

## License

By contributing to pdf2svg2pdf, you agree that your contributions will be licensed under the Apache-2.0 License.

## Recognition

Contributors are automatically recognized in the AUTHORS.md file and GitHub contributors list.

Thank you for contributing to pdf2svg2pdf! 🎉