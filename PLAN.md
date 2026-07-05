# PLAN

## Where the project stands

`pdf2svg2pdf` is a working PDF→SVG→PDF round-trip tool with two coexisting
implementations:

- **Classic / legacy** (`pdf2svg2pdf_classic.py`, `pdf2svg2pdf.py`) — small,
  script-style, shells out to poppler + cairosvg, supports eval-based filters.
  This is the code the tests cover and the code the pipeline actually runs.
- **Modern** (`core/`, `backends/`, `filters/`, `config/`, `utils/`) — an async,
  registry-driven architecture behind the `pdf2svg2pdf` console entry point. It
  imports and runs, but its async path is not yet under test.

The 2026 modernization pass moved the build to hatchling + hatch-vcs, put ruff +
mypy + pytest green, added CI/release workflows, fixed a missing-`await` bug and
an import cycle, and rebuilt the docs as a Jekyll site.

## Direction

The central open question is the two-implementation split. The modern layer adds
a lot of surface (plugin registries, async orchestration, a config system) for a
tool whose core job is "split, run pdftocairo, run cairosvg, pdfunite". The next
substantial decision is whether to:

1. Invest in the modern layer — add mocked-backend tests, finish the `TODO`
   items in `converter.py` (timing, memory metrics), and retire the classic
   path; or
2. Treat the classic path as the product and trim the modern layer down to what
   earns its keep.

Until that is decided, keep both working and keep the tests honest about which
path they cover. Concrete tasks live in `TODO.md`.
