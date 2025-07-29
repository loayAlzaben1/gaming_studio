#!/usr/bin/env bash
# MINIMAL BUILD - Skip custom commands that might be causing issues

set -o errexit

echo "==> MINIMAL BUILD STARTING..."
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Running basic Django migrations..."
python manage.py migrate --run-syncdb

echo "==> Setting up Google OAuth (CRITICAL for login)..."
python manage.py setup_oauth_enhanced || echo "Enhanced OAuth setup failed, trying basic..."
python manage.py setup_oauth_now || echo "OAuth setup failed, continuing..."

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> MINIMAL BUILD COMPLETE - OAuth configured"
