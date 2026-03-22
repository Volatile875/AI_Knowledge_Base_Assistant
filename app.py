#!/usr/bin/env python3
"""
AI Knowledge Base Assistant - Main Application Runner
"""
 
import subprocess
import sys
import os
from pathlib import Path
 
def run_api():
    """Run the FastAPI server which now serves the static frontend"""
    print("Starting AI Knowledge Base Assistant on http://localhost:8000")
    os.chdir(Path(__file__).parent)
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "api:app",
        "--host", "0.0.0.0",
        "--port", "8000"
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
        elif command == "install":
            install_dependencies()
        else:
            print("Usage: python app.py [api|install]")
    else:
        # Default behavior: run the API server
        run_api()
