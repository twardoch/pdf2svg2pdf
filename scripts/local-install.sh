#!/bin/bash
# this_file: scripts/local-install.sh
# Local installation script for pdf2svg2pdf

set -e

echo "🏠 Local installation script for pdf2svg2pdf"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Parse command line arguments
DEV_MODE=false
FORCE_REINSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dev)
            DEV_MODE=true
            shift
            ;;
        -f|--force)
            FORCE_REINSTALL=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -d, --dev     Install in development mode"
            echo "  -f, --force   Force reinstallation"
            echo "  -h, --help    Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "📋 Installation Configuration:"
echo "  Development mode: $DEV_MODE"
echo "  Force reinstall: $FORCE_REINSTALL"
echo ""

# Uninstall existing version if force reinstall
if [ "$FORCE_REINSTALL" = true ]; then
    echo "🗑️ Uninstalling existing version..."
    python -m pip uninstall pdf2svg2pdf -y || true
fi

# Install dependencies
echo "📦 Installing dependencies..."
python -m pip install --upgrade pip setuptools wheel

if [ "$DEV_MODE" = true ]; then
    echo "🔧 Installing in development mode..."
    python -m pip install -e .[testing]
    
    # Install development tools
    echo "🛠️ Installing development tools..."
    python -m pip install black isort flake8 pytest pytest-cov pre-commit
    
    # Install pre-commit hooks
    echo "🪝 Installing pre-commit hooks..."
    pre-commit install
else
    echo "📦 Installing in production mode..."
    python -m pip install .
fi

# Verify installation
echo "✅ Verifying installation..."
python -c "import pdf2svg2pdf; print(f'pdf2svg2pdf version: {pdf2svg2pdf.__version__}')"

# Test CLI
echo "🖥️ Testing CLI..."
pdf2svg2pdf --help
pdf2svg2pdf --version

echo ""
echo "🎉 Installation completed successfully!"
echo ""
if [ "$DEV_MODE" = true ]; then
    echo "🔧 Development mode enabled:"
    echo "  - Editable installation (changes reflect immediately)"
    echo "  - Testing dependencies installed"
    echo "  - Pre-commit hooks installed"
    echo "  - Run tests with: pytest"
    echo "  - Format code with: black src tests"
    echo "  - Sort imports with: isort src tests"
    echo "  - Lint code with: flake8 src tests"
fi
echo ""
echo "📚 Usage:"
echo "  pdf2svg2pdf input.pdf --outdir output/"
echo "  python -m pdf2svg2pdf.pdf2svg2pdf_classic input.pdf --outdir output/"