#!/bin/bash
# this_file: scripts/test.sh
# Test script for pdf2svg2pdf

set -e

echo "🧪 Testing pdf2svg2pdf..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Install test dependencies
echo "📦 Installing test dependencies..."
python -m pip install --upgrade pip
python -m pip install -e .[testing]
python -m pip install pytest pytest-cov pytest-xdist reportlab

# Install external dependencies (if available)
echo "🔧 Checking external dependencies..."
if command -v apt-get &> /dev/null; then
    echo "🐧 Installing dependencies via apt-get..."
    sudo apt-get update
    sudo apt-get install -y poppler-utils cairosvg ghostscript
elif command -v brew &> /dev/null; then
    echo "🍺 Installing dependencies via brew..."
    brew install poppler cairo ghostscript
    pip install cairosvg
elif command -v dnf &> /dev/null; then
    echo "🎩 Installing dependencies via dnf..."
    sudo dnf install -y poppler-utils cairo ghostscript
    pip install cairosvg
else
    echo "⚠️  Could not install external dependencies automatically"
    echo "Please install poppler-utils, cairosvg, and ghostscript manually"
fi

# Run linting
echo "🔍 Running linting..."
python -m pip install flake8 black isort
python -m flake8 src tests
python -m black --check src tests
python -m isort --check-only src tests

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml

# Generate coverage report
echo "📊 Coverage report generated in htmlcov/"

# Test CLI
echo "🖥️  Testing CLI..."
python -m pdf2svg2pdf --help
python -m pdf2svg2pdf --version

echo "✅ All tests passed!"