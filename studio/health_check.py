# Health check view for debugging production issues
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint for debugging"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "OK"
        
        # Check if critical tables exist
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studio_game';")
            game_table_exists = bool(cursor.fetchone())
            
        return JsonResponse({
            'status': 'healthy',
            'database': db_status,
            'game_table_exists': game_table_exists,
            'timestamp': str(timezone.now()) if 'timezone' in globals() else 'N/A'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': 'N/A'
        }, status=500)
