from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from studio.views import home, games, team, contact
from studio.health_check import health_check
from studio.media_views import serve_media
from instant_auth import instant_login, instant_signup
from test_simple import simple_test
from url_test import url_test
from oauth_debug import oauth_debug

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('games/', games, name='games'),  
    path('team/', team, name='team'),
    path('contact/', contact, name='contact'),
    path('health/', health_check, name='health_check'),
    path('test/', simple_test, name='simple_test'),
    path('urls/', url_test, name='url_test'),
    path('oauth-debug/', oauth_debug, name='oauth_debug'),
    
    # CRITICAL: Include socialaccount URLs first for OAuth callbacks
    path('accounts/', include('allauth.socialaccount.urls')),
    
    # Override broken allauth login/signup with our working custom pages
    path('accounts/login/', instant_login, name='account_login'),
    path('accounts/signup/', instant_signup, name='account_signup'),
    
    # Additional custom paths
    path('signin/', instant_login, name='custom_login'),
    path('register/', instant_signup, name='custom_signup'),
    
    # Include remaining allauth account URLs (for other functionality)
    path('accounts/', include('allauth.account.urls')),
    
    # Keep studio URLs
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