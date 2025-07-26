#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Checking Django configuration..."
python manage.py check

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Created superuser: admin')
else:
    print('Superuser already exists')
"

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Setting up Google OAuth for production..."
python manage.py update_google_oauth --production

echo "==> Setting up achievements..."
python manage.py setup_achievements || echo "Achievements setup failed, continuing..."

echo "==> Setting up user profiles..."
python manage.py setup_user_profiles || echo "User profiles setup failed, continuing..."

echo "==> Setting up Google OAuth for production..."
python manage.py setup_google_oauth_production || echo "Google OAuth setup failed, continuing..."

echo "==> Build completed successfully!"
