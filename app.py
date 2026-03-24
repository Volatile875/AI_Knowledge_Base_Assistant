#!/usr/bin/env python3
"""AI Knowledge Base Assistant - Main Application Runner."""

import os
import socket
import subprocess
import sys
from pathlib import Path


DEFAULT_HOST = os.getenv("APP_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("APP_PORT", "8000"))


def is_port_available(host: str, port: int) -> bool:
    """Return True when the given host/port can be bound locally."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def find_available_port(host: str, preferred_port: int, attempts: int = 10) -> int:
    """Pick the first available port starting from the preferred one."""
    for port in range(preferred_port, preferred_port + attempts):
        if is_port_available(host, port):
            return port
    raise RuntimeError(
        f"Could not find an available port between {preferred_port} and {preferred_port + attempts - 1}."
    )


def run_api():
    """Run the FastAPI server which also serves the static frontend."""
    os.chdir(Path(__file__).parent)
    host = DEFAULT_HOST
    port = find_available_port(host, DEFAULT_PORT)

    if port != DEFAULT_PORT:
        print(
            f"Port {DEFAULT_PORT} is busy. Starting AI Knowledge Base Assistant on "
            f"http://{host}:{port} instead."
        )
    else:
        print(f"Starting AI Knowledge Base Assistant on http://{host}:{port}")

    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "api:app",
        "--host", host,
        "--port", str(port)
    ])


def install_dependencies():
    """Install required dependencies."""
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
