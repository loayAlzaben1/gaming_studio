#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "==> Forcing complete database recreation..."

# Remove any existing database
if [ -f "db.sqlite3" ]; then
    echo "Removing existing database..."
    rm -f db.sqlite3
fi

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Checking Django configuration..."
python manage.py check

echo "==> Creating fresh migrations..."
# Remove migration cache
find . -path "*/migrations/__pycache__" -exec rm -rf {} +

# Create migrations for studio app specifically
python manage.py makemigrations studio --noinput
python manage.py makemigrations --noinput

echo "==> Applying migrations in order..."
# Apply core Django migrations first
python manage.py migrate contenttypes --noinput
python manage.py migrate auth --noinput
python manage.py migrate admin --noinput
python manage.py migrate sessions --noinput
python manage.py migrate sites --noinput

# Apply third-party migrations
python manage.py migrate account --noinput
python manage.py migrate socialaccount --noinput

# Apply studio migrations
echo "Applying studio migrations..."
python manage.py migrate studio --noinput

# Apply any remaining migrations
python manage.py migrate --noinput

echo "==> Checking if migration worked..."
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"studio_game\";')
if cursor.fetchone():
    print('✓ Migrations successful - studio_game table exists')
else:
    print('✗ Migrations failed - studio_game table missing')
    print('Running emergency database setup...')
    exit(42)  # Special exit code to trigger emergency setup
"

# If migrations failed, run emergency setup
if [ $? -eq 42 ]; then
    echo "==> Running emergency database setup..."
    python emergency_db_setup.py
    if [ $? -eq 0 ]; then
        echo "✓ Emergency database setup successful"
    else
        echo "✗ Emergency database setup failed"
        exit 1
    fi
fi

echo "==> Verifying database setup..."
python manage.py shell -c "
import os
print(f'Database file exists: {os.path.exists(\"db.sqlite3\")}')
if os.path.exists('db.sqlite3'):
    print(f'Database size: {os.path.getsize(\"db.sqlite3\")} bytes')

from django.db import connection
from studio.models import Game
try:
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
    tables = [table[0] for table in cursor.fetchall()]
    print(f'Total tables: {len(tables)}')
    
    studio_tables = [t for t in tables if t.startswith('studio_')]
    print(f'Studio tables: {studio_tables}')
    
    if 'studio_game' in tables:
        print('✓ studio_game table exists')
        game_count = Game.objects.count()
        print(f'✓ Games in database: {game_count}')
        print('✓ Database setup successful!')
    else:
        print('✗ studio_game table still missing!')
        print('All available tables:', ', '.join(tables))
        # Try to create the table manually
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', 'studio', '--verbosity=2'])
        exit(1)
except Exception as e:
    print(f'✗ Database verification failed: {e}')
    import traceback
    traceback.print_exc()
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
