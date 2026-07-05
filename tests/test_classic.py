#!/usr/bin/env python3
# this_file: tests/test_classic.py
"""Tests for the classic filter functions.

The classic SVG filters operate on the CSS ``fill:rgb(...);`` style syntax that
``pdftocairo`` emits, not on presentation attributes like ``fill="white"``.
The fixtures below use that real syntax.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from pdf2svg2pdf.pdf2svg2pdf_classic import (
    cli,
    pdf_grayscale,
    svg_fill0,
    svg_fill1,
    svg_frequency_fills,
    svg_transparent_white,
    svgo,
)

WHITE = "fill:rgb(100%,100%,100%);"
BLACK = "fill:rgb(0%,0%,0%);"
RED = "fill:rgb(100%,0%,0%);"


class TestSvgFilters:
    def test_transparent_white_replaces_white_with_none(self):
        svg = f"<path style='{WHITE}'/>"
        result = svg_transparent_white(svg)
        assert WHITE not in result
        assert "fill:none;" in result

    def test_transparent_white_leaves_other_colours(self):
        svg = f"<path style='{RED}'/>"
        assert svg_transparent_white(svg) == svg

    def test_frequency_fills_orders_by_count(self):
        svg = f"{BLACK}{BLACK}{RED}"
        freqs = svg_frequency_fills(svg)
        assert freqs[0][0] == "rgb(0%,0%,0%)"
        assert freqs[0][1] == 2

    def test_fill0_collapses_to_most_common_colour(self):
        svg = f"<a style='{BLACK}'/><b style='{BLACK}'/><c style='{RED}'/>"
        result = svg_fill0(svg)
        # Everything visible becomes the most frequent fill (black); red is gone.
        assert RED not in result
        assert "fill:rgb(0%,0%,0%);" in result

    def test_fill1_uses_second_most_common_colour(self):
        svg = f"<a style='{BLACK}'/><b style='{BLACK}'/><c style='{RED}'/>"
        result = svg_fill1(svg)
        assert "fill:rgb(100%,0%,0%);" in result

    def test_filters_handle_empty_input(self):
        for fn in (svg_transparent_white, svg_fill0, svg_fill1):
            assert fn("") == ""


class TestFilterProcesses:
    @patch("pdf2svg2pdf.pdf2svg2pdf_classic.subprocess.run")
    def test_svgo_invokes_svgo(self, mock_run):
        mock_run.return_value = MagicMock(stdout="<svg/>")
        assert svgo("<svg/>") == "<svg/>"
        assert "svgo" in mock_run.call_args[0][0]

    @patch("pdf2svg2pdf.pdf2svg2pdf_classic.subprocess.run")
    def test_grayscale_invokes_ghostscript(self, mock_run):
        mock_run.return_value = MagicMock(stdout=b"grey-pdf")
        assert pdf_grayscale(b"%PDF-1.4") == b"grey-pdf"
        assert "gs " in mock_run.call_args[0][0]


def test_cli_entrypoint_exists():
    assert callable(cli)
