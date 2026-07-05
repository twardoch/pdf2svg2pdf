# Makefile for pdf2svg2pdf
# this_file: Makefile

.PHONY: help install install-dev test test-all build clean lint format security release release-dry docs

# Default target
help:
	@echo "pdf2svg2pdf - Build and Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  install      - Install package in production mode"
	@echo "  install-dev  - Install package in development mode"
	@echo "  test         - Run tests"
	@echo "  test-all     - Run all tests including integration"
	@echo "  build        - Build package"
	@echo "  clean        - Clean build artifacts"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code"
	@echo "  security     - Run security scans"
	@echo "  release      - Create release (requires VERSION=x.y.z)"
	@echo "  release-dry  - Dry run release (requires VERSION=x.y.z)"
	@echo "  docs         - Generate documentation"
	@echo ""
	@echo "Usage examples:"
	@echo "  make install-dev"
	@echo "  make test"
	@echo "  make build"
	@echo "  make release VERSION=1.2.3"

# Installation targets
install:
	@echo "🏠 Installing pdf2svg2pdf..."
	./scripts/local-install.sh

install-dev:
	@echo "🔧 Installing pdf2svg2pdf in development mode..."
	./scripts/local-install.sh --dev

# Testing targets
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

test-all:
	@echo "🧪 Running all tests including integration..."
	./scripts/test.sh

# Build targets
build:
	@echo "🏗️ Building package..."
	./scripts/build.sh

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Code quality targets
lint:
	@echo "🔍 Running linting checks..."
	ruff check src tests
	ruff format --check src tests
	mypy src/pdf2svg2pdf

format:
	@echo "✨ Formatting code..."
	ruff check --fix src tests
	ruff format src tests

# Release targets
release:
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ VERSION is required. Use: make release VERSION=1.2.3"; \
		exit 1; \
	fi
	@echo "🚀 Creating release $(VERSION)..."
	./scripts/release.sh --version $(VERSION) --push

release-dry:
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ VERSION is required. Use: make release-dry VERSION=1.2.3"; \
		exit 1; \
	fi
	@echo "🚀 Dry run release $(VERSION)..."
	./scripts/release.sh --version $(VERSION) --dry-run

# Documentation targets
docs:
	@echo "📚 Generating documentation..."
	@echo "Documentation is in README.md, CONTRIBUTING.md, and docs/ directory"
	@echo "To build Sphinx docs, run: cd docs && make html"

# Pre-commit targets
pre-commit:
	@echo "🪝 Running pre-commit hooks..."
	pre-commit run --all-files

pre-commit-install:
	@echo "🪝 Installing pre-commit hooks..."
	pre-commit install

# Development workflow targets
setup: install-dev pre-commit-install
	@echo "🎉 Development setup complete!"

check: lint test
	@echo "✅ All checks passed!"

# CI/CD simulation
ci: clean lint test build
	@echo "🎯 CI simulation complete!"

# Show project info
info:
	@echo "📋 Project Information:"
	@echo "  Name: pdf2svg2pdf"
	@echo "  Version: $(shell python -c 'import src.pdf2svg2pdf; print(src.pdf2svg2pdf.__version__)')"
	@echo "  Python: $(shell python --version)"
	@echo "  Location: $(shell pwd)"
	@echo "  Git Branch: $(shell git branch --show-current)"
	@echo "  Git Status: $(shell git status --porcelain | wc -l) modified files"

# Quick development cycle
dev: clean format lint test
	@echo "🔄 Development cycle complete!"