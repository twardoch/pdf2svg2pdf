# Deployment Guide for pdf2svg2pdf

This document explains how to deploy and use the complete git-tag-based semversioning system for pdf2svg2pdf.

## Overview

The project now includes:
- ✅ Git-tag-based semantic versioning with setuptools-scm
- ✅ Comprehensive test suite (pytest)
- ✅ Build, test, and release scripts
- ✅ GitHub Actions CI/CD pipeline
- ✅ Multiplatform binary releases
- ✅ Pre-commit hooks for code quality
- ✅ Security scanning
- ✅ Automated PyPI publishing

## Quick Start

### 1. Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/pdf2svg2pdf.git
cd pdf2svg2pdf

# Set up development environment
./scripts/local-install.sh --dev

# Or use Make
make install-dev
```

### 2. Running Tests

```bash
# Run tests
./scripts/test.sh

# Or use Make
make test

# Run specific test types
pytest tests/test_pdf2svg2pdf.py -v
pytest tests/test_integration.py -v  # Requires external tools
```

### 3. Building

```bash
# Build package
./scripts/build.sh

# Or use Make
make build
```

### 4. Creating a Release

```bash
# Create a release (replace 1.2.3 with your version)
./scripts/release.sh --version 1.2.3 --push

# Or use Make
make release VERSION=1.2.3

# Dry run first
./scripts/release.sh --version 1.2.3 --dry-run
make release-dry VERSION=1.2.3
```

## GitHub Actions Workflow

The CI/CD pipeline runs on:
- Push to main/develop branches
- Pull requests to main
- Git tags matching v*
- Manual trigger

### Jobs:

1. **Prepare**: Lint, build, version detection
2. **Test**: Multi-platform testing (Linux, macOS, Windows) across Python 3.8-3.12
3. **Build Binaries**: Create standalone executables
4. **Security**: Safety and bandit scans
5. **Release**: Create GitHub release and publish to PyPI (on tags)
6. **Notify**: Workflow summary

## Release Process

### Manual Release

1. **Prepare your changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin main
   ```

2. **Create and push tag**
   ```bash
   git tag -a v1.2.3 -m "Release v1.2.3"
   git push origin v1.2.3
   ```

3. **Monitor GitHub Actions**
   - Tests run across all platforms
   - Binaries are built
   - Release is created on GitHub
   - Package is published to PyPI

### Automated Release

Use the release script:
```bash
./scripts/release.sh --version 1.2.3 --push
```

This will:
- Run tests
- Build package
- Create git tag
- Push to remote
- Trigger GitHub Actions

## Version Management

The project uses setuptools-scm for automatic version detection:

- **Development**: `1.2.3.dev0+g1234567` (uncommitted changes)
- **Tagged**: `1.2.3` (exact tag)
- **Post-release**: `1.2.3.post0+g1234567` (commits after tag)

### Version Sources:
1. Git tags (primary)
2. Distance from last tag
3. Commit hash
4. Dirty working directory

## File Structure

```
pdf2svg2pdf/
├── .github/workflows/ci.yml    # GitHub Actions CI/CD
├── scripts/                    # Build and release scripts
│   ├── build.sh
│   ├── test.sh
│   ├── release.sh
│   └── local-install.sh
├── tests/                      # Test suite
│   ├── test_pdf2svg2pdf.py
│   ├── test_classic.py
│   └── test_integration.py
├── src/pdf2svg2pdf/           # Source code
├── pyproject.toml             # Build configuration
├── setup.cfg                  # Package configuration
├── .pre-commit-config.yaml    # Pre-commit hooks
├── Makefile                   # Convenience commands
├── CHANGELOG.md               # Change log
├── CONTRIBUTING.md            # Contribution guidelines
└── DEPLOYMENT.md              # This file
```

## Key Features

### 1. Git-Tag-Based Versioning
- Automatic version detection from git tags
- Semantic versioning (MAJOR.MINOR.PATCH)
- Development version suffixes

### 2. Comprehensive Testing
- Unit tests for all modules
- Integration tests (requires external tools)
- Mock tests for external dependencies
- Coverage reporting

### 3. Build Scripts
- `scripts/build.sh`: Build packages
- `scripts/test.sh`: Run test suite
- `scripts/release.sh`: Create releases
- `scripts/local-install.sh`: Local installation

### 4. GitHub Actions
- Multi-platform testing
- Binary artifact creation
- Security scanning
- Automated releases
- PyPI publishing

### 5. Code Quality
- Pre-commit hooks
- Black formatting
- isort import sorting
- flake8 linting
- bandit security scanning
- mypy type checking

## Environment Variables

### GitHub Actions
- `GITHUB_TOKEN`: Automatically provided
- `PYPI_TOKEN`: Add to repository secrets for PyPI publishing

### Local Development
- `PYTEST_CURRENT_TEST`: Set by pytest
- `CI`: Set in CI environment

## Troubleshooting

### Common Issues

1. **Version shows 'unknown'**
   - No git tags present
   - Not in a git repository
   - setuptools-scm not installed

2. **Tests fail with 'external tools not available'**
   - Install poppler-utils, cairosvg, ghostscript
   - Some tests are skipped if tools are missing

3. **Build fails**
   - Check Python version (3.8+)
   - Install build dependencies
   - Verify git repository state

4. **Release fails**
   - Check git working directory is clean
   - Verify version format (MAJOR.MINOR.PATCH)
   - Ensure tag doesn't already exist

### Debug Commands

```bash
# Check version detection
python -c "import setuptools_scm; print(setuptools_scm.get_version())"

# Check git tags
git tag -l

# Check git status
git status

# Test imports
python -c "import pdf2svg2pdf; print(pdf2svg2pdf.__version__)"

# Run specific test
pytest tests/test_pdf2svg2pdf.py::TestPDF2SVG2PDF::test_version_available -v
```

## Next Steps

1. **Set up PyPI token** in GitHub repository secrets
2. **Create first release** with `./scripts/release.sh --version 0.1.0 --push`
3. **Monitor GitHub Actions** for successful CI/CD
4. **Verify package** is available on PyPI
5. **Test installation** with `pip install pdf2svg2pdf`

## Support

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and community support
- Documentation: README.md and CONTRIBUTING.md