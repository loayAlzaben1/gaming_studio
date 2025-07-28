"""
Auto-setup tables when Django starts
This ensures critical database tables exist in production
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
            # Check critical tables for full functionality
            critical_tables = {
                'studio_game': 'Studio app tables',
                'auth_user': 'Django auth tables', 
                'account_emailaddress': 'Django-allauth tables',
                'socialaccount_socialapp': 'Social auth tables',
                'django_site': 'Sites framework'
            }
            
            missing_tables = []
            existing_tables = []
            
            for table, description in critical_tables.items():
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
                if cursor.fetchone():
                    existing_tables.append(table)
                else:
                    missing_tables.append(f"{table} ({description})")
            
            if not missing_tables:
                logger.info(f"All critical tables exist: {existing_tables}")
                return True
                
            logger.info(f"Missing tables: {missing_tables}")
            logger.info("Running complete database migrations...")
            
            # Try to run all migrations
            from django.core.management import execute_from_command_line
            
            old_argv = sys.argv
            try:
                # Run migrations for all apps
                sys.argv = ['manage.py', 'migrate']
                execute_from_command_line(sys.argv)
                
                # Specifically ensure sites framework is set up
                sys.argv = ['manage.py', 'migrate', 'sites']
                execute_from_command_line(sys.argv)
                
                logger.info("All database migrations completed successfully")
                return True
            except Exception as migration_error:
                logger.warning(f"Some migrations failed: {migration_error}")
                
                # Manual fallback only for studio_game table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studio_game';")
                if not cursor.fetchone():
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
                    logger.info("Created studio_game table manually")
                
                logger.info("Partial setup completed - some features may not work until full migrations succeed")
                return True
            finally:
                sys.argv = old_argv
            
    except Exception as e:
        logger.error(f"Error ensuring tables exist: {e}")
        return False

# Run when this module is imported in production
if os.environ.get('DJANGO_SETTINGS_MODULE'):
    ensure_tables_exist()
