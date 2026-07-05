#!/usr/bin/env python3
# this_file: tests/test_integration.py
"""End-to-end round-trip test.

This drives the real PDF -> SVG -> PDF pipeline, so it needs the external
binaries (``pdfseparate``, ``pdfunite``, ``pdftocairo``) and a working
``cairosvg`` (which in turn needs the native cairo library). When any of those
is missing or broken, the whole module is skipped rather than failed.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz
import pytest

from pdf2svg2pdf import PDF2SVG2PDF


def _toolchain_ready() -> bool:
    """Return True only if every step of the round-trip can actually run."""
    if not all(
        shutil.which(tool) for tool in ("pdfseparate", "pdfunite", "pdftocairo")
    ):
        return False
    # cairosvg's CLI can be on PATH yet fail to load libcairo; prove it works.
    try:
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "probe.svg"
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4"/>'
            )
            out = Path(tmp) / "probe.pdf"
            result = subprocess.run(
                ["cairosvg", "-f", "pdf", "-o", str(out), str(svg)],
                capture_output=True,
                timeout=30,
            )
            return result.returncode == 0 and out.exists()
    except (OSError, subprocess.SubprocessError):
        return False


pytestmark = pytest.mark.skipif(
    not _toolchain_ready(),
    reason="round-trip toolchain (poppler + working cairosvg) not available",
)


@pytest.fixture
def two_page_pdf() -> Path:
    """A minimal, real 2-page PDF built with PyMuPDF (always available)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "in.pdf"
        doc = fitz.open()
        for n in range(2):
            page = doc.new_page()
            page.insert_text((72, 72), f"Page {n + 1}")
        doc.save(path)
        doc.close()
        yield path


@pytest.mark.integration
def test_roundtrip_preserves_page_count(two_page_pdf: Path):
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "out"
        converter = PDF2SVG2PDF(inpath=str(two_page_pdf), outdir=str(out_dir))
        converter.process()

        assert converter.pdf_q_path.exists()
        result = fitz.open(converter.pdf_q_path)
        assert len(result) == 2

        # One intermediate SVG and one requantised PDF per source page.
        assert len(list(converter.svg_q_dir.glob("*.svg"))) == 2
        assert len(list(converter.pdf_q_dir.glob("*.pdf"))) == 2
