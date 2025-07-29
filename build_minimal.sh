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

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> MINIMAL BUILD COMPLETE - Custom setup skipped for now"
