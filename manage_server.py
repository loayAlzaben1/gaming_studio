#!/usr/bin/env python3
"""
Gaming Studio Server Management Script
Provides easy commands for managing the Django server in different environments
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run_command(command, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return False

def start_dev():
    """Start development server"""
    print("Starting development server...")
    os.chdir(BASE_DIR)
    
    if sys.platform.startswith('win'):
        return run_command("start_dev.bat")
    else:
        return run_command("chmod +x start_dev.sh && ./start_dev.sh")

def start_prod():
    """Start production server"""
    print("Starting production server...")
    os.chdir(BASE_DIR)
    
    # Run deployment first
    run_command("python deploy.py")
    
    if sys.platform.startswith('win'):
        return run_command("gunicorn gaming_studio.wsgi -c gunicorn.conf.py")
    else:
        return run_command("chmod +x start_prod.sh && ./start_prod.sh")

def docker_build():
    """Build Docker image"""
    print("Building Docker image...")
    return run_command("docker build -t gaming-studio .")

def docker_run():
    """Run with Docker Compose"""
    print("Starting with Docker Compose...")
    return run_command("docker-compose up -d")

def docker_stop():
    """Stop Docker containers"""
    print("Stopping Docker containers...")
    return run_command("docker-compose down")

def setup():
    """Setup the project for first time"""
    print("Setting up Gaming Studio project...")
    
    # Create .env file if it doesn't exist
    env_file = BASE_DIR / '.env'
    if not env_file.exists():
        env_content = """# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
DEPLOY_ENV=local

# Database Settings (for PythonAnywhere)
DB_NAME=gaming_studio_db
DB_USER=your-username
DB_PASSWORD=your-password
DB_HOST=your-host
DB_PORT=5432
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("Created .env file - please update with your settings")
    
    # Install requirements
    print("Installing requirements...")
    run_command("pip install -r requirements.txt")
    
    # Run initial setup
    run_command("python deploy.py")
    
    print("Setup completed!")

def main():
    parser = argparse.ArgumentParser(description='Gaming Studio Server Management')
    parser.add_argument('command', choices=[
        'dev', 'prod', 'docker-build', 'docker-run', 'docker-stop', 'setup'
    ], help='Command to execute')
    
    args = parser.parse_args()
    
    commands = {
        'dev': start_dev,
        'prod': start_prod,
        'docker-build': docker_build,
        'docker-run': docker_run,
        'docker-stop': docker_stop,
        'setup': setup,
    }
    
    command_func = commands.get(args.command)
    if command_func:
        success = command_func()
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
