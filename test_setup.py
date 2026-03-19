#!/usr/bin/env python3
"""
Test script to validate the AI Knowledge Base Assistant setup
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_dependencies():
    """Test if all required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'langchain',
        'openai', 'faiss', 'pypdf2', 'python-multipart'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")

    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\n✅ All dependencies installed!")
    return True

def test_environment():
    """Test environment variables"""
    load_dotenv()

    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'your_openai_api_key_here':
        print("✅ OpenAI API key configured")
        return True
    else:
        print("❌ OpenAI API key not configured")
        print("Please set OPENAI_API_KEY in .env file")
        return False

def test_directories():
    """Test required directories exist"""
    required_dirs = ['data']

    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            Path(dir_name).mkdir()
            print(f"✅ Created {dir_name}/ directory")

    return True

def test_pdf_files():
    """Check for PDF files in data directory"""
    data_dir = Path('data')
    pdf_files = list(data_dir.glob('*.pdf'))

    if pdf_files:
        print(f"✅ Found {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            print(f"   - {pdf.name}")
        return True
    else:
        print("⚠️  No PDF files found in data/ directory")
        print("   Please add Dell knowledge PDFs to the data/ directory")
        print("   Or upload them through the Streamlit interface")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing AI Knowledge Base Assistant Setup\n")

    tests = [
        ("Dependencies", test_dependencies),
        ("Environment Variables", test_environment),
        ("Directories", test_directories),
        ("PDF Files", test_pdf_files)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"Testing {test_name}:")
        result = test_func()
        results.append(result)
        print()

    print("📊 Test Results:")
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\n🚀 Ready to run the application!")
        print("   API: python app.py api")
        print("   Frontend: python app.py frontend")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\n🔧 Please fix the failed tests before running the application")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)