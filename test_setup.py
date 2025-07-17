#!/usr/bin/env python3
"""
Simple test script to validate the setup.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    try:
        import pdf2svg2pdf
        print(f"✅ pdf2svg2pdf imported successfully")
        print(f"   Version: {pdf2svg2pdf.__version__}")
        
        from pdf2svg2pdf import PDF2SVG2PDF
        print(f"✅ PDF2SVG2PDF class imported successfully")
        
        from pdf2svg2pdf import pdf2svg2pdf_classic
        print(f"✅ pdf2svg2pdf_classic module imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_version():
    """Test version detection."""
    try:
        import pdf2svg2pdf
        version = pdf2svg2pdf.__version__
        print(f"📦 Package version: {version}")
        
        if version != "unknown":
            print("✅ Version detection working")
            return True
        else:
            print("⚠️  Version is 'unknown' - this is expected without tags")
            return True
    except Exception as e:
        print(f"❌ Version test failed: {e}")
        return False

def test_cli():
    """Test CLI functionality."""
    try:
        from pdf2svg2pdf.pdf2svg2pdf import cli
        print("✅ CLI function imported successfully")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    print("🧪 Testing pdf2svg2pdf setup...\n")
    
    tests = [
        ("Import test", test_imports),
        ("Version test", test_version),
        ("CLI test", test_cli),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed\n")
        else:
            print(f"❌ {test_name} failed\n")
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())