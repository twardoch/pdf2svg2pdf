#!/bin/bash
# this_file: scripts/release.sh
# Release script for pdf2svg2pdf

set -e

echo "🚀 Release script for pdf2svg2pdf"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ Not in a git repository"
        exit 1
    fi
}

# Function to check if working directory is clean
check_clean_working_dir() {
    if [ -n "$(git status --porcelain)" ]; then
        echo "❌ Working directory is not clean. Please commit or stash changes."
        git status --short
        exit 1
    fi
}

# Function to get the current version
get_current_version() {
    python -c "
import sys
sys.path.insert(0, 'src')
from pdf2svg2pdf import __version__
print(__version__)
"
}

# Function to validate semantic version
validate_semver() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "❌ Invalid semantic version: $version"
        echo "Use format: MAJOR.MINOR.PATCH (e.g., 1.2.3)"
        exit 1
    fi
}

# Parse command line arguments
VERSION=""
PUSH_TO_REMOTE=false
SKIP_TESTS=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -p|--push)
            PUSH_TO_REMOTE=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -v, --version VERSION    Version to release (required)"
            echo "  -p, --push              Push to remote repository"
            echo "  --skip-tests            Skip running tests"
            echo "  --dry-run              Show what would be done without doing it"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$VERSION" ]; then
    echo "❌ Version is required. Use -v or --version to specify it."
    echo "Use '$0 --help' for more information."
    exit 1
fi

validate_semver "$VERSION"

echo "📋 Release Configuration:"
echo "  Version: $VERSION"
echo "  Push to remote: $PUSH_TO_REMOTE"
echo "  Skip tests: $SKIP_TESTS"
echo "  Dry run: $DRY_RUN"
echo ""

# Check git repository
check_git_repo

# Check working directory
check_clean_working_dir

# Get current version
CURRENT_VERSION=$(get_current_version)
echo "📦 Current version: $CURRENT_VERSION"
echo "📦 Release version: $VERSION"

# Check if tag already exists
if git tag -l | grep -q "^v$VERSION$"; then
    echo "❌ Tag v$VERSION already exists"
    exit 1
fi

# Run tests unless skipped
if [ "$SKIP_TESTS" = false ]; then
    echo "🧪 Running tests..."
    if [ "$DRY_RUN" = false ]; then
        "$SCRIPT_DIR/test.sh"
    else
        echo "  [DRY RUN] Would run: $SCRIPT_DIR/test.sh"
    fi
fi

# Build the package
echo "🏗️ Building package..."
if [ "$DRY_RUN" = false ]; then
    "$SCRIPT_DIR/build.sh"
else
    echo "  [DRY RUN] Would run: $SCRIPT_DIR/build.sh"
fi

# Create and push tag
echo "🏷️ Creating tag v$VERSION..."
if [ "$DRY_RUN" = false ]; then
    git tag -a "v$VERSION" -m "Release v$VERSION"
    echo "✅ Tag v$VERSION created"
else
    echo "  [DRY RUN] Would run: git tag -a v$VERSION -m \"Release v$VERSION\""
fi

# Push to remote if requested
if [ "$PUSH_TO_REMOTE" = true ]; then
    echo "📤 Pushing to remote..."
    if [ "$DRY_RUN" = false ]; then
        git push origin "v$VERSION"
        echo "✅ Tag pushed to remote"
    else
        echo "  [DRY RUN] Would run: git push origin v$VERSION"
    fi
fi

echo ""
echo "🎉 Release v$VERSION prepared successfully!"
echo ""
echo "Next steps:"
if [ "$PUSH_TO_REMOTE" = false ]; then
    echo "  1. Push the tag to trigger CI/CD: git push origin v$VERSION"
fi
echo "  2. Monitor GitHub Actions for the release process"
echo "  3. Check the generated release on GitHub"
echo "  4. Verify the package is published to PyPI"
echo ""
echo "📊 Release Summary:"
echo "  - Version: $VERSION"
echo "  - Tag: v$VERSION"
echo "  - Built packages: $(ls -1 dist/ | tr '\n' ' ')"
if [ "$DRY_RUN" = true ]; then
    echo "  - Mode: DRY RUN (no changes made)"
fi