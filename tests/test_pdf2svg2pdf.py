#!/usr/bin/env python3
# this_file: tests/test_pdf2svg2pdf.py

"""
Test suite for pdf2svg2pdf package.
"""

import os
import tempfile
from pathlib import Path
import pytest
import shutil
from unittest.mock import patch, MagicMock

from pdf2svg2pdf import PDF2SVG2PDF, __version__
from pdf2svg2pdf.pdf2svg2pdf import cli


class TestPDF2SVG2PDF:
    """Test cases for the PDF2SVG2PDF class."""
    
    def test_version_available(self):
        """Test that version is available."""
        assert __version__ is not None
        assert __version__ != "unknown"
    
    def test_init_with_valid_paths(self):
        """Test initialization with valid paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.pdf"
            input_file.touch()  # Create empty file
            
            converter = PDF2SVG2PDF(
                inpath=str(input_file),
                outdir=str(tmpdir_path / "output")
            )
            
            assert converter.inpath == input_file
            assert converter.outdir == tmpdir_path / "output"
            assert converter.outdir.exists()
    
    def test_init_with_invalid_input(self):
        """Test initialization with invalid input file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError):
                PDF2SVG2PDF(
                    inpath="/nonexistent/file.pdf",
                    outdir=str(tmpdir)
                )
    
    def test_init_creates_output_directories(self):
        """Test that initialization creates required output directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.pdf"
            input_file.touch()
            
            converter = PDF2SVG2PDF(
                inpath=str(input_file),
                outdir=str(tmpdir_path / "output")
            )
            
            # Check that subdirectories are created
            assert converter.pdf_t_dir.exists()
            assert converter.svg_q_dir.exists()
            assert converter.pdf_q_dir.exists()
            
            # Check directory naming
            assert converter.pdf_t_dir.name == "test-pdf-t"
            assert converter.svg_q_dir.name == "test-svg-q"
            assert converter.pdf_q_dir.name == "test-pdf-q"
    
    def test_backend_selection(self):
        """Test backend selection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.pdf"
            input_file.touch()
            
            # Test default backends
            converter = PDF2SVG2PDF(
                inpath=str(input_file),
                outdir=str(tmpdir_path / "output")
            )
            assert "poppler" in converter.backends
            assert "pdfcairo" in converter.backends
            assert "cairosvg" in converter.backends
            
            # Test custom backends
            custom_backends = ["fitz", "pdfcairo", "cairosvg"]
            converter = PDF2SVG2PDF(
                inpath=str(input_file),
                outdir=str(tmpdir_path / "output"),
                backends=custom_backends
            )
            assert converter.backends == custom_backends
    
    @patch('pdf2svg2pdf.pdf2svg2pdf.subprocess.run')
    def test_check_dependencies(self, mock_run):
        """Test dependency checking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.pdf"
            input_file.touch()
            
            # Mock successful command execution
            mock_run.return_value = MagicMock(returncode=0)
            
            converter = PDF2SVG2PDF(
                inpath=str(input_file),
                outdir=str(tmpdir_path / "output")
            )
            
            # Should not raise an exception
            converter.check_dependencies()
    
    def test_verbose_mode(self):
        """Test verbose mode initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.pdf"
            input_file.touch()
            
            converter = PDF2SVG2PDF(
                inpath=str(input_file),
                outdir=str(tmpdir_path / "output"),
                verbose=True
            )
            
            assert converter.verbose is True


class TestCLI:
    """Test cases for CLI functionality."""
    
    def test_cli_help(self):
        """Test CLI help functionality."""
        with pytest.raises(SystemExit) as exc_info:
            cli(["--help"])
        
        # Help should exit with code 0
        assert exc_info.value.code == 0
    
    def test_cli_version(self):
        """Test CLI version display."""
        with pytest.raises(SystemExit) as exc_info:
            cli(["--version"])
        
        # Version should exit with code 0
        assert exc_info.value.code == 0
    
    def test_cli_missing_args(self):
        """Test CLI with missing arguments."""
        with pytest.raises(SystemExit) as exc_info:
            cli([])
        
        # Should exit with non-zero code
        assert exc_info.value.code != 0


class TestUtilities:
    """Test utility functions."""
    
    def test_path_handling(self):
        """Test path handling utilities."""
        from pdf2svg2pdf.pdf2svg2pdf import PDF2SVG2PDF
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.pdf"
            input_file.touch()
            
            # Test with Path objects
            converter = PDF2SVG2PDF(
                inpath=input_file,
                outdir=tmpdir_path / "output"
            )
            
            assert isinstance(converter.inpath, Path)
            assert isinstance(converter.outdir, Path)
            
            # Test with string paths
            converter = PDF2SVG2PDF(
                inpath=str(input_file),
                outdir=str(tmpdir_path / "output")
            )
            
            assert isinstance(converter.inpath, Path)
            assert isinstance(converter.outdir, Path)


class TestIntegration:
    """Integration tests (require external tools)."""
    
    def test_dependency_check_real(self):
        """Test actual dependency checking (if tools are available)."""
        from pdf2svg2pdf.pdf2svg2pdf import PDF2SVG2PDF
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "test.pdf"
            input_file.touch()
            
            converter = PDF2SVG2PDF(
                inpath=str(input_file),
                outdir=str(tmpdir_path / "output")
            )
            
            # This will only pass if dependencies are installed
            # In CI, we should ensure they are available
            try:
                converter.check_dependencies()
                # If we get here, dependencies are available
                assert True
            except Exception:
                # If dependencies are not available, skip this test
                pytest.skip("External dependencies not available")


@pytest.fixture
def sample_pdf():
    """Create a minimal PDF file for testing."""
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Test PDF Content")
    p.showPage()
    p.save()
    
    return buffer.getvalue()


class TestWithSamplePDF:
    """Tests using a real PDF file."""
    
    def test_with_sample_pdf(self, sample_pdf):
        """Test processing with a sample PDF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create sample PDF file
            pdf_file = tmpdir_path / "sample.pdf"
            pdf_file.write_bytes(sample_pdf)
            
            converter = PDF2SVG2PDF(
                inpath=str(pdf_file),
                outdir=str(tmpdir_path / "output")
            )
            
            # Basic initialization should work
            assert converter.inpath.exists()
            assert converter.outdir.exists()
            
            # Check that all required directories are created
            assert converter.pdf_t_dir.exists()
            assert converter.svg_q_dir.exists()
            assert converter.pdf_q_dir.exists()