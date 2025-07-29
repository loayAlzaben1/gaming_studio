#!/usr/bin/env bash
# EMERGENCY SIMPLE BUILD - Try to isolate issue

set -o errexit

echo "==> EMERGENCY BUILD STARTING..."
echo "Current directory: $(pwd)"

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Running Django checks..."
python manage.py check --deploy

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> EMERGENCY BUILD COMPLETE!"
echo "If this works, the issue is with our custom commands."
