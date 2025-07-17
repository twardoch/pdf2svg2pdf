# Setup Instructions for Git-Tag-Based Semversioning

## 🚨 Important: Manual Workflow Setup Required

Due to GitHub App permissions, the workflow file cannot be automatically committed. Please follow these steps to complete the setup:

## Step 1: Move the Workflow File

```bash
# Move the workflow file to the correct location
mv ci-workflow.yml .github/workflows/ci.yml

# Remove the original file
rm ci-workflow.yml
```

## Step 2: Commit the Workflow

```bash
# Add the workflow file
git add .github/workflows/ci.yml

# Commit the workflow
git commit -m "feat: add comprehensive CI/CD workflow with semversioning"

# Push to remote
git push origin terragon/implement-git-tag-semver-ci
```

## Step 3: Set Up PyPI Token (Optional)

If you want to publish to PyPI automatically:

1. Go to [PyPI](https://pypi.org) and create an API token
2. Go to your GitHub repository settings
3. Add a new secret named `PYPI_TOKEN` with your token value

## Step 4: Create Your First Release

```bash
# Using the release script
./scripts/release.sh --version 1.0.0 --push

# Or manually
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## What's Been Implemented

✅ **Git-Tag-Based Semversioning**
- Automatic version detection from git tags
- setuptools-scm configuration in `pyproject.toml`

✅ **Comprehensive Test Suite**
- `tests/test_pdf2svg2pdf.py` - Main module tests
- `tests/test_classic.py` - Classic module tests
- `tests/test_integration.py` - Integration tests

✅ **Build & Release Scripts**
- `scripts/build.sh` - Build packages
- `scripts/test.sh` - Run tests
- `scripts/release.sh` - Create releases
- `scripts/local-install.sh` - Development setup

✅ **Code Quality Tools**
- Pre-commit hooks in `.pre-commit-config.yaml`
- Black, isort, flake8, bandit, mypy

✅ **Documentation**
- `CHANGELOG.md` - Change tracking
- `CONTRIBUTING.md` - Contribution guidelines
- `DEPLOYMENT.md` - Deployment guide
- `SETUP.md` - This file

✅ **Convenience Tools**
- `Makefile` - Common tasks
- Enhanced `setup.cfg` with dev dependencies

## Quick Start After Setup

1. **Development setup:**
   ```bash
   make install-dev
   ```

2. **Run tests:**
   ```bash
   make test
   ```

3. **Build package:**
   ```bash
   make build
   ```

4. **Create release:**
   ```bash
   make release VERSION=1.0.0
   ```

## GitHub Actions Workflow Features

The workflow (`ci-workflow.yml`) includes:

- **Multi-platform testing** (Linux, macOS, Windows)
- **Python version matrix** (3.8-3.12)
- **Security scanning** (bandit, safety)
- **Binary creation** (PyInstaller)
- **Automated releases** (GitHub + PyPI)
- **Coverage reporting** (codecov)

## File Structure

```
pdf2svg2pdf/
├── .github/workflows/           # GitHub Actions
├── scripts/                     # Build/release scripts
├── tests/                       # Test suite
├── src/pdf2svg2pdf/            # Source code
├── pyproject.toml              # Build config (semver)
├── setup.cfg                   # Package config
├── .pre-commit-config.yaml     # Code quality
├── Makefile                    # Convenience commands
├── CHANGELOG.md                # Change log
├── CONTRIBUTING.md             # Contribution guide
├── DEPLOYMENT.md               # Deployment guide
├── SETUP.md                    # This file
└── ci-workflow.yml             # → Move to .github/workflows/ci.yml
```

## Next Steps

1. ✅ Complete the manual workflow setup above
2. ✅ Test the workflow with a small commit
3. ✅ Create your first release
4. ✅ Monitor GitHub Actions
5. ✅ Verify PyPI publishing (if configured)

## Support

- Check `DEPLOYMENT.md` for detailed usage
- Check `CONTRIBUTING.md` for development
- Use GitHub Issues for problems
- Use GitHub Discussions for questions

## Troubleshooting

### Common Issues

1. **Workflow not triggering**
   - Ensure `ci-workflow.yml` is moved to `.github/workflows/ci.yml`
   - Check GitHub Actions tab for errors

2. **Tests failing**
   - Install system dependencies (see `scripts/test.sh`)
   - Check Python version compatibility

3. **Release not working**
   - Verify tag format: `v1.2.3`
   - Check PyPI token setup
   - Monitor GitHub Actions logs

### Debug Commands

```bash
# Check version
python -c "import setuptools_scm; print(setuptools_scm.get_version())"

# Test imports
python -c "import pdf2svg2pdf; print(pdf2svg2pdf.__version__)"

# Run tests
pytest tests/ -v

# Check git status
git status
git log --oneline -5
```

That's it! The semversioning system is now fully implemented and ready for use.