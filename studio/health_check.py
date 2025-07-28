# Health check view for debugging production issues
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Comprehensive health check endpoint for debugging"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "OK"
        
        # Get database info
        db_path = settings.DATABASES['default']['NAME']
        db_exists = os.path.exists(db_path)
        db_size = os.path.getsize(db_path) if db_exists else 0
        
        # Get all tables
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            all_tables = [row[0] for row in cursor.fetchall()]
            
            # Check if studio_game table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studio_game';")
            game_table_exists = bool(cursor.fetchone())
            
            # If studio_game doesn't exist, try to create it now
            if not game_table_exists:
                try:
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS studio_game (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(200) NOT NULL DEFAULT 'Test Game',
                        description TEXT NOT NULL DEFAULT 'Test Description',
                        short_description VARCHAR(500) NOT NULL DEFAULT 'Short desc',
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
                    
                    # Verify creation
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studio_game';")
                    game_table_exists = bool(cursor.fetchone())
                    table_creation_result = "SUCCESS" if game_table_exists else "FAILED"
                except Exception as create_error:
                    table_creation_result = f"ERROR: {str(create_error)}"
            else:
                table_creation_result = "TABLE_ALREADY_EXISTS"
            
        return JsonResponse({
            'status': 'healthy',
            'database': db_status,
            'db_path': db_path,
            'db_exists': db_exists,
            'db_size_bytes': db_size,
            'total_tables': len(all_tables),
            'all_tables': all_tables,
            'game_table_exists': game_table_exists,
            'table_creation_attempt': table_creation_result,
            'environment': os.environ.get('DJANGO_SETTINGS_MODULE', 'unknown'),
            'timestamp': 'N/A'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': 'N/A'
        }, status=500)
