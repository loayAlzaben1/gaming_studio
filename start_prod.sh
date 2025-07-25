#!/bin/bash
# Production server startup script for Linux/Unix systems
# This script sets up the production environment and starts the server with Gunicorn

echo "Starting Gaming Studio Production Server..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing/updating requirements..."
pip install -r requirements.txt

# Run deployment script
echo "Running deployment script..."
python deploy.py

echo
echo "Starting production server with Gunicorn..."
echo "Server will be available on port 8000"
echo "Press Ctrl+C to stop the server"
echo

# Start the production server
gunicorn gaming_studio.wsgi -c gunicorn.conf.py
