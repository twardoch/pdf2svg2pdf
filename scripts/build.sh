#!/bin/bash
# this_file: scripts/build.sh
# Build script for pdf2svg2pdf

set -e

echo "🔧 Building pdf2svg2pdf..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/ src/*.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
python -m pip install --upgrade pip
python -m pip install build setuptools-scm wheel

# Build the package
echo "🏗️ Building package..."
python -m build

# Verify the build
echo "✅ Build completed successfully!"
echo "📄 Generated files:"
ls -la dist/

# Optional: Show package info
echo "📋 Package info:"
python -m pip show pdf2svg2pdf || echo "Package not installed yet"

echo "🎉 Build complete!"