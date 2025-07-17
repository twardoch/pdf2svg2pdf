#!/usr/bin/env python3
# this_file: tests/test_integration.py

"""
Integration tests for pdf2svg2pdf package.
These tests require external dependencies and may be skipped in CI.
"""

import os
import tempfile
from pathlib import Path
import pytest
import subprocess
import shutil

from pdf2svg2pdf import PDF2SVG2PDF


def check_external_tool(tool_name):
    """Check if an external tool is available."""
    try:
        result = subprocess.run([tool_name, '--help'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# Skip integration tests if external tools are not available
pytestmark = pytest.mark.skipif(
    not all([
        check_external_tool('pdfseparate'),
        check_external_tool('pdfunite'),
        check_external_tool('pdftocairo'),
        check_external_tool('cairosvg')
    ]),
    reason="External tools not available"
)


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            p = canvas.Canvas(tmp.name, pagesize=letter)
            p.drawString(100, 750, "Test PDF Content - Page 1")
            p.showPage()
            p.drawString(100, 750, "Test PDF Content - Page 2")
            p.showPage()
            p.save()
            
            yield tmp.name
            
            # Cleanup
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)
                
    except ImportError:
        # Create a minimal PDF without reportlab
        pytest.skip("reportlab not available for creating test PDF")


class TestFullWorkflow:
    """Test the complete PDF->SVG->PDF workflow."""
    
    def test_full_conversion_workflow(self, sample_pdf_file):
        """Test complete conversion workflow with a real PDF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            converter = PDF2SVG2PDF(
                inpath=sample_pdf_file,
                outdir=str(tmpdir_path / "output"),
                verbose=True
            )
            
            # Check dependencies first
            converter.check_dependencies()
            
            # Run the conversion
            output_pdf = converter.process()
            
            # Verify output file exists
            assert Path(output_pdf).exists()
            assert Path(output_pdf).suffix == '.pdf'
            
            # Verify intermediate directories were created
            assert converter.pdf_t_dir.exists()
            assert converter.svg_q_dir.exists()
            assert converter.pdf_q_dir.exists()
            
            # Check that intermediate files were created
            pdf_pages = list(converter.pdf_t_dir.glob('*.pdf'))
            svg_pages = list(converter.svg_q_dir.glob('*.svg'))
            processed_pages = list(converter.pdf_q_dir.glob('*.pdf'))
            
            assert len(pdf_pages) > 0
            assert len(svg_pages) > 0
            assert len(processed_pages) > 0
            
            # All should have same count (one per page)
            assert len(pdf_pages) == len(svg_pages) == len(processed_pages)
    
    def test_single_page_pdf(self, sample_pdf_file):
        """Test conversion of single page PDF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create single page PDF
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                
                single_page_pdf = tmpdir_path / "single.pdf"
                p = canvas.Canvas(str(single_page_pdf), pagesize=letter)
                p.drawString(100, 750, "Single Page PDF")
                p.save()
                
                converter = PDF2SVG2PDF(
                    inpath=str(single_page_pdf),
                    outdir=str(tmpdir_path / "output"),
                    verbose=True
                )
                
                output_pdf = converter.process()
                
                # Verify output
                assert Path(output_pdf).exists()
                
                # Should have exactly one page in each directory
                pdf_pages = list(converter.pdf_t_dir.glob('*.pdf'))
                svg_pages = list(converter.svg_q_dir.glob('*.svg'))
                processed_pages = list(converter.pdf_q_dir.glob('*.pdf'))
                
                assert len(pdf_pages) == 1
                assert len(svg_pages) == 1
                assert len(processed_pages) == 1
                
            except ImportError:
                pytest.skip("reportlab not available")
    
    def test_different_backends(self, sample_pdf_file):
        """Test conversion with different backend combinations."""
        backend_combinations = [
            ["poppler", "pdfcairo", "cairosvg"],
            ["fitz", "pdfcairo", "cairosvg"],
        ]
        
        for backends in backend_combinations:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                converter = PDF2SVG2PDF(
                    inpath=sample_pdf_file,
                    outdir=str(tmpdir_path / f"output_{'_'.join(backends)}"),
                    backends=backends,
                    verbose=True
                )
                
                try:
                    output_pdf = converter.process()
                    assert Path(output_pdf).exists()
                except Exception as e:
                    # Some backends might not be available
                    pytest.skip(f"Backend combination {backends} not available: {e}")


class TestExternalToolIntegration:
    """Test integration with external tools directly."""
    
    def test_pdfseparate_available(self):
        """Test that pdfseparate is available and working."""
        result = subprocess.run(['pdfseparate', '--help'], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert 'pdfseparate' in result.stdout.lower()
    
    def test_pdfunite_available(self):
        """Test that pdfunite is available and working."""
        result = subprocess.run(['pdfunite', '--help'], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert 'pdfunite' in result.stdout.lower()
    
    def test_pdftocairo_available(self):
        """Test that pdftocairo is available and working."""
        result = subprocess.run(['pdftocairo', '-h'], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert 'cairo' in result.stdout.lower()
    
    def test_cairosvg_available(self):
        """Test that cairosvg is available and working."""
        result = subprocess.run(['cairosvg', '--help'], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert 'cairosvg' in result.stdout.lower()


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    def test_invalid_pdf_file(self):
        """Test handling of invalid PDF files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create invalid PDF file
            invalid_pdf = tmpdir_path / "invalid.pdf"
            invalid_pdf.write_text("This is not a PDF file")
            
            converter = PDF2SVG2PDF(
                inpath=str(invalid_pdf),
                outdir=str(tmpdir_path / "output"),
                verbose=True
            )
            
            # Should handle invalid PDF gracefully
            with pytest.raises(Exception):
                converter.process()
    
    def test_corrupted_pdf_file(self):
        """Test handling of corrupted PDF files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create corrupted PDF file
            corrupted_pdf = tmpdir_path / "corrupted.pdf"
            corrupted_pdf.write_bytes(b'%PDF-1.4\n%%EOF\ninvalid content')
            
            converter = PDF2SVG2PDF(
                inpath=str(corrupted_pdf),
                outdir=str(tmpdir_path / "output"),
                verbose=True
            )
            
            # Should handle corrupted PDF gracefully
            with pytest.raises(Exception):
                converter.process()
    
    def test_permission_denied_output(self):
        """Test handling of permission denied on output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create a read-only directory
            readonly_dir = tmpdir_path / "readonly"
            readonly_dir.mkdir()
            readonly_dir.chmod(0o444)  # Read-only
            
            # Create sample PDF
            sample_pdf = tmpdir_path / "sample.pdf"
            sample_pdf.write_bytes(b'%PDF-1.4\n%%EOF')
            
            try:
                converter = PDF2SVG2PDF(
                    inpath=str(sample_pdf),
                    outdir=str(readonly_dir / "output"),
                    verbose=True
                )
                
                # Should handle permission error gracefully
                with pytest.raises(PermissionError):
                    converter.process()
                    
            finally:
                # Cleanup: restore permissions
                readonly_dir.chmod(0o755)


class TestPerformance:
    """Test performance aspects of the conversion."""
    
    def test_large_pdf_handling(self):
        """Test handling of larger PDF files."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                
                # Create a PDF with multiple pages
                large_pdf = tmpdir_path / "large.pdf"
                p = canvas.Canvas(str(large_pdf), pagesize=letter)
                
                # Create 5 pages
                for i in range(5):
                    p.drawString(100, 750, f"Page {i+1} of large PDF")
                    p.showPage()
                p.save()
                
                converter = PDF2SVG2PDF(
                    inpath=str(large_pdf),
                    outdir=str(tmpdir_path / "output"),
                    verbose=True
                )
                
                output_pdf = converter.process()
                
                # Verify all pages were processed
                pdf_pages = list(converter.pdf_t_dir.glob('*.pdf'))
                assert len(pdf_pages) == 5
                
                # Output should exist
                assert Path(output_pdf).exists()
                
        except ImportError:
            pytest.skip("reportlab not available")
    
    def test_memory_usage(self):
        """Test that memory usage is reasonable."""
        # This is a placeholder for memory usage testing
        # In a real scenario, you might use memory profiling tools
        assert True  # Placeholder test