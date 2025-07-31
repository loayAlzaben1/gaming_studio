#!/bin/bash
# Production Database Setup for Render
# Fixes: no such table: studio_game after authentication removal

echo "🚀 PRODUCTION DATABASE SETUP"
echo "=============================="

echo "📊 Running database migrations..."
python manage.py makemigrations
python manage.py migrate --run-syncdb

echo "✅ Creating superuser (if needed)..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')
    print('✅ Superuser created')
else:
    print('✅ Superuser already exists')
"

echo "📋 Listing database tables..."
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table';\")
tables = cursor.fetchall()
print(f'📊 Found {len(tables)} tables')
studio_tables = [t[0] for t in tables if 'studio_' in t[0]]
print(f'🎮 Studio tables: {len(studio_tables)}')
if 'studio_game' in [t[0] for t in tables]:
    print('✅ studio_game table exists!')
else:
    print('❌ studio_game table missing!')
"

echo "🎯 Production database setup complete!"
