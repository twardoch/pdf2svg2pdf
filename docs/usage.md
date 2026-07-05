---
title: Usage
layout: default
nav_order: 2
---

# Usage

## Command line

Convert one PDF:

```bash
pdf2svg2pdf convert input.pdf --output out.pdf
```

Convert every PDF in a directory:

```bash
pdf2svg2pdf batch --input-dir ./pdfs --output-dir ./converted
```

List the built-in filters:

```bash
pdf2svg2pdf list-filters
```

Show the version:

```bash
pdf2svg2pdf version
```

## Python API

The modern API runs the pipeline through a `Converter`:

```python
from pdf2svg2pdf import Converter, load_configuration

config = load_configuration()
converter = Converter(config)
result = converter.convert_sync("input.pdf", output_path="out.pdf")

if result["success"]:
    print("wrote", result["output_path"])
else:
    print("failed:", result["error"])
```

The legacy class is still available and maps one-to-one onto the shell tools,
which is handy when you want to see exactly what each step does:

```python
from pdf2svg2pdf import PDF2SVG2PDF

converter = PDF2SVG2PDF(inpath="input.pdf", outdir="out")
converter.process()  # writes out/input-q.pdf
```
