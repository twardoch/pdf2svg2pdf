#!/usr/bin/env python3
# this_file: tests/test_pdf2svg2pdf.py
"""Tests for the package surface and the legacy PDF2SVG2PDF class."""

from __future__ import annotations

import tempfile
from pathlib import Path

from pdf2svg2pdf import PDF2SVG2PDF, __version__
from pdf2svg2pdf.pdf2svg2pdf import convert_pdfs


def _touch_pdf(directory: Path, name: str = "test.pdf") -> Path:
    """Create an empty placeholder PDF so path handling can be exercised."""
    path = directory / name
    path.touch()
    return path


class TestPackage:
    def test_version_available(self):
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_public_api_exports(self):
        import pdf2svg2pdf

        for name in ("Converter", "Configuration", "PDF2SVG2PDF", "convert_pdfs"):
            assert hasattr(pdf2svg2pdf, name), name


class TestLegacyConverter:
    def test_init_accepts_str_and_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pdf = _touch_pdf(tmp_path)

            for inpath in (str(pdf), pdf):
                converter = PDF2SVG2PDF(inpath=inpath, outdir=str(tmp_path / "out"))
                assert isinstance(converter.inpath, Path)
                assert isinstance(converter.outdir, Path)

    def test_init_creates_working_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pdf = _touch_pdf(tmp_path)

            converter = PDF2SVG2PDF(inpath=str(pdf), outdir=str(tmp_path / "out"))

            assert converter.pdf_t_dir.exists()
            assert converter.svg_q_dir.exists()
            assert converter.pdf_q_dir.exists()
            assert converter.pdf_t_dir.name == "test-pdf-t"
            assert converter.svg_q_dir.name == "test-svg-q"
            assert converter.pdf_q_dir.name == "test-pdf-q"

    def test_default_backends(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pdf = _touch_pdf(tmp_path)

            converter = PDF2SVG2PDF(inpath=str(pdf), outdir=str(tmp_path / "out"))
            assert converter.backends == ["poppler", "pdfcairo", "cairosvg"]

    def test_custom_backends_override_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pdf = _touch_pdf(tmp_path)

            custom = ["fitz", "pdfcairo", "cairosvg"]
            converter = PDF2SVG2PDF(
                inpath=str(pdf), outdir=str(tmp_path / "out"), backends=custom
            )
            assert converter.backends == custom

    def test_verbose_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pdf = _touch_pdf(tmp_path)

            converter = PDF2SVG2PDF(
                inpath=str(pdf), outdir=str(tmp_path / "out"), verbose=True
            )
            assert converter.verbose is True

    def test_convert_pdfs_is_callable(self):
        # The module-level helper must exist and accept the documented signature.
        assert callable(convert_pdfs)
