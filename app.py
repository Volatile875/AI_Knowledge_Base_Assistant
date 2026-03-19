#!/usr/bin/env python3
"""
AI Knowledge Base Assistant - Main Application Runner
"""
 
import subprocess
import sys
import os
from pathlib import Path
 
def run_api():
    """Run the FastAPI server"""
    print("Starting FastAPI server...")
    os.chdir(Path(__file__).parent)
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "api:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])
 
def run_frontend():
    """Run the Streamlit frontend"""
    print("Starting Streamlit frontend...")
    os.chdir(Path(__file__).parent)
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "frontend.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])
 
def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
 
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "api":
            run_api()
        elif command == "frontend":
            run_frontend()
        elif command == "install":
            install_dependencies()
        else:
            print("Usage: python app.py [api|frontend|install]")
    else:
        print("AI Knowledge Base Assistant")
        print("Usage:")
        print("  python app.py install    # Install dependencies")
        print("  python app.py api        # Run FastAPI server")
        print("  python app.py frontend   # Run Streamlit frontend")
        print("\nOr run both servers in separate terminals:")
        print("  Terminal 1: python app.py api")
        print("  Terminal 2: python app.py frontend")
