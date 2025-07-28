"""
Auto-setup tables when Django starts
This should be imported in Django settings to ensure tables exist
"""
import os
import sys
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def ensure_tables_exist():
    """Ensure critical tables exist when Django starts"""
    try:
        with connection.cursor() as cursor:
            # Check if studio_game table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studio_game';")
            if cursor.fetchone():
                logger.info("studio_game table exists")
                return True
                
            logger.warning("studio_game table missing, creating it now...")
            
            # Create studio_game table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS studio_game (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                short_description VARCHAR(500) NOT NULL DEFAULT '',
                genre VARCHAR(100) NOT NULL DEFAULT 'Action',
                platform VARCHAR(100) NOT NULL DEFAULT 'PC',
                release_date DATE,
                status VARCHAR(20) NOT NULL DEFAULT 'development',
                cover_image VARCHAR(100),
                trailer_link VARCHAR(200),
                tags VARCHAR(500) DEFAULT '',
                age_rating VARCHAR(10) NOT NULL DEFAULT 'E',
                min_players INTEGER DEFAULT 1,
                max_players INTEGER DEFAULT 1,
                estimated_playtime INTEGER DEFAULT 60,
                is_featured BOOLEAN NOT NULL DEFAULT 0,
                featured_order INTEGER,
                average_rating DECIMAL NOT NULL DEFAULT 0.0,
                total_reviews INTEGER NOT NULL DEFAULT 0,
                play_count INTEGER NOT NULL DEFAULT 0,
                wishlist_count INTEGER NOT NULL DEFAULT 0,
                download_count INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            logger.info("studio_game table created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error ensuring tables exist: {e}")
        return False

# Run when this module is imported - always run in production
if 'wsgi' in sys.argv or 'gunicorn' in str(sys.argv) or os.environ.get('DJANGO_SETTINGS_MODULE'):
    print("Running auto-setup for production environment...")
    ensure_tables_exist()
elif 'runserver' in sys.argv or os.environ.get('RUN_MAIN'):
    print("Running auto-setup for development environment...")
    ensure_tables_exist()
else:
    print("Auto-setup conditions not met, forcing execution anyway...")
    ensure_tables_exist()
