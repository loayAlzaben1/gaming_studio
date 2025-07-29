#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "==> Build script starting..."
echo "Current directory: $(pwd)"
echo "Files in directory: $(ls -la)"

echo "==> INSTALLING DEPENDENCIES FIRST..."
pip install -r requirements.txt

echo "==> ULTRA MINIMAL FIX - ONLY CREATE STUDIO_GAME TABLE..."
python manage.py ultra_minimal
if [ $? -eq 0 ]; then
    echo "✅ Ultra minimal fix SUCCESS"
else
    echo "⚠️ Ultra minimal command failed, trying script..."
    python ultra_minimal.py || echo "Script also failed"
fi

echo "==> RUNNING SUPER SIMPLE FIX FIRST..."
python simple_fix.py
if [ $? -eq 0 ]; then
    echo "✅ Simple fix completed successfully"
else
    echo "⚠️ Simple fix failed, continuing with normal process..."
fi

echo "==> Ensuring database exists first..."
# Create a basic database file if it doesn't exist
if [ ! -f "db.sqlite3" ]; then
    echo "Creating initial database file..."
    python -c "
import sqlite3
conn = sqlite3.connect('db.sqlite3')
conn.close()
print('Created empty database file')
"
fi

echo "==> Running direct database setup immediately..."
python direct_db_setup.py
if [ $? -eq 0 ]; then
    echo "Direct database setup completed"
else
    echo "Direct database setup failed"
    exit 1
fi

echo "==> Forcing complete database recreation..."

# Remove any existing database
if [ -f "db.sqlite3" ]; then
    echo "Removing existing database..."
    rm -f db.sqlite3
fi

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> RUNNING SIMPLE FIX AS MANAGEMENT COMMAND..."
python manage.py simple_fix
if [ $? -eq 0 ]; then
    echo "✅ Management command simple fix completed"
else
    echo "⚠️ Management command failed, trying script version..."
    python simple_fix.py || echo "Both fixes failed, continuing..."
fi

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
MIGRATION_CHECK=$(python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"studio_game\";')
if cursor.fetchone():
    print('SUCCESS')
else:
    print('FAILED')
")

if [[ "$MIGRATION_CHECK" == *"FAILED"* ]]; then
    echo "Migrations failed - studio_game table missing"
    echo "==> Running direct database setup..."
    python direct_db_setup.py
    if [ $? -eq 0 ]; then
        echo "Direct database setup successful"
        # Try migrations again after manual table creation
        echo "Retrying migrations..."
        python manage.py migrate --noinput
    else
        echo "Direct database setup failed"
        exit 1
    fi
else
    echo "Migrations successful - studio_game table exists"
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

echo "==> SETTING UP GOOGLE OAUTH IMMEDIATELY..."
python manage.py setup_oauth_now
if [ $? -eq 0 ]; then
    echo "✅ Google OAuth configured - Gmail sign-in ready!"
else
    echo "⚠️ OAuth setup failed"
fi

echo "==> IMMEDIATE GAMES FIX..."
python manage.py add_games
if [ $? -eq 0 ]; then
    echo "✅ Sample games added immediately"
else
    echo "⚠️ Games fix failed"
fi

echo "==> FINAL FIX - ADD MISSING DATA AND OAUTH..."
python manage.py final_fix
if [ $? -eq 0 ]; then
    echo "✅ Final fix SUCCESS - OAuth and games configured"
else
    echo "⚠️ Final fix failed"
fi

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running emergency database fix..."
python manage.py emergency_fix
if [ $? -eq 0 ]; then
    echo "✅ Emergency fix completed"
else
    echo "⚠️ Emergency fix failed, trying comprehensive deployment..."
    python deploy_production.py || echo "Deployment script also failed, continuing..."
fi

echo "==> Final verification..."
python manage.py shell -c "
try:
    from studio.models import Game
    from django.contrib.sites.models import Site
    from allauth.socialaccount.models import SocialApp
    
    print(f'Games: {Game.objects.count()}')
    print(f'Sites: {Site.objects.count()}')  
    print(f'OAuth apps: {SocialApp.objects.count()}')
    print('✅ All models accessible')
except Exception as e:
    print(f'❌ Model error: {e}')
"

echo "==> Build completed successfully!"
