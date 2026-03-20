#!/usr/bin/env python3
"""
Test script to validate the AI Knowledge Base Assistant setup
"""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_dependencies():
    """Test if all required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'numpy', 'sklearn',
        'pypdf', 'requests'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"[X] {package}")

    if missing_packages:
        print(f"\n[X] Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\n[OK] All dependencies installed!")
    return True

def test_environment():
    """Test environment variables"""
    load_dotenv()

    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    print(f"[OK] OLLAMA_BASE_URL={ollama_url}")
    print(f"[OK] OLLAMA_MODEL={ollama_model}")
    return True

def test_ollama():
    """Test that Ollama is installed and the configured model is available."""
    load_dotenv()
    ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b').lower()

    try:
        version = subprocess.run(
            ['ollama', '--version'],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"[OK] {version.stdout.strip()}")
    except Exception:
        print("[X] Ollama is not installed or not available in PATH")
        return False

    try:
        models = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        print("[X] Could not query Ollama models")
        return False

    if ollama_model in models.stdout.lower():
        print(f"[OK] Ollama model available: {ollama_model}")
        return True

    print(f"[X] Ollama model not found: {ollama_model}")
    print(f"Run: ollama pull {ollama_model}")
    return False

def test_directories():
    """Test required directories exist"""
    required_dirs = ['data']

    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"[OK] {dir_name}/ directory exists")
        else:
            print(f"[X] {dir_name}/ directory missing")
            Path(dir_name).mkdir()
            print(f"[OK] Created {dir_name}/ directory")

    return True

def test_pdf_files():
    """Check for PDF files in data directory"""
    data_dir = Path('data')
    pdf_files = list(data_dir.glob('*.pdf'))

    if pdf_files:
        print(f"[OK] Found {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            print(f"   - {pdf.name}")
        return True
    else:
        print("[!] No PDF files found in data/ directory")
        print("   Please add Dell knowledge PDFs to the data/ directory")
        print("   Or upload them through the Streamlit interface")
        return False

def main():
    """Run all tests"""
    print("Testing AI Knowledge Base Assistant Setup\n")

    tests = [
        ("Dependencies", test_dependencies),
        ("Environment Variables", test_environment),
        ("Ollama", test_ollama),
        ("Directories", test_directories),
        ("PDF Files", test_pdf_files)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"Testing {test_name}:")
        result = test_func()
        results.append(result)
        print()

    print("Test Results:")
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"[OK] All tests passed ({passed}/{total})")
        print("\nReady to run the application!")
        print("   API: python app.py api")
        print("   Frontend: python app.py frontend")
    else:
        print(f"[!] {passed}/{total} tests passed")
        print("\nPlease fix the failed tests before running the application")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
