#!/usr/bin/env python3
"""
Windows-compatible production server startup script
Uses waitress instead of gunicorn for Windows compatibility
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error in {description}: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def start_production_server():
    """Start production server with waitress"""
    print("Starting Gaming Studio Production Server (Windows-compatible)...")
    
    # Run deployment first
    print("Running deployment script...")
    if not run_command("python deploy.py", "Deployment"):
        print("Deployment failed, but continuing...")
    
    # Start waitress server
    print("\nStarting production server with Waitress...")
    print("Server will be available at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Use waitress for Windows compatibility
        subprocess.run([
            "python", "-m", "waitress", 
            "--host", "127.0.0.1", 
            "--port", "8000",
            "--threads", "4", 
            "gaming_studio.wsgi:application"
        ], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Server error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_production_server()
