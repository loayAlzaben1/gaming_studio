from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from studio.views import home, games, team, contact
from studio.health_check import health_check
from studio.media_views import serve_media

# NO AUTHENTICATION - COMPLETELY REMOVED!
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('games/', games, name='games'),
    path('team/', team, name='team'),
    path('contact/', contact, name='contact'),
    path('health/', health_check, name='health_check'),
    
    # Keep studio URLs (but remove any auth requirements)
    path('', include('studio.urls')),
]

# Serve media files
if settings.DEBUG:
    # Development - use Django's built-in static serve
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production - use custom media serving
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media, name='media'),
    ]

# Serve files from the project root (for Google verification HTML)
urlpatterns += static('/', document_root=settings.BASE_DIR)