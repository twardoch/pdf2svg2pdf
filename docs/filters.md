---
title: Filters
layout: default
nav_order: 3
---

# Filters

A filter is where you change the document mid-pipeline. There are two hooks,
each running at a different stage.

## The two hooks

**PDF filters** run on the raw PDF bytes *before* the page split.

```python
def my_pdf_filter(pdf_bytes: bytes) -> bytes:
    ...
    return new_pdf_bytes
```

**SVG filters** run on each page's SVG text *after* the PDF-to-SVG step.

```python
def my_svg_filter(svg: str) -> str:
    ...
    return new_svg
```

The classic module ships a handful of each. SVG filters operate on the CSS
`fill:rgb(...);` syntax that `pdftocairo` emits, not on `fill="..."` attributes.

| Hook | Function | What it does |
|------|----------|--------------|
| PDF  | `pdf_grayscale`        | Convert every page to grayscale (Ghostscript). |
| SVG  | `svgo`                 | Shrink markup through the `svgo` optimiser. |
| SVG  | `svg_transparent_white`| Turn pure-white fills into `fill:none`. |
| SVG  | `svg_fill0`            | Repaint everything with the most common fill. |
| SVG  | `svg_fill1`            | Repaint everything with the second most common fill. |

## Worked example: grayscale a PDF

The `pdf_grayscale` filter runs before the split, so the whole document is
desaturated in one Ghostscript pass, then converted through SVG as usual:

```python
from pdf2svg2pdf.pdf2svg2pdf_classic import pdf2svg2pdf, pdf_grayscale

pdf2svg2pdf("color.pdf", outdir="out", pdf_filters=[pdf_grayscale])
```

From the classic CLI, filters are passed as comma-separated Python expressions:

```bash
python -m pdf2svg2pdf.pdf2svg2pdf_classic color.pdf \
    --outdir out --pdf_filters pdf_grayscale
```

Because the classic CLI evaluates those expressions with `eval`, only feed it
input you trust.

## Writing your own

A filter is just a function with the right signature. Pass it in the
`pdf_filters` or `svg_filters` list and it joins the chain in order:

```python
def redact_black(svg: str) -> str:
    # Paint every visible fill solid black.
    import re
    return re.sub(r"fill:(?!none;)(.*?);", "fill:rgb(0%,0%,0%);", svg)

pdf2svg2pdf("in.pdf", outdir="out", svg_filters=[redact_black])
```
