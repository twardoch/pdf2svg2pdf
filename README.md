# pdf2svg2pdf

Take a PDF apart into vectors, change the vectors, put it back together as a PDF.

`pdf2svg2pdf` splits a PDF into single pages, turns each page into an SVG, lets
you rewrite that SVG (or the source PDF) with a filter, then renders the pages
back to PDF and merges them. SVG is the middle step because it is plain XML: a
regex or a string replace can recolour a fill or strip an element that a PDF
editor would fight you over, and nothing gets rasterised, so the output stays as
sharp as the input.

## Install

```bash
pip install pdf2svg2pdf
```

The pipeline shells out to a few tools; install them too:

- **Poppler** (`pdfseparate`, `pdfunite`, `pdftocairo`) — `brew install poppler`
  or `sudo apt-get install poppler-utils`.
- **cairo** — the native library `cairosvg` needs — `brew install cairo` or
  `sudo apt-get install libcairo2`. (`cairosvg` itself installs with the package.)

Two filters need extra tools: `pdf_grayscale` needs Ghostscript (`gs`) and the
`svgo` filter needs [SVGO](https://github.com/svg/svgo) (`npm install -g svgo`).

## Use it

Convert one PDF (writes `out.pdf`):

```bash
pdf2svg2pdf convert input.pdf --output out.pdf
```

Convert a whole directory:

```bash
pdf2svg2pdf batch --input-dir ./pdfs --output-dir ./converted
```

List filters, or show the version:

```bash
pdf2svg2pdf list-filters
pdf2svg2pdf version
```

## From Python

```python
from pdf2svg2pdf import Converter, load_configuration

converter = Converter(load_configuration())
result = converter.convert_sync("input.pdf", output_path="out.pdf")
print(result["output_path"] if result["success"] else result["error"])
```

The legacy `PDF2SVG2PDF` class maps one-to-one onto the shell tools and is handy
when you want to watch each step:

```python
from pdf2svg2pdf import PDF2SVG2PDF

PDF2SVG2PDF(inpath="input.pdf", outdir="out").process()  # writes out/input-q.pdf
```

## Filters

A filter changes the document mid-pipeline. PDF filters run on the raw bytes
before the split (`(bytes) -> bytes`); SVG filters run on each page's SVG text
(`(str) -> str`). To grayscale a PDF on the way through:

```python
from pdf2svg2pdf.pdf2svg2pdf_classic import pdf2svg2pdf, pdf_grayscale

pdf2svg2pdf("color.pdf", outdir="out", pdf_filters=[pdf_grayscale])
```

See the [Filters guide](https://twardoch.github.io/pdf2svg2pdf/filters) for the
full list and how to write your own.

## Docs

Full documentation: <https://twardoch.github.io/pdf2svg2pdf/>

## Develop

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -e '.[dev]'
ruff check src tests && mypy src/pdf2svg2pdf && pytest
```

The round-trip integration test skips itself unless Poppler and a working
`cairosvg` are both present.

## License

Apache-2.0. © Adam Twardoch.
