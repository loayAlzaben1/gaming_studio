#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Checking Django configuration..."
python manage.py check

echo "==> Running database migrations..."
echo "Checking for existing database..."
if [ -f "db.sqlite3" ]; then
    echo "Database exists, checking tables..."
    python manage.py shell -c "
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"studio_game\";')
    result = cursor.fetchone()
    if result:
        print('studio_game table exists')
    else:
        print('studio_game table missing - will recreate database')
        import os
        os.remove('db.sqlite3')
except Exception as e:
    print(f'Database check failed: {e}')
    import os
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
"
fi

echo "Making migrations..."
python manage.py makemigrations --noinput
echo "Applying migrations..."
python manage.py migrate --noinput
echo "Migrations completed successfully!"

echo "==> Verifying database setup..."
python manage.py shell -c "
from django.db import connection
from studio.models import Game
cursor = connection.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
tables = [table[0] for table in cursor.fetchall()]
print(f'Total tables: {len(tables)}')
if 'studio_game' in tables:
    print('✓ studio_game table exists')
    game_count = Game.objects.count()
    print(f'✓ Games in database: {game_count}')
else:
    print('✗ studio_game table missing!')
    exit(1)
"

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
