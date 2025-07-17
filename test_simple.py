#!/usr/bin/env python3
"""
Simple test script to validate basic functionality without external dependencies.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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

def test_file_structure():
    """Test that all expected files exist."""
    expected_files = [
        'src/pdf2svg2pdf/__init__.py',
        'src/pdf2svg2pdf/pdf2svg2pdf.py',
        'src/pdf2svg2pdf/pdf2svg2pdf_classic.py',
        'pyproject.toml',
        'setup.cfg',
        'README.md',
        'CHANGELOG.md',
        'CONTRIBUTING.md',
        'Makefile',
        '.github/workflows/ci.yml',
        '.pre-commit-config.yaml',
        'scripts/build.sh',
        'scripts/test.sh',
        'scripts/release.sh',
        'scripts/local-install.sh',
        'tests/test_pdf2svg2pdf.py',
        'tests/test_classic.py',
        'tests/test_integration.py',
    ]
    
    missing = []
    for file_path in expected_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ All expected files present")
        return True

def test_git_setup():
    """Test git setup."""
    try:
        import subprocess
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository is set up")
            return True
        else:
            print("❌ Git repository not properly set up")
            return False
    except Exception as e:
        print(f"❌ Git test failed: {e}")
        return False

def test_scripts_executable():
    """Test that scripts are executable."""
    scripts = [
        'scripts/build.sh',
        'scripts/test.sh',
        'scripts/release.sh',
        'scripts/local-install.sh'
    ]
    
    for script in scripts:
        if not os.access(script, os.X_OK):
            print(f"❌ Script {script} is not executable")
            return False
    
    print("✅ All scripts are executable")
    return True

def main():
    print("🧪 Testing pdf2svg2pdf setup (simple)...\n")
    
    tests = [
        ("Version test", test_version),
        ("File structure test", test_file_structure),
        ("Git setup test", test_git_setup),
        ("Scripts executable test", test_scripts_executable),
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