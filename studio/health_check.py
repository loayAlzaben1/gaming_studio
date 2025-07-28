# Health check view for production monitoring
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint for monitoring"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "OK"
        
        # Check if critical tables exist
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studio_game';")
            game_table_exists = bool(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='account_emailaddress';")
            allauth_table_exists = bool(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
            auth_user_exists = bool(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='socialaccount_socialapp';")
            oauth_table_exists = bool(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_site';")
            site_table_exists = bool(cursor.fetchone())
            
            # Count total tables
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
            total_tables = cursor.fetchone()[0]
        
        # Check if we have sample data
        try:
            from studio.models import Game
            game_count = Game.objects.count()
        except:
            game_count = 0
        
        # Check OAuth configuration
        try:
            from allauth.socialaccount.models import SocialApp
            oauth_configured = SocialApp.objects.filter(provider='google').exists()
        except:
            oauth_configured = False
            
        return JsonResponse({
            'status': 'healthy',
            'database': db_status,
            'tables': {
                'studio_game': game_table_exists,
                'account_emailaddress': allauth_table_exists,
                'auth_user': auth_user_exists,
                'socialaccount_socialapp': oauth_table_exists,
                'django_site': site_table_exists,
                'total_count': total_tables
            },
            'data': {
                'game_count': game_count,
                'oauth_configured': oauth_configured
            },
            'authentication_ready': game_table_exists and allauth_table_exists and auth_user_exists and oauth_table_exists,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
