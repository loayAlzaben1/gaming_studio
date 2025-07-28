#!/usr/bin/env python
"""
Test script to verify emergency database setup works locally
"""
import os
import sqlite3
import shutil

# Backup current database if it exists
if os.path.exists('db.sqlite3'):
    shutil.copy('db.sqlite3', 'db.sqlite3.backup')
    print("Backed up existing database")

# Remove current database to simulate fresh deployment
if os.path.exists('db.sqlite3'):
    os.remove('db.sqlite3')
    print("Removed existing database")

# Run emergency setup
print("Testing emergency database setup...")
import subprocess
result = subprocess.run(['python', 'emergency_db_setup.py'], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
print(f"Return code: {result.returncode}")

# Check if tables were created
if os.path.exists('db.sqlite3'):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables created: {tables}")
    
    if 'studio_game' in tables:
        print("✓ SUCCESS: studio_game table created!")
    else:
        print("✗ FAILED: studio_game table not found")
    
    conn.close()
else:
    print("✗ FAILED: No database file created")

# Restore backup if it exists
if os.path.exists('db.sqlite3.backup'):
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
    shutil.move('db.sqlite3.backup', 'db.sqlite3')
    print("Restored original database")
