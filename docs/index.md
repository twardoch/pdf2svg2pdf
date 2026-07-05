---
title: Home
layout: default
nav_order: 1
---

# pdf2svg2pdf

Take a PDF apart into vectors, change the vectors, put it back together as a PDF.

`pdf2svg2pdf` splits a PDF into single pages, turns each page into an SVG, lets
you rewrite that SVG (or the source PDF) with a filter, then renders the pages
back to PDF and merges them. SVG is the middle step because it is plain XML: a
regex or a string replace can recolour a fill or strip an element that a PDF
editor would fight you over, and nothing gets rasterised, so the output stays as
sharp as the input.

```bash
pip install pdf2svg2pdf
pdf2svg2pdf convert input.pdf --output out.pdf
```

## The pipeline

1. **Split** the PDF into one PDF per page (`pdfseparate` or PyMuPDF).
2. **PDF to SVG** for each page (`pdftocairo -svg`).
3. **Filter** the SVG (or the PDF, before the split) — optional.
4. **SVG to PDF** for each page (`cairosvg`).
5. **Merge** the pages into the final PDF (`pdfunite`).

## External dependencies

The pipeline shells out to a few tools. Install them before you run it:

- **Poppler** — provides `pdfseparate`, `pdfunite`, `pdftocairo`.
  - macOS: `brew install poppler`
  - Debian/Ubuntu: `sudo apt-get install poppler-utils`
- **cairosvg** — the SVG-to-PDF renderer. Installed as a Python dependency, but
  it needs the native cairo library:
  - macOS: `brew install cairo`
  - Debian/Ubuntu: `sudo apt-get install libcairo2`

Optional, only for specific filters: `gs` (Ghostscript, for grayscale) and
`svgo` (for SVG optimisation).

## Next

- [Usage](usage.md) — the CLI and the Python API.
- [Filters](filters.md) — the filter hooks and a worked grayscale example.
