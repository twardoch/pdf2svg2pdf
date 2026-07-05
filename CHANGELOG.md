# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project uses
git-tag-based [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Build & packaging
- Migrated the build backend from setuptools + `setuptools_scm` to
  **hatchling + hatch-vcs**; the version now derives from git tags and lands in
  a git-ignored `src/pdf2svg2pdf/_version.py`.
- Removed the dual `setup.py` / `setup.cfg` / `.isort.cfg` build config and the
  stale pinned `requirements.txt`.
- Added `cairosvg` as a real dependency — the pipeline shells out to it but it
  was never declared.
- Added GitHub Actions `ci.yml` (ruff, ruff-format, mypy, pytest on Python 3.12
  and 3.13) and `release.yml` (build, GitHub release, PyPI trusted publishing on
  tag push); removed the old root `ci-workflow.yml`.

### Code
- Replaced the broken test suite (it was written against methods that never
  existed — `check_dependencies`, a `main` in the classic module, `cli(args)`)
  with tests that exercise the real API, plus a genuine PDF→SVG→PDF round-trip
  test that skips cleanly when Poppler or a working `cairosvg` is absent.
- Fixed a real bug in `core.pipeline`: `AsyncPool.submit` is a coroutine and was
  called without `await`, so pages were never scheduled onto the pool.
- Broke a `core` ↔ `backends` import cycle by importing the backend registry
  lazily inside the methods that use it.
- Fixed `retry_async` raising a possibly-`None` exception, and a missing `Any`
  import in `utils.io`.
- Added type hints and a filter-API docstring to the classic module.

### Quality
- Switched linting/formatting to **ruff** (replacing black, isort, flake8,
  bandit) and made `ruff check`, `ruff format`, and strict-ish `mypy` pass
  cleanly across the package.
- Updated `.pre-commit-config.yaml` and the `Makefile` to the ruff/mypy toolchain.

### Docs
- Rewrote the README from ~320 lines to a focused overview with an accurate API
  (the old one claimed `process()` returned a path — it does not).
- Replaced the Sphinx/ReadTheDocs docs with a Jekyll + Just-the-Docs site under
  `docs/` (home, usage, filters), and documented the external binary
  dependencies and the two filter hooks.

## [0.1.0] — Initial work
- PDF→SVG→PDF conversion pipeline, CLI, and Python library.
- Modular backend/filter architecture and the classic script-style module.
