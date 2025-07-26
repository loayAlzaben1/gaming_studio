#!/usr/bin/env bash
# Build script for Render deployment

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Running database migrations..."
python manage.py migrate

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Setting up achievements and user profiles..."
python manage.py setup_achievements
python manage.py setup_user_profiles

echo "==> Build completed successfully!"
