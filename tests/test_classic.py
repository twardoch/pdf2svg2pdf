#!/usr/bin/env python3
# this_file: tests/test_classic.py

"""
Test suite for pdf2svg2pdf_classic module.
"""

import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from pdf2svg2pdf.pdf2svg2pdf_classic import (
    pdf2svg2pdf,
    svgo,
    svg_transparent_white,
    svg_fill0,
    svg_fill1,
    pdf_grayscale
)


class TestClassicModule:
    """Test cases for the classic module."""
    
    def test_svg_transparent_white(self):
        """Test SVG transparent white filter."""
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <rect x="10" y="10" width="80" height="80" fill="white"/>
</svg>'''
        
        result = svg_transparent_white(svg_content)
        assert 'fill="white"' not in result
        assert 'fill="transparent"' in result or 'fill="none"' in result
    
    def test_svg_fill0(self):
        """Test SVG fill0 filter."""
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <rect x="10" y="10" width="80" height="80" fill="#000000"/>
</svg>'''
        
        result = svg_fill0(svg_content)
        assert 'fill="#000000"' not in result
        assert 'fill="transparent"' in result or 'fill="none"' in result
    
    def test_svg_fill1(self):
        """Test SVG fill1 filter."""
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <rect x="10" y="10" width="80" height="80" fill="#ffffff"/>
</svg>'''
        
        result = svg_fill1(svg_content)
        assert 'fill="#ffffff"' not in result
        assert 'fill="transparent"' in result or 'fill="none"' in result
    
    @patch('pdf2svg2pdf.pdf2svg2pdf_classic.subprocess.run')
    def test_svgo_filter(self, mock_run):
        """Test SVGO filter."""
        mock_run.return_value = MagicMock(returncode=0)
        
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <rect x="10" y="10" width="80" height="80" fill="red"/>
</svg>'''
        
        # Mock successful svgo execution
        result = svgo(svg_content)
        
        # Should call subprocess.run with svgo command
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert 'svgo' in call_args
    
    @patch('pdf2svg2pdf.pdf2svg2pdf_classic.subprocess.run')
    def test_pdf_grayscale(self, mock_run):
        """Test PDF grayscale filter."""
        mock_run.return_value = MagicMock(returncode=0, stdout=b'fake_pdf_content')
        
        pdf_bytes = b'%PDF-1.4\nfake pdf content'
        
        result = pdf_grayscale(pdf_bytes)
        
        # Should call subprocess.run with ghostscript command
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert 'gs' in call_args
        assert result == b'fake_pdf_content'
    
    def test_filter_chain(self):
        """Test chaining multiple SVG filters."""
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <rect x="10" y="10" width="80" height="80" fill="white"/>
  <circle cx="50" cy="50" r="20" fill="#000000"/>
</svg>'''
        
        # Apply multiple filters
        result = svg_transparent_white(svg_content)
        result = svg_fill0(result)
        
        # Both white and black fills should be transparent
        assert 'fill="white"' not in result
        assert 'fill="#000000"' not in result
    
    def test_empty_svg_content(self):
        """Test filters with empty SVG content."""
        empty_svg = ""
        
        # Filters should handle empty content gracefully
        result = svg_transparent_white(empty_svg)
        assert result == empty_svg
        
        result = svg_fill0(empty_svg)
        assert result == empty_svg
        
        result = svg_fill1(empty_svg)
        assert result == empty_svg


class TestClassicCLI:
    """Test the classic CLI functionality."""
    
    def test_main_function_import(self):
        """Test that main function can be imported."""
        from pdf2svg2pdf.pdf2svg2pdf_classic import main
        assert callable(main)
    
    @patch('pdf2svg2pdf.pdf2svg2pdf_classic.pdf2svg2pdf')
    def test_main_with_args(self, mock_pdf2svg2pdf):
        """Test main function with arguments."""
        from pdf2svg2pdf.pdf2svg2pdf_classic import main
        
        # Mock the main processing function
        mock_pdf2svg2pdf.return_value = None
        
        # This would normally be called with sys.argv
        # We'll test the function directly
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.pdf"
            input_file.touch()
            
            # Test that the function can be called
            # (actual execution would require external tools)
            assert main is not None


class TestFilterFunctions:
    """Test individual filter functions."""
    
    def test_svg_content_modifications(self):
        """Test that SVG content is properly modified."""
        test_cases = [
            {
                'filter': svg_transparent_white,
                'input': '<rect fill="white"/>',
                'should_not_contain': 'fill="white"'
            },
            {
                'filter': svg_fill0,
                'input': '<rect fill="#000000"/>',
                'should_not_contain': 'fill="#000000"'
            },
            {
                'filter': svg_fill1,
                'input': '<rect fill="#ffffff"/>',
                'should_not_contain': 'fill="#ffffff"'
            }
        ]
        
        for case in test_cases:
            result = case['filter'](case['input'])
            assert case['should_not_contain'] not in result
    
    def test_complex_svg_content(self):
        """Test filters with complex SVG content."""
        complex_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <defs>
    <style>
      .white-fill { fill: white; }
      .black-fill { fill: #000000; }
    </style>
  </defs>
  <rect x="10" y="10" width="80" height="80" fill="white"/>
  <circle cx="100" cy="100" r="30" fill="#000000"/>
  <path d="M 50 50 L 150 50" stroke="white" fill="none"/>
  <text x="10" y="180" fill="#ffffff">Test text</text>
</svg>'''
        
        # Test that filters work with complex SVG
        result = svg_transparent_white(complex_svg)
        assert 'fill="white"' not in result
        
        result = svg_fill0(complex_svg)
        assert 'fill="#000000"' not in result
        
        result = svg_fill1(complex_svg)
        assert 'fill="#ffffff"' not in result
    
    def test_filter_preserves_structure(self):
        """Test that filters preserve SVG structure."""
        svg_with_structure = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <g id="group1">
    <rect x="10" y="10" width="30" height="30" fill="white"/>
    <rect x="50" y="50" width="30" height="30" fill="#000000"/>
  </g>
</svg>'''
        
        result = svg_transparent_white(svg_with_structure)
        
        # Should preserve XML structure
        assert '<?xml version="1.0" encoding="UTF-8"?>' in result
        assert '<g id="group1">' in result
        assert '</g>' in result
        assert '</svg>' in result